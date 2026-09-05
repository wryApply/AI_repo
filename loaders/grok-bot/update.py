#!/usr/bin/env python3
"""Grok Bot skills updater: pull wryApply/AI_repo@stable, then install into native workflows/."""
from __future__ import annotations

import json
import os
import shutil
import sys
import tempfile
import urllib.request
import zipfile
from datetime import datetime, timezone
from pathlib import Path

REPO = os.environ.get("AGENT_SKILLS_REPO", "wryApply/AI_repo")
BRANCH = os.environ.get("AGENT_SKILLS_BRANCH", "stable")
ROOT = Path(os.environ.get("AGENT_SKILLS_ROOT", Path.home() / "agent-skills")).expanduser()
CURRENT = ROOT / "current"
STAGING = ROOT / "staging"
STATE = ROOT / "state.json"
WORKFLOWS = Path(
    os.environ.get(
        "AGENT_SKILLS_WORKFLOWS",
        Path.home() / "agent-data" / "workflows",
    )
).expanduser()
ZIP_URL = f"https://codeload.github.com/{REPO}/zip/refs/heads/{BRANCH}"

# Never overwrite these local-only skill folders even if names collide.
PROTECTED = {
    "update-agent-skills",
    "update-agent-skills-2",
    "understand-a-concept",
}


def die(msg: str, code: int = 1) -> None:
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def download_zip(dest: Path) -> None:
    req = urllib.request.Request(ZIP_URL, headers={"User-Agent": "grok-bot-skills-loader"})
    with urllib.request.urlopen(req, timeout=120) as resp, open(dest, "wb") as f:
        shutil.copyfileobj(resp, f)


def extract_zip(zip_path: Path, staging: Path) -> Path:
    if staging.exists():
        shutil.rmtree(staging)
    staging.mkdir(parents=True)
    with zipfile.ZipFile(zip_path) as zf:
        zf.extractall(staging)
    kids = [p for p in staging.iterdir() if p.is_dir()]
    if len(kids) != 1:
        die(f"unexpected zip layout under {staging}: {kids}")
    return kids[0]


def validate(tree: Path) -> dict:
    index_path = tree / "generated" / "index.json"
    if not index_path.is_file():
        die(f"missing {index_path}")
    index = json.loads(index_path.read_text(encoding="utf-8"))
    skills = index.get("skills") or []
    if not isinstance(skills, list):
        die("index.skills must be a list")
    for entry in skills:
        name = entry.get("name")
        root = entry.get("root") or (f"skills/{name}" if name else None)
        if not name or not root:
            die(f"bad skill entry: {entry}")
        skill_md = tree / root / "SKILL.md"
        if not skill_md.is_file():
            die(f"missing SKILL.md for {name}: {skill_md}")
    return index


def atomic_promote(extracted: Path) -> None:
    ROOT.mkdir(parents=True, exist_ok=True)
    if STAGING.exists():
        shutil.rmtree(STAGING)
    shutil.copytree(extracted, STAGING)
    backup = ROOT / "current.bak"
    if backup.exists():
        shutil.rmtree(backup)
    if CURRENT.exists():
        CURRENT.rename(backup)
    try:
        STAGING.rename(CURRENT)
    except Exception:
        if backup.exists() and not CURRENT.exists():
            backup.rename(CURRENT)
        raise
    if backup.exists():
        shutil.rmtree(backup)
    if STAGING.exists():
        shutil.rmtree(STAGING)


def install_native(index: dict) -> list[str]:
    """Copy each catalog skill into shared workflows/. Only touch skills listed in the index."""
    WORKFLOWS.mkdir(parents=True, exist_ok=True)
    installed: list[str] = []
    for entry in index.get("skills") or []:
        name = entry.get("name")
        if not name:
            continue
        if name in PROTECTED:
            print(f"SKIP native install (protected): {name}")
            continue
        root = entry.get("root") or f"skills/{name}"
        src = CURRENT / root
        if not (src / "SKILL.md").is_file():
            die(f"cannot install {name}: missing {src / 'SKILL.md'}")
        dest = WORKFLOWS / name
        if dest.exists():
            shutil.rmtree(dest)
        shutil.copytree(src, dest)
        installed.append(name)
        print(f"INSTALLED native: {dest}")
    return installed


def write_state(index: dict, commit: str | None, installed: list[str]) -> None:
    skills = index.get("skills") or []
    state = {
        "repo": REPO,
        "branch": BRANCH,
        "source_commit": commit or index.get("source_commit"),
        "skill_count": len(skills),
        "skills": [s.get("name") for s in skills if s.get("name")],
        "native_installed": installed,
        "native_workflows": str(WORKFLOWS),
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }
    STATE.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(state, ensure_ascii=False, indent=2))


def main() -> None:
    ROOT.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="agent-skills-") as tmp:
        tmp_path = Path(tmp)
        zip_path = tmp_path / "stable.zip"
        try:
            print(f"Fetching {ZIP_URL} ...")
            download_zip(zip_path)
            extracted = extract_zip(zip_path, tmp_path / "unpack")
            index = validate(extracted)
            commit = index.get("source_commit")
            try:
                api = f"https://api.github.com/repos/{REPO}/commits/{BRANCH}"
                req = urllib.request.Request(
                    api,
                    headers={
                        "User-Agent": "grok-bot-skills-loader",
                        "Accept": "application/vnd.github+json",
                    },
                )
                with urllib.request.urlopen(req, timeout=60) as resp:
                    commit = json.loads(resp.read().decode()).get("sha") or commit
            except Exception as e:
                print(f"WARN: could not resolve tip SHA via API ({e}); using index source_commit")
            atomic_promote(extracted)
            installed = install_native(index)
            write_state(index, commit, installed)
            print(f"OK: current={CURRENT}")
            print(f"OK: native_workflows={WORKFLOWS} installed={installed}")
        except SystemExit:
            if STAGING.exists():
                shutil.rmtree(STAGING, ignore_errors=True)
            raise
        except Exception as e:
            if STAGING.exists():
                shutil.rmtree(STAGING, ignore_errors=True)
            die(str(e))


if __name__ == "__main__":
    main()

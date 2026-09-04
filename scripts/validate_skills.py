#!/usr/bin/env python3
"""Validate skills/*/SKILL.md front matter and simple relative references."""

from __future__ import annotations

import re
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    yaml = None  # type: ignore

ROOT = Path(__file__).resolve().parents[1]
SKILLS_DIR = ROOT / "skills"

REQUIRED_KEYS = ("name", "description", "priority", "platforms", "capabilities")
PLATFORM_KEYS = ("codex", "chatgpt", "grok", "grok_bot")
CAPABILITY_KEYS = ("scripts", "files")
PLATFORM_ENUM = {"full", "partial", "unsupported"}
CAPABILITY_ENUM = {"required", "optional", "none"}

FRONTMATTER_RE = re.compile(r"\A---\s*\n(.*?)\n---\s*\n?", re.DOTALL)
# Simple relative markdown/file links: ](./foo) or ](foo.md) not http
REL_LINK_RE = re.compile(r"\[[^\]]*\]\((?!https?://|#)([^)]+)\)")


def parse_frontmatter(text: str) -> tuple[dict | None, str | None]:
    m = FRONTMATTER_RE.match(text)
    if not m:
        return None, "missing YAML front matter delimited by ---"
    raw = m.group(1)
    if yaml is not None:
        try:
            data = yaml.safe_load(raw)
        except Exception as e:  # noqa: BLE001
            return None, f"YAML parse error: {e}"
    else:
        data = _minimal_yaml(raw)
        if data is None:
            return None, "YAML parse failed (install PyYAML for full support)"
    if not isinstance(data, dict):
        return None, "front matter must be a mapping"
    return data, None


def _minimal_yaml(raw: str) -> dict | None:
    """Tiny subset parser if PyYAML is unavailable."""
    data: dict = {}
    lines = raw.splitlines()
    i = 0
    current_map: dict | None = None
    current_key: str | None = None
    folded: list[str] | None = None

    def flush_folded() -> None:
        nonlocal folded, current_key, data
        if folded is not None and current_key is not None:
            data[current_key] = " ".join(s.strip() for s in folded if s.strip())
            folded = None
            current_key = None

    while i < len(lines):
        line = lines[i]
        if not line.strip() or line.strip().startswith("#"):
            i += 1
            continue
        # nested map entry "  key: value"
        if current_map is not None and re.match(r"^  \w", line):
            mm = re.match(r"^  ([A-Za-z0-9_]+):\s*(.*)$", line)
            if not mm:
                return None
            current_map[mm.group(1)] = mm.group(2).strip().strip("\"'")
            i += 1
            continue
        if current_map is not None and not line.startswith(" "):
            current_map = None
        flush_folded()
        m = re.match(r"^([A-Za-z0-9_]+):\s*(.*)$", line)
        if not m:
            return None
        key, val = m.group(1), m.group(2)
        if val in (">", ">-", "|", "|-"):
            current_key = key
            folded = []
            i += 1
            while i < len(lines) and (lines[i].startswith("  ") or lines[i].strip() == ""):
                if lines[i].strip():
                    folded.append(lines[i])
                i += 1
            flush_folded()
            continue
        if val == "":
            nested: dict = {}
            data[key] = nested
            current_map = nested
            i += 1
            continue
        # scalar
        if val.startswith(("'", '"')):
            val = val.strip("\"'")
        elif re.fullmatch(r"-?\d+", val):
            val = int(val)
        data[key] = val
        i += 1
    flush_folded()
    return data


def check_skill(skill_dir: Path, errors: list[str], names: dict[str, Path]) -> None:
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.is_file():
        errors.append(f"{skill_dir.relative_to(ROOT)}: missing SKILL.md")
        return
    text = skill_md.read_text(encoding="utf-8")
    meta, err = parse_frontmatter(text)
    rel = skill_md.relative_to(ROOT)
    if err:
        errors.append(f"{rel}: {err}")
        return
    assert meta is not None
    for key in REQUIRED_KEYS:
        if key not in meta:
            errors.append(f"{rel}: missing required key '{key}'")
    name = meta.get("name")
    if not isinstance(name, str) or not name.strip():
        errors.append(f"{rel}: 'name' must be a non-empty string")
    else:
        if name in names:
            errors.append(f"{rel}: duplicate name '{name}' (also {names[name]})")
        else:
            names[name] = rel
        if name != skill_dir.name:
            errors.append(f"{rel}: name '{name}' must match directory '{skill_dir.name}'")

    desc = meta.get("description")
    if not isinstance(desc, str) or not desc.strip():
        errors.append(f"{rel}: 'description' must be a non-empty string")

    pri = meta.get("priority")
    if not isinstance(pri, int) or isinstance(pri, bool):
        errors.append(f"{rel}: 'priority' must be an integer")

    platforms = meta.get("platforms")
    if not isinstance(platforms, dict):
        errors.append(f"{rel}: 'platforms' must be a mapping")
    else:
        for pk in PLATFORM_KEYS:
            if pk not in platforms:
                errors.append(f"{rel}: platforms missing '{pk}'")
            else:
                val = platforms[pk]
                if val not in PLATFORM_ENUM:
                    errors.append(
                        f"{rel}: platforms.{pk}={val!r} not in {sorted(PLATFORM_ENUM)}"
                    )

    caps = meta.get("capabilities")
    if not isinstance(caps, dict):
        errors.append(f"{rel}: 'capabilities' must be a mapping")
    else:
        for ck in CAPABILITY_KEYS:
            if ck not in caps:
                errors.append(f"{rel}: capabilities missing '{ck}'")
            else:
                val = caps[ck]
                if val not in CAPABILITY_ENUM:
                    errors.append(
                        f"{rel}: capabilities.{ck}={val!r} not in {sorted(CAPABILITY_ENUM)}"
                    )

    # Simple relative file existence checks
    body = FRONTMATTER_RE.sub("", text, count=1)
    for m in REL_LINK_RE.finditer(body):
        target = m.group(1).strip()
        if not target or target.startswith(("mailto:", "data:")):
            continue
        # strip anchors
        path_part = target.split("#", 1)[0]
        if not path_part:
            continue
        candidate = (skill_dir / path_part).resolve()
        try:
            candidate.relative_to(skill_dir.resolve())
        except ValueError:
            errors.append(f"{rel}: link escapes skill dir: {target}")
            continue
        if not candidate.exists():
            errors.append(f"{rel}: referenced file missing: {path_part}")


def main() -> int:
    errors: list[str] = []
    names: dict[str, Path] = {}
    if not SKILLS_DIR.is_dir():
        print(f"ERROR: skills directory missing: {SKILLS_DIR}", file=sys.stderr)
        return 1
    skill_dirs = sorted(p for p in SKILLS_DIR.iterdir() if p.is_dir() and not p.name.startswith("."))
    if not skill_dirs:
        print("WARNING: no skill directories under skills/", file=sys.stderr)
    for d in skill_dirs:
        check_skill(d, errors, names)
    if errors:
        print(f"validate_skills: {len(errors)} error(s)", file=sys.stderr)
        for e in errors:
            print(f"  - {e}", file=sys.stderr)
        return 1
    print(f"validate_skills: OK ({len(skill_dirs)} skill(s))")
    return 0


if __name__ == "__main__":
    sys.exit(main())

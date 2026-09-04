#!/usr/bin/env python3
"""Generate generated/index.json from skills/*/SKILL.md. Never hand-edit the output."""

from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    yaml = None  # type: ignore

ROOT = Path(__file__).resolve().parents[1]
SKILLS_DIR = ROOT / "skills"
OUT = ROOT / "generated" / "index.json"
FRONTMATTER_RE = re.compile(r"\A---\s*\n(.*?)\n---\s*\n?", re.DOTALL)


def parse_frontmatter(text: str) -> dict:
    m = FRONTMATTER_RE.match(text)
    if not m:
        raise ValueError("missing front matter")
    raw = m.group(1)
    if yaml is not None:
        data = yaml.safe_load(raw)
    else:
        # reuse validator's approach via subprocess-free import
        from validate_skills import _minimal_yaml  # type: ignore

        data = _minimal_yaml(raw)
    if not isinstance(data, dict):
        raise ValueError("front matter not a mapping")
    return data


def main() -> int:
    skills = []
    for skill_dir in sorted(p for p in SKILLS_DIR.iterdir() if p.is_dir() and not p.name.startswith(".")):
        skill_md = skill_dir / "SKILL.md"
        if not skill_md.is_file():
            print(f"skip {skill_dir.name}: no SKILL.md", file=sys.stderr)
            continue
        meta = parse_frontmatter(skill_md.read_text(encoding="utf-8"))
        entry = {
            "name": meta["name"],
            "description": meta["description"].strip()
            if isinstance(meta.get("description"), str)
            else meta.get("description"),
            "priority": meta.get("priority"),
            "root": f"skills/{skill_dir.name}",
            "platforms": meta.get("platforms", {}),
            "capabilities": meta.get("capabilities", {}),
        }
        skills.append(entry)

    skills.sort(key=lambda s: (-(s.get("priority") or 0), s["name"]))

    index = {
        "schema_version": 1,
        "source_branch": os.environ.get("SOURCE_BRANCH", "main"),
        "source_commit": os.environ.get("SOURCE_COMMIT", "PLACEHOLDER"),
        "skills": skills,
    }

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(index, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"wrote {OUT.relative_to(ROOT)} ({len(skills)} skill(s))")
    return 0


if __name__ == "__main__":
    sys.exit(main())

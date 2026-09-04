# Skills catalog

This directory is the **open, platform-neutral** Skills catalog. There is one `skills/` tree for all loaders—do not fork per-platform copies.

## Current Skills

| Skill | Status |
|-------|--------|
| [`teach`](./teach/) | Present — stateful, goal-oriented teaching |

`teach` is the only Skill committed for now.

## Catalog is not locked

Proposed candidates discussed during planning (`grillme`, `loop`, `handoff`, and others) are **not** committed. The catalog stays open: add or remove Skills on `main` without changing the registry architecture.

## Layout

Each Skill is a directory with a required `SKILL.md` entry point (YAML front matter + Markdown body). Optional companions: `scripts/`, `references/`, `templates/`, `assets/`, format helpers, and platform adapter files under `agents/`.

See the root [README.md](../README.md) for front-matter schema, how to add a Skill, and the `main` → `stable` publish flow.

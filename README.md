# AI_repo — dynamic Skills registry

Public GitHub repository for cross-platform Agent Skills. **GitHub is the source of truth.** Cost target: **¥0** (no hosted service, no marketplace, no MCP in v0.1).

## Branches

| Branch | Role |
|--------|------|
| `main` | Development / integration |
| `stable` | Production registry that loaders read |

Flow: edit Skill on `main` → CI validates & builds index → PR/merge to `stable` → user says **更新 skills** in an Agent → that Agent loads the latest stable snapshot.

Agents update independently. During ordinary requests, a loader uses its local/session snapshot and does **not** hit GitHub.

## One `skills/` tree

All platforms share a single platform-neutral [`skills/`](./skills/) directory. Do not create `skills-codex/`, `skills-chatgpt/`, etc.—that causes version drift.

`generated/index.json` is **machine-generated**. Never hand-edit it; run `scripts/build_index.py` (or CI).

## Update command

Canonical trigger (user says this to an Agent):

- **更新 skills**

Aliases: `同步 skills`, `刷新 skills`, `reload skills`, `update skills`.

Loaders contact GitHub **only** on this explicit command. See [`loaders/common/PROTOCOL.md`](./loaders/common/PROTOCOL.md).

## Loaders

Thin platform adapters (install once; they do **not** self-update):

| Loader | Notes |
|--------|--------|
| [`loaders/codex/`](./loaders/codex/LOADER.md) | Local filesystem (`~/.agent-skills/{current,staging}/`) |
| [`loaders/grok-bot/`](./loaders/grok-bot/LOADER.md) | Persistent VM filesystem (same staging→current pattern) |
| [`loaders/chatgpt/`](./loaders/chatgpt/LOADER.md) | Session snapshot (read stable manifest + Skill Markdown) |
| [`loaders/grok/`](./loaders/grok/LOADER.md) | Session snapshot (same idea as ChatGPT) |

## Skill front matter

```yaml
---
name: example
description: >
  What this Skill does and when it should be selected.
priority: 50
platforms:
  codex: full
  chatgpt: full
  grok: partial
  grok_bot: full
capabilities:
  scripts: optional
  files: optional
---
```

- **platforms:** `full` | `partial` | `unsupported`
- **capabilities:** `required` | `optional` | `none`
- Higher `priority` wins automatic conflicts. No `depends_on` in MVP.

## CI

[`.github/workflows/skills-ci.yml`](./.github/workflows/skills-ci.yml) runs on pushes to `main` and PRs targeting `stable`:

1. `scripts/validate_skills.py`
2. `scripts/build_index.py`

Failures block merging to `stable`.

## How to add a Skill

1. Create `skills/<name>/SKILL.md` with valid front matter and body.
2. Add any format helpers / scripts / assets under that directory.
3. Push to `main`; CI validates and regenerates `generated/index.json`.
4. Open a PR from `main` to `stable` and merge when green.
5. Tell Agents **更新 skills** to pick up the new snapshot.

## Current Skills

See [`skills/README.md`](./skills/README.md). The catalog is **open**—not locked to a fixed list. Only `teach` is present for now; other candidates are not committed.

## Deferred (do not build in v0.1)

- Skill Marketplace
- MCP Server / MCP-based sync
- Hosted workers, webhooks, push updates
- Databases / OAuth / private-repo auth
- Semver, dependency graphs, differential updates
- Automatic loader self-updates
- Multi-device state sync / one-command-updates-all-Agents

## Rollback

Revert the bad commit on `stable` (new good commit), then run **更新 skills** on Agents.

# Codex loader

Thin adapter over [`../common/PROTOCOL.md`](../common/PROTOCOL.md).

## Runtime shape

Codex has a local filesystem. Recommended layout:

```text
~/.agent-skills/
  current/     # active snapshot (stable commit tree)
  staging/     # download + validate here
  state.json   # source_commit, updated_at, skill_count
```

## Update path (MVP)

On **更新 skills** (and aliases):

1. Download the public `stable` ZIP for `wryApply/AI_repo` (no credentials).
2. Extract into `staging/`.
3. Validate (`generated/index.json`, `skills/*/SKILL.md`).
4. Atomically swap `staging` → `current`; write `state.json` with the commit SHA.
5. On failure, delete `staging` and keep `current`.

Git clone/pull is optional; ZIP avoids working-tree and branch-state complexity.

## Ordinary requests

Read Skills only from `~/.agent-skills/current/`. Do not hit GitHub unless the user triggers an update.

## Notes

- Full filesystem: scripts and files capabilities can be honored when marked `optional`/`required`.
- This loader does not self-update.

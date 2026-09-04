# Grok Bot loader

Thin adapter over [`../common/PROTOCOL.md`](../common/PROTOCOL.md).

## Runtime shape

```text
~/agent-skills/
  update.py      # run this on 「更新 skills」
  current/       # active snapshot (skills/, generated/, …)
  staging/       # ephemeral; removed after promote
  state.json     # source_commit, skill_count, skills, updated_at
```

## Update path (MVP)

On **更新 skills** (aliases: 同步/刷新/reload/update skills):

```bash
python3 ~/agent-skills/update.py
```

The script:

1. Downloads the public `stable` ZIP of `wryApply/AI_repo`
2. Validates `generated/index.json` and each listed Skill's `SKILL.md`
3. Atomically promotes staging → `current` (keeps previous on failure)
4. Writes `state.json`

## Ordinary requests

Use `~/agent-skills/current/` only. Do not hit GitHub. Do not register synced Skills into Grok Bot's native skill library in MVP (native install is optional/manual).

## Notes

- Loaders do not self-update.
- Script source of truth in-repo: `loaders/grok-bot/update.py` (copy to `~/agent-skills/update.py` on a new box).

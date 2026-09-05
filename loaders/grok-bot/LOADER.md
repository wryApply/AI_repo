# Grok Bot loader

Thin adapter over [`../common/PROTOCOL.md`](../common/PROTOCOL.md).

## Triggers

Only on explicit user request: **更新 skills** (aliases: 同步/刷新/reload/update skills). No background pull.

## Runtime shape

```text
~/agent-skills/
  update.py
  current/
  staging/
  state.json
~/agent-data/workflows/<skill>/   # native shared library (post-update install)
```

## Update path

```bash
python3 ~/agent-skills/update.py
```

1. Fetch public `stable` ZIP of `wryApply/AI_repo`
2. Validate → atomic promote to `current`
3. Install each catalog skill into `~/agent-data/workflows/<name>/`
4. Leave unrelated local skills alone; skip protected names

## Ordinary requests

Use installed native skills / `~/agent-skills/current`. Do not contact GitHub until the next explicit update.

## Notes

- Loaders do not self-update.
- In-repo copy of the script: `loaders/grok-bot/update.py`

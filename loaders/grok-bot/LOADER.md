# Grok Bot loader

Thin adapter over [`../common/PROTOCOL.md`](../common/PROTOCOL.md).

## Runtime shape

Grok Bot has a persistent VM/filesystem/terminal—same pattern as Codex:

```text
~/agent-skills/
  current/
  staging/
  state.json
```

## Update path (MVP)

On **更新 skills**:

1. Fetch public `stable` ZIP (or raw `stable` tree) for `wryApply/AI_repo`.
2. Stage → validate → atomic promote to `current`.
3. Failure keeps the previous snapshot.

## Ordinary requests

Use `~/agent-skills/current/` only. Do not register synced Skills into Grok Bot’s native Skill system in MVP.

## Notes

- Filesystem capabilities available; do not self-update the loader.

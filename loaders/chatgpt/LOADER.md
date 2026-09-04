# ChatGPT loader

Thin adapter over [`../common/PROTOCOL.md`](../common/PROTOCOL.md).

## Runtime shape

Do **not** assume a local `~/.skills` directory or universal mobile MCP/App install. Persistence is the **current Agent/session snapshot**.

## Update path (MVP)

On **更新 skills**:

1. Read public `stable` `generated/index.json`.
2. Fetch listed `skills/*/SKILL.md` (and small companions as needed) via raw stable URLs.
3. Replace the session Skills snapshot atomically (staging buffer → current session pointer).
4. On failure, keep the previous session snapshot.

Large assets/scripts load on demand only if the platform can reach them; otherwise treat as context-only / skipped when capability is `optional`.

## Ordinary requests

Use the session snapshot only; no GitHub access.

## Notes

- Skill Markdown bodies stay unchanged if a better mobile adapter appears later.
- Loader does not self-update.

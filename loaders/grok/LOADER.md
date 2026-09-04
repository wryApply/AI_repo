# Grok loader

Thin adapter over [`../common/PROTOCOL.md`](../common/PROTOCOL.md).

## Runtime shape

Session-oriented, similar to ChatGPT: persist if the product allows; otherwise hold Skills in the **current session snapshot**.

## Update path (MVP)

On **更新 skills**:

1. Read public `stable/generated/index.json` (raw URL on branch `stable`).
2. Pull relevant `SKILL.md` files for this session.
3. Stage in session memory/buffer, validate minimally, then swap the session snapshot.
4. Failure keeps the old snapshot.

## Ordinary requests

Use the session snapshot; do not contact GitHub.

## Notes

- Platform support for many Skills may be `partial` (limited files/scripts).
- Loader does not self-update.

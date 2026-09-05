# Grok loader

Thin adapter over [`../common/PROTOCOL.md`](../common/PROTOCOL.md).

## Runtime shape

Grok.com Personal Skills (no local disk). Catalog sync is user-triggered only.

## Install once

Add Personal Skill from [`update-agent-skills.SKILL.md`](./update-agent-skills.SKILL.md) (Name: `update-agent-skills`).

## Update path

On **更新 skills** (aliases: 同步/刷新/reload/update skills):

1. Fetch public `https://raw.githubusercontent.com/wryApply/AI_repo/stable/generated/index.json`
2. Fetch each `skills/.../SKILL.md`
3. Stage → validate → replace matching Personal Skills
4. Failure keeps prior Personal Skills

## Ordinary requests

Use Personal Skills; do not contact GitHub until the next explicit update.

## Notes

- Many Skills are `partial` on Grok (limited files/scripts).
- Loader does not self-update.

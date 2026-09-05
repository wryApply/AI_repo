---
name: update-agent-skills
description: >-
  Use when the user says 更新 skills, 同步 skills, 刷新 skills, reload skills,
  or update skills. Pull the public wryApply/AI_repo stable catalog and refresh
  Grok Personal Skills to match. Do not pull unless the user explicitly asks.
---

# Update agent skills (Grok)

**Only** on explicit user request. Never pull on ordinary chat.

## Source of truth

Public GitHub (no auth):

- Index: https://raw.githubusercontent.com/wryApply/AI_repo/stable/generated/index.json
- Each skill: https://raw.githubusercontent.com/wryApply/AI_repo/stable/<root>/SKILL.md
  (use `root` from the index, e.g. `skills/teach/SKILL.md`)

Branch must be **stable**, never main for production updates.

## Procedure

1. Fetch `generated/index.json` from the URL above (browse/fetch tools).
2. Validate: JSON parses; each entry has `name`, `description`, `root`; for each entry fetch `<root>/SKILL.md` and confirm it is non-empty markdown with YAML frontmatter.
3. Stage: hold the new catalog in working memory (names + full SKILL.md bodies). Do not partially apply mid-fetch.
4. Apply: for each skill in the catalog, create or **replace** the matching Grok **Personal Skill** so Name = `name`, Description = index/frontmatter description, and the skill body = the fetched `SKILL.md` (frontmatter + body). Remove or disable Personal Skills that were previously installed from this registry but are no longer in the index **only if** they are clearly registry-managed (same names as prior update). Do not delete unrelated Personal Skills the user created.
5. Confirm to the user: commit/source tip if known, skill names installed, and that ordinary chats must not hit GitHub until the next explicit update.

## Failure

If any fetch/validate step fails: keep the previous Personal Skills unchanged, tell the user update failed, do not leave half-updated registry skills.

## Ordinary requests

After a successful update, use the refreshed Personal Skills. Do not contact GitHub again until the next 更新 skills.

---
name: update-agent-skills
description: >-
  Use when the user says 更新 skills, 同步 skills, 刷新 skills, reload skills,
  or update skills. Pull the public wryApply/AI_repo stable catalog and refresh
  ChatGPT Skills (or this GPT/Project skill snapshot) to match. Do not pull
  unless the user explicitly asks.
---

# Update agent skills (ChatGPT)

**Only** on explicit user request. Never pull on ordinary chat.

## Source of truth

Public GitHub (no auth):

- Index: https://raw.githubusercontent.com/wryApply/AI_repo/stable/generated/index.json
- Each skill: https://raw.githubusercontent.com/wryApply/AI_repo/stable/<root>/SKILL.md
  (use `root` from the index, e.g. `skills/teach/SKILL.md`)

Branch must be **stable**, never main for production updates.

## Procedure

1. Fetch `generated/index.json` from the URL above (browse / fetch / web tools).
2. Validate: JSON parses; each entry has `name`, `description`, `root`; for each entry fetch `<root>/SKILL.md` and confirm it is non-empty markdown with YAML frontmatter.
3. Stage: hold the new catalog in working memory (names + full SKILL.md bodies). Do not partially apply mid-fetch.
4. **ChatGPT frontmatter sanitize (required before save):** for each staged `SKILL.md`, rewrite the YAML frontmatter so it only keeps ChatGPT-accepted keys. Keep at least `name` and `description`. **Strip** registry-only keys that cause HTTP 422 / save rejection, including: `platforms`, `capabilities`, `priority`, and any other unknown keys beyond `name` / `description` (and `license` only if the UI already accepts it). Keep the markdown body after the closing `---` unchanged. Use the sanitized body for Apply; keep the original only as a private reference if needed for capability notes.
5. Apply (pick the strongest persistence the product allows, in this order):
   - If ChatGPT **Skills** (or Custom Skills) UI exists: for each catalog skill, create or **replace** the matching Skill so Name = `name`, Description = index/frontmatter description, and the skill body = the **sanitized** `SKILL.md`. If a save returns 422 or “拒绝”, strip more keys / retry once with a minimal frontmatter (`name` + `description` only) before failing the whole update.
   - Else if this is a **Custom GPT** or **Project**: write/replace Project files or GPT knowledge/instructions entries named after each skill (e.g. `skills/<name>/SKILL.md` or a single consolidated Skills section), keeping sanitized bodies.
   - Else: keep the staged catalog as the **current session snapshot** and tell the user it will not survive a new chat unless they paste it into Skills/GPT/Project.
   Remove or disable Skills that were previously installed from this registry but are no longer in the index **only if** they are clearly registry-managed (same names as a prior update). Do not delete unrelated Skills the user created (including this loader itself: never delete `update-agent-skills`).
6. Confirm to the user: `source_commit` from the index if present, skill names installed, any frontmatter keys stripped for ChatGPT, and that ordinary chats must not hit GitHub until the next explicit update.

## Platform limits

- ChatGPT often cannot run `scripts/` or host large `assets/` locally. If index `capabilities` mark them `optional`, skip and note; if `required` and unavailable, mark that skill partial/unavailable and say so. (Read capabilities from the **index JSON**, not from ChatGPT-facing frontmatter.)
- Large companions under a skill directory: fetch on demand only when the user actually needs that skill in the current turn; do not dump every asset into context on update.
- This loader does **not** self-update. To change the updater, the user must edit this Skill manually (or re-fetch this file from `loaders/chatgpt/update-agent-skills.SKILL.md` on `stable`).

## Failure

If any fetch/validate/save step fails after the sanitize retry: keep the previous Skills / session snapshot unchanged, tell the user update failed, do not leave half-updated registry skills.

## Ordinary requests

After a successful update, use the refreshed Skills / session snapshot. Do not contact GitHub again until the next 更新 skills.

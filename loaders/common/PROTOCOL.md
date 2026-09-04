# Loader protocol (common)

Shared contract for all platform loaders. Platform-specific adapters stay thin; Skill content stays in `skills/`.

## Triggers

Update **only** when the user explicitly requests it. Canonical phrase:

- **更新 skills**

Accepted aliases:

- `同步 skills`
- `刷新 skills`
- `reload skills`
- `update skills`

Ordinary chat must use the current local/session snapshot and must **not** contact GitHub.

## Source of truth

- Public repo: `wryApply/AI_repo`
- Production branch: **`stable`**
- Prefer the public **stable ZIP** (or equivalent archive of the `stable` ref), or raw paths on `stable`:
  - `generated/index.json`
  - `skills/*/SKILL.md` and companion files listed by the index

Do not load from `main` in production loaders.

## Atomic update (staging → current)

1. Download the stable snapshot into a **staging** location (directory or session staging buffer).
2. **Validate** staging (index present; each Skill has `SKILL.md`; optional local `validate_skills` if the platform can run scripts).
3. On success, **atomically** promote staging to **current** (rename/swap directories, or replace the session snapshot pointer).
4. On failure, **delete staging** and **keep the previous current snapshot** unchanged.

Never overwrite `current` in place mid-download.

## Snapshot identity

- Snapshot id = **`stable` commit SHA** (optionally also `updated_at`, `skill_count`).
- No per-Skill semantic versions in MVP.
- Record the SHA in local `state.json` (filesystem loaders) or in the session snapshot metadata (session loaders).

## Failure behavior

Any validation or I/O error during update: discard staging, retain the old snapshot, report failure to the user. Do not leave a half-applied tree as current.

## Loader self-update

**Loaders do not self-update.** Users install/replace loader docs or bootstrap scripts manually. Only Skill packages update via **更新 skills**.

## Discovery & composition

After load, Agents may auto-match Skills from the manifest (`name`, `description`, platform compatibility). Multiple Skills may be composed. Conflict resolution: system/platform rules > explicit current user request > explicitly named Skill > automatically matched Skill (higher `priority` wins among auto matches).

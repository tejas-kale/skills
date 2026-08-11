# skills

Personal agent-skills library built on [mattpocock/skills](https://github.com/mattpocock/skills), with room for local skills and in-place tweaks.

## Layout

```text
skills/
  engineering/     # from mattpocock/skills (edit in place to tweak)
  productivity/
  misc/
  in-progress/
  deprecated/
  local/           # skills authored here only — never overwritten by sync
.upstream/
  mattpocock-version   # pinned upstream release tag
  mattpocock/          # pristine mirror used as the 3-way merge base
scripts/
  sync-mattpocock.sh
.github/workflows/
  sync-mattpocock.yml
```

## Usage

Install into a project (Cursor, Codex, Claude Code, etc.):

```bash
npx skills@latest add tejas-kale/skills
```

Or copy the skill folders you want into `.cursor/skills/` / `.agents/skills/`.

After install in a consuming repo, run `/setup-matt-pocock-skills` once.

## Customizing Matt’s skills

Edit upstream skills **in place** under `skills/engineering/` (etc.). Keep the same skill name — do not copy to `skills/local/` under a new name for small tweaks.

Examples of good in-place tweaks:

- Prefer a lighter model for `/research` subagents launched from `/wayfinder`
- Adjust wording or defaults in a single section of a `SKILL.md`

Add brand-new skills only under `skills/local/`.

## Upstream sync

This repo pins a release of `mattpocock/skills` in `.upstream/mattpocock-version` (currently checked in at import time).

CI (`.github/workflows/sync-mattpocock.yml`):

- Runs on weekdays and via **Actions → Sync mattpocock/skills → Run workflow**
- Fetches the latest upstream release (or a ref you pass in)
- 3-way merges into `skills/`, preserving your in-place edits
- Refreshes `.upstream/mattpocock/` as the new merge base
- Opens a PR on branch `chore/sync-mattpocock-skills` for review

Manual sync locally:

```bash
bash scripts/sync-mattpocock.sh
# or pin a specific tag:
MATTPCOCK_SKILLS_REF=v1.2.3 bash scripts/sync-mattpocock.sh
```

If both you and upstream changed the same hunk, the sync script leaves conflict markers in the file and reports `conflicts > 0` on the PR — resolve those before merging.

## License

Upstream Matt Pocock skills are MIT — see `LICENSE.mattpocock`. Your local additions are yours to license as you like.

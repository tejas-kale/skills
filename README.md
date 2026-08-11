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
  mattpocock-version   # pinned upstream release tag (merge base is fetched from this tag)
scripts/
  sync-mattpocock.sh
.github/workflows/
  sync-mattpocock.yml
```

Matt’s skills live **once**, under `skills/`. The pin file is only a version pointer — sync fetches that tag from GitHub when it needs a merge base.

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

Pinned release: `.upstream/mattpocock-version`.

CI (`.github/workflows/sync-mattpocock.yml`):

- Runs **once a week** (and via **Actions → Sync mattpocock/skills → Run workflow**)
- **Exits with no PR** unless the latest upstream release differs from the pin
- 3-way merges into `skills/` (base = pinned tag, ours = your tree, theirs = new tag)
- Opens/updates `chore/sync-mattpocock-skills` with a PR body that includes:
  - file-level change summary (added / updated / merged / removed)
  - explicit **merge conflicts to resolve** (paths + what to do)
  - upstream release notes for the new tag

Manual sync locally:

```bash
bash scripts/sync-mattpocock.sh
# optional: sync to a specific newer tag
MATTPCOCK_SKILLS_REF=v1.2.3 bash scripts/sync-mattpocock.sh
```

## License

Upstream Matt Pocock skills are MIT — see `LICENSE.mattpocock`. Your local additions are yours to license as you like.

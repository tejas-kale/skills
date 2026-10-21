# Skills repo

Skills live in `skills/<name>/` (all agents) and `host/<name>/` (Mac-only). `README.md` has the layout, the manifest and `scripts/refresh`.

## Edit a skill

Edit `skills/<name>/` or `host/<name>/` only. Leave `~/.agents`, `~/.claude/skills` and any other install directory unchanged, and do not run `scripts/refresh` without being asked: it writes links there.

A skill with a row in `manifest.tsv` is an upstream copy. Edit it only for a local edit the user asked for, and add that edit to the list in `README.md`. Take upstream changes with `scripts/refresh --bump`, not by hand.

**Done when:** the definition in this repo is updated and no install location was written.

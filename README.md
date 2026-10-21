# skills

Tejas's agent skills, and the single source of skills for Claude Code on the host, the Claude Code container and the Pi container.

## Layout

```
skills/<name>/   every skill for every agent (host and containers), flat
host/<name>/     Mac-only skills (macos-disk-cleanup, german-shopping-receipts); never mounted into containers
manifest.tsv     one row per skill copied from an upstream: name, repo, path, commit
scripts/refresh  checks the layout, links skills into the agent dirs, bumps and adds upstream skills
licenses/        upstream licence texts
```

A skill dir holds a `SKILL.md` whose `name:` matches the dir name. A name may exist once across `skills/` and `host/`.

Skills without a manifest row are mine. Rows are skills copied from an upstream (see Credits). The copy is verbatim except for the local edits listed below, and `commit` is the upstream commit the copy is based on.

## Using the checkout

- Host: run `scripts/refresh`. It symlinks every dir in `skills/` and `host/` into `~/.claude/skills` and `~/.agents/skills`. It never replaces a real file or dir, or a symlink that points outside this checkout: it reports a conflict, carries on and exits non-zero. It removes links into this checkout whose skill is gone, and touches nothing else. Override the target dirs with `SKILL_LINK_DIRS` (colon-separated).
- Containers: the wrappers in `~/Code/config` mount `skills/` (not the repo root, not `host/`) read-only: at `~/.claude/skills` in the Claude container and `~/.pi/agent/skills` in the Pi container. A new skill is live in the next session, with no image rebuild. `SKILLS_DIR` overrides the mounted path.

## Refresh

```
scripts/refresh                              check manifest.tsv and the skill dirs, then link
scripts/refresh --bump <name|all> [ref]      merge upstream changes into the copies
scripts/refresh --add <name> <owner/repo> <path-in-repo> [ref]
```

`--bump` fetches the upstream repo and merges per file with `git merge-file`: base is upstream at the commit in the manifest, ours is the copy here, theirs is upstream at the new ref (default: the latest `vX.Y.Z` tag, else the default branch). My local edits survive. Files added upstream are added, files removed upstream are removed unless I edited them. The manifest records the new commit. It prints what updated cleanly, what was unchanged and what conflicted; conflicting files keep `<<<<<<<` markers to resolve by hand, and the exit status is non-zero. It never commits: review `git diff`, then commit.

`--add` copies one more upstream skill into `skills/<name>` and adds its row.

## Local edits on upstream copies

- `writing-for-agents/SKILL-MECHANICS.md`: a "Procedural anchor" section and a changed intro sentence.
- `grilling/SKILL.md`: ask each round through the harness's structured question tool when there is one (`AskUserQuestion`, `ask_user_question`).

## Credits

- [mattpocock/skills](https://github.com/mattpocock/skills) (MIT, `licenses/mattpocock-skills.LICENSE`): the `engineering`, `productivity` and `misc` skills at v1.3.1, except `git-guardrails-claude-code`.
- [ayghri/i-have-adhd](https://github.com/ayghri/i-have-adhd) (MIT, `licenses/i-have-adhd.LICENSE`): `i-have-adhd`.
- `show-me` is adapted from [humanlayer/skills](https://github.com/humanlayer/skills): ASCII output in place of Mermaid and HTML.

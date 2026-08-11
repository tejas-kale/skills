# skills

Personal fork of [mattpocock/skills](https://github.com/mattpocock/skills), plus skills of my own.

## Install

After this repo’s default branch has the `skills/` tree:

```bash
npx skills add tejas-kale/skills
```

Use `--skill <name>` for one skill, or follow the installer prompts for all agents.

## Layout

| Path | Purpose |
| --- | --- |
| `skills/engineering`, `productivity`, … | Matt’s skills — edit **in place** for small tweaks |
| `skills/local/` | Skills authored here |
| `.upstream/mattpocock-version` | Pinned upstream release |

## Upstream sync

Weekly GitHub Action checks for a new `mattpocock/skills` release. If the pin differs, it 3-way merges into `skills/` (keeping your tweaks) and opens a PR with release notes, file deltas, and any conflicts to resolve.

```bash
bash scripts/sync-mattpocock.sh   # local / manual
```

## License

Upstream skills: MIT (`LICENSE.mattpocock`). Local additions: yours.

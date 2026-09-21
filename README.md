# skills

Personal agent skills.

## Install

Use the Vercel **`skills`** package (`skills@latest`). Pinning `@latest` matters: a different npm package, **`skills-cli`**, also ships a `skills` binary. If that CLI is on your `PATH`, `npx skills add tejas-kale/skills` looks the slug up in *its* registry (not GitHub) and fails with `Skill "tejas-kale/skills" not found in registry`.

```bash
npx skills@latest add tejas-kale/skills
```

Or install from this repo (same CLI, full GitHub URL):

```bash
npx github:tejas-kale/skills
```

Use `--skill <name>` for one skill, or follow the installer prompts for all agents.

## Layout

Skills live under `skills/local/`.

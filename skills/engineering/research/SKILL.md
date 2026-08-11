---
name: research
description: Investigate a question against high-trust primary sources and capture the findings as a Markdown file in the repo. Use when the user wants a topic researched, docs or API facts gathered, or reading legwork delegated to a background agent.
---

Spin up a **background agent** to do the research, so you keep working while it reads. Pin a **mid-tier / fast** model on the spawn (`model` / equivalent) — never inherit a frontier parent:

- Claude Code → `sonnet`
- Cursor → `composer-2.5-fast` (or the cheapest mid-tier / `*-fast` slug available)
- Codex → `gpt-5.6-terra`
- Else → that provider's mid-tier or fast alias

If the exact slug isn't available, pick the closest cheaper mid-tier. If you are already the research agent, do the job yourself — do not re-delegate.

Its job:

1. Investigate the question against **primary sources** — official docs, source code, specs, first-party APIs — not a secondary write-up of them. Follow every claim back to the source that owns it.
2. Write the findings to a single Markdown file, citing each claim's source.
3. Save it where the repo already keeps such notes; match the existing convention, and if there is none, put it somewhere sensible and say where.

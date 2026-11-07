---
name: threads
description: Keep the session's open threads in `.threads/<date>-<slug>.md` at the repo root. Use at session start, when parking a question or side topic for later, and when a thread closes or the current one changes.
---

A **thread** is one open topic of the session: a question not yet answered, a side task, a decision still pending. The thread file is the session's agenda on disk, so it survives the session closing without `/bye`.

## The file

- **Path:** `<root>/.threads/<YYYY-MM-DD>-<slug>.md`. `<root>` is `git rev-parse --show-toplevel`, else the working directory. The date is the session's start date.
- **One file per session.** Create it when you park the first thread. Pick a 2-to-4-word kebab-case slug for the session's topic, then tell the user the file name in one line.
- `.threads/` is ignored through the global gitignore. Leave it out of commits and out of the repo's own `.gitignore`.

Format:

```markdown
---
started: 2026-11-07
tool: claude
continues: 2026-11-05-delegate-mod.md
---

## Open

1. Whether the delegate relay should log token counts
2. Rename pi-cache volume

## Closed

- Packaging -> new portable core, no mod
```

- `tool:` is the harness running this session: `claude`, `codex` or `agy`.
- `continues:` is present only when this session took over another file (written by `/bye` transfer).
- `## Open` is numbered, current thread first, one line per thread.
- `## Closed` holds `- <thread> -> <outcome>`, one line each, newest last.
- A transferred file also has a `## Handoff` section after `## Closed`.

## Keep it current

Write the file the moment a thread changes, before you reply:

- **Park:** add a new thread to `## Open`. When a message holds several questions, answer the first and park the rest, saying so in one line ("Parked 2 more in `.threads/2026-11-07-sandbox-image.md`").
- **Close:** move the thread to `## Closed` with its outcome in a few words.
- **Switch:** reorder `## Open` so the thread now being worked is `1.`.

Done when the file on disk matches the threads as they stand after your reply.

## Session start

At the first message of a session, check `<root>/.threads/` for files whose `## Open` is non-empty.

1. If none, carry on with the user's message.
2. Otherwise list them, one line each: file name and open count. Ask which to resume, or "new". Wait for the answer before doing anything else, including the user's first request.
3. **Resume:** read that file, and its `## Handoff` section if present. Keep using that file for this session. Say its first open thread in one line and start on it.
4. **New:** handle the user's message; create a new file when the first thread is parked.

## Closing a session

`/bye` closes or transfers the threads. It is user-invoked; mention it only when the user is wrapping up.

---
name: bye
description: End the session: close its threads file, or transfer the open threads to a new file for the next session.
disable-model-invocation: true
---

Run this when the user ends the session. It works on the session's threads file (`<root>/.threads/<date>-<slug>.md`); load the `threads` skill for the path and format.

1. **Find the file.** Use the file this session created or resumed. If there is none, say "No threads this session" and stop.
2. **List the open threads**, numbered as in `## Open`. If `## Open` is empty, say the file name and stop.
3. **Ask:** close, or transfer? Wait for the answer.

## Close

Change nothing. Say the file name so the user can resume it later: the next session in this repo offers it.

## Transfer

1. **Write the new file** `<root>/.threads/<today>-<slug>.md`, slug picked for what the next session will work on (a new slug if today's date would reuse the old name):
   - front matter: `started: <today>`, `tool:` this harness, `continues: <old file name>`;
   - `## Open`: the old file's open threads, same order;
   - `## Closed`: empty;
   - `## Handoff`, with these parts:
     - **Established:** decisions and facts the next session must take as settled, one line each.
     - **In progress:** what is half-done and its state (branch, uncommitted files, last command run).
     - **Pointers:** paths, commits, tickets, specs, PRs. Point at them; leave their content where it is.
     - **Suggested skills:** which skills the next session should load, and for what.
2. **Redact** secrets, tokens and personal data from the new file.
3. **Close the moved threads in the old file:** each one goes from `## Open` to `## Closed` as `- <thread> -> moved to <new file name>`, leaving `## Open` empty.
4. **Tell the user** the new file name, and to start a new session in this repo: it will offer the new file.

Done when the new file holds every open thread, the old file's `## Open` is empty, and the user has the new file name.

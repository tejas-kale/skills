# Mentor as a Claude project

`SKILL.md` serves both Claude Code and a Claude project; its "Where you run" section holds the differences. This file is for the user, not for the mentor.

## Set up (once)

1. Create a **private** project on claude.ai (GitHub content can only be added to a private project).
2. **Instructions:** paste `SKILL.md` from the line `# Mentor` to the end (leave out the front matter).
3. **Knowledge, from GitHub:** add the folder `skills/mentor/references/` of `tejas-kale/skills`.
4. **Knowledge, uploaded:** the state files (`charter.md`, `log.md`, `ledger.md`, `gate.md`, `parked.md`, `rule-requests.md`) from `~/Code/mentor`, if they exist. With no `charter.md`, the first chat runs Intake.

## Keep it current

| What changed | What to do |
|---|---|
| A new source was added to `references/` | Push, then **Sync now** in the project's knowledge panel |
| `SKILL.md` changed | Replace the project instructions with the new text; sync |
| A session ended | Replace the state files the mentor handed you |

Syncing is manual: the project does not see a push until you press **Sync now**.

## Adding sources

Do it in Claude Code in this repo, with the raw source attached: say "add this source to the mentor". The mentor writes the distillation and the index changes (`references/sources.md`); you commit, push and sync. It works in the project too, but there you have to copy the two files into the repo yourself.

Keep raw PDFs, articles and transcripts out of this repo and out of project knowledge. Attach one to a single chat when you want to distil it or check a citation.

## Size

The references are about 25k tokens. Project knowledge switches to retrieval (RAG) when it nears the context limit; past that point the mentor no longer sees the whole index at once, so routing gets worse. At about 10 KB a source, that is a few dozen more sources away.

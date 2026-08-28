---
name: harvest
description: Harvest durable project lessons from this session into memory, instructions, and skills.
argument-hint: "Optional scope (e.g. auth retries)"
disable-model-invocation: true
---

Harvest from **this session** into the **current project** so the next session needs fewer prompts or iterations.

If the user passed an argument, treat it as a scope limiter. No argument means the whole session.

Inspect in this session. Do not dispatch a subagent to read the conversation.

When editing the instruction file or a project skill, follow `/writing-for-agents`.

## 1. Gate

Stop and write nothing unless the cwd has a git root **or** a root `AGENTS.md` / `CLAUDE.md` / `.github/copilot-instructions.md`. Harvest is project-scoped.

**Done when:** you have a project, or you have stopped.

## 2. Identify stores

**Harness** layout for Cursor, Claude Code, Codex, Copilot CLI, and Copilot in VS Code: [HARNESSES.md](HARNESSES.md).

**Instruction file** (behaviour) — git-root only:

- `CLAUDE.md` if it exists, else `AGENTS.md`, unless this harness names a different file in [HARNESSES.md](HARNESSES.md).
- Create a root instruction file only when none of `CLAUDE.md`, `AGENTS.md`, or `.github/copilot-instructions.md` exists — ask which name. If only a nested `AGENTS.md` exists, edit that one and say so.

**Memory** (facts, decisions, project state, reasoning that may change):

- `docs/agents/memory.md` if `docs/agents/` exists, else `MEMORY.md` at repo root.
- The instruction file needs a **one-line pointer** at that file or the next session will not load it. Adding the pointer is an instruction-file edit.

**Project skills** (reusable workflows):

- Existing `.agents/skills`, `.claude/skills`, `.cursor/skills`, or `.github/skills`.
- If none, `.agents/skills/<name>/SKILL.md` plus an instruction-file pointer.
- One copy, in a project skill tree, not a personal skills library.

**Read-only:** `CONTEXT.md`, `CONTEXT-MAP.md`, `docs/adr/**`, tickets/specs from this session, and this harness's native memories in [HARNESSES.md](HARNESSES.md).

**Done when:** paths are chosen.

## 3. Read what already exists

Read the instruction file, memory file (if any), project skills, and the read-only files.

If this session already wrote glossary, ADRs, tickets, or specs, trust those files.

If terms look unresolved and `/domain-modeling` never ran, say so and suggest `/grill-with-docs` or `/domain-modeling`.

**Done when:** the instruction file, memory file (if any), project skills, and read-only files have been read.

## 4. Recover the thread

Use the context window plus **this session's transcript only** (id, cwd, mtime): user and assistant turns. Path in [HARNESSES.md](HARNESSES.md).

If the file is missing, unreadable, or ambiguous: harvest from the window and say recovery failed.

**Done when:** this session's transcript is read end to end, or recovery is declared failed.

## 5. Read artifacts

`git status`, staged and unstaged diff, paths this conversation clearly touched. Not `main...HEAD` unless the conversation was about those commits.

**Done when:** artifact evidence matches the scope.

## 6. Candidates

A lesson is a candidate only if **all** hold:

- **Would-have-shortened** — present at session start, this session would have needed fewer prompts or iterations.
- **Evidenced** — conversation (including recovered transcript) and artifacts agree, **or** the user explicitly corrected the agent.
- **Not already recorded** in the stores or read-only files above.
- **Not** secrets, one-off flakes, unsupported guesses, or session logistics.

Failures: wrong assumption, repeated dead end, user correction. Successes: a move that avoided a usual failure, a check that settled the work.

If none pass: report **nothing to harvest** and write nothing.

**Route** what passed:

- One-line fact / correction / state → memory
- Standing "always do X in this repo" → instruction file
- Named reusable **procedure** you would invoke again here → project skill (expensive; default to memory or one instruction line). Shape it with `/writing-for-agents`. Failure-only evidence → memory or one instruction-file warning, not a new skill.

**Conflicts:** quote both sides. Recommend overwrite only if this session showed the old text was wrong (user correction, or following it caused the wasted iterations). Conflict with a read-only file → skip and point at that file.

**Done when:** every candidate is routed, skipped with a reason, or marked as a conflict.

## 7. Present, then write

Show four groups:

1. **Will write now (memory)**
2. **Needs confirmation** — instruction-file edits (including the pointer), new or edited project skills, instruction-file deletions. Unified diff.
3. **Conflicts**
4. **Skipped**

Then write group 1 immediately. Memory shape: dated one-claim bullets under topic headings (`- 2026-08-15: …`). Create the file if missing. Prune a memory bullet autonomously when this session evidenced it false and removing it would-have-shortened the next session.

Wait for **one** yes/no on group 2. On no: keep memory writes; leave instruction file and skills untouched.

Leave git unstaged. Never `git add` or `git commit`.

**Done when:** memory writes that were going to happen have happened, and the user has answered the confirmation batch (or there was nothing to confirm).

## 8. Apply confirmation and report

On yes, apply group 2.

Report every write and skip. Leave git unstaged.

**Done when:** group 2 is applied or was empty, and the report lists every write and skip.

---
name: harvest
description: Harvest durable project lessons from this session into memory, instructions, and skills.
argument-hint: "Optional scope (e.g. auth retries)"
disable-model-invocation: true
---

Harvest from **this session** into the **current project** so the next session needs fewer prompts or iterations. Not a handoff, compact, or clear. Never write `CONTEXT.md` or ADRs.

If the user passed an argument, treat it as a scope limiter. No argument means the whole session.

Inspect in this session. Do not dispatch a subagent to read the conversation.

When editing the instruction file or a project skill, follow `/writing-for-agents`.

## 1. Gate

Stop and write nothing unless the cwd has a git root **or** a root `AGENTS.md` / `CLAUDE.md` / `.github/copilot-instructions.md`. Harvest is project-scoped.

**Done when:** you have a project, or you have stopped.

## 2. Identify stores

**Instruction file** (behaviour) — git-root only:

- Copilot session **and** `.github/copilot-instructions.md` exists → that file (Copilot always-on repo instructions). Path-specific `.github/instructions/*.instructions.md` are read-only; do not harvest into them.
- Else `CLAUDE.md` if it exists, else `AGENTS.md` (Copilot also loads `AGENTS.md` when present).
- If none of those exist, ask before creating. Never create the other name when one exists. Never create `.github/copilot-instructions.md` when `CLAUDE.md` or `AGENTS.md` already exists. Never create nested instruction files. If only a nested `AGENTS.md` exists, edit that one and say so.

**Memory** (facts, decisions, project state, reasoning that may change):

- `docs/agents/memory.md` if `docs/agents/` exists, else `MEMORY.md` at repo root.
- The instruction file needs a **one-line pointer** at that file or the next session will not load it. Adding the pointer is an instruction-file edit.

**Project skills** (reusable workflows):

- Existing `.agents/skills`, `.claude/skills`, `.cursor/skills`, or `.github/skills`.
- If none, `.agents/skills/<name>/SKILL.md` plus an instruction-file pointer. Copilot also reads `.agents/skills`; do not default to `.github/skills` unless that tree already exists.
- One copy. Never the personal skills library this skill lives in (`~/.copilot/skills` included).

**Read-only:** `CONTEXT.md`, `CONTEXT-MAP.md`, `docs/adr/**`, tickets/specs from this session, harness-native memories (`~/.claude/projects/*/memory/`, Cursor user memories, Codex personal memories, Copilot `~/.copilot/session-store.db` / Chronicle).

**Done when:** paths are chosen.

## 3. Read what already exists

Read the instruction file, memory file (if any), project skills, and `CONTEXT.md` / ADRs.

If this session already wrote glossary, ADRs, tickets, or specs, trust those files. Do not harvest a parallel conclusion.

If terms look unresolved and `/domain-modeling` never ran, say so and suggest `/grill-with-docs` or `/domain-modeling`. Do not backfill a glossary.

**Done when:** existing durable text is in view.

## 4. Recover the thread

Use the context window plus **this session's transcript only** (id, cwd, mtime). Skip other sessions. Skip system, permissions, and tool-catalog blobs.

| Harness | Transcript |
| --- | --- |
| Cursor | `~/.cursor/projects/<workspace>/agent-transcripts/<id>/<id>.jsonl` |
| Claude Code | `~/.claude/projects/<encoded-cwd>/<sessionId>.jsonl` |
| Codex | `~/.codex/sessions/YYYY/MM/DD/rollout-*.jsonl` (`session_meta` cwd / id) |
| Copilot CLI | `~/.copilot/session-state/<id>/events.jsonl` (`workspace.yaml` for cwd; `$COPILOT_HOME` replaces `~/.copilot`). `/session` prints the path. |
| Copilot in VS Code | `<user-data>/User/workspaceStorage/<hash>/GitHub.copilot-chat/transcripts/<id>.jsonl` — Linux `~/.config/Code`, macOS `~/Library/Application Support/Code`. Pick the hash whose `workspace.json` `folder` URI is this cwd. Fall back to `chatSessions/*.jsonl` in the same hash dir. |

If the file is missing, unreadable, or ambiguous: harvest from the window and say recovery failed.

**Done when:** conversation evidence is assembled.

## 5. Read artifacts

`git status`, staged and unstaged diff, paths this conversation clearly touched. Not `main...HEAD` unless the conversation was about those commits.

**Done when:** artifact evidence matches the scope.

## 6. Candidates

A lesson is a candidate only if **all** hold:

- **Would-have-shortened** — present at session start, this session would have needed fewer prompts or iterations.
- **Evidenced** — conversation (including recovered transcript) and artifacts agree, **or** the user explicitly corrected the agent.
- **Not already recorded** in the stores above (including Matt artifacts).
- **Not** secrets, one-off flakes, unsupported guesses, or session logistics.

Failures: wrong assumption, repeated dead end, user correction. Successes: a move that avoided a usual failure, a check that settled the work.

If none pass: report **nothing to harvest** and write nothing.

**Route** what passed:

- One-line fact / correction / state → memory
- Standing "always do X in this repo" → instruction file
- Named reusable procedure you would invoke again here, uncovered by an existing skill → project skill (expensive; default to memory or one instruction line)

**Conflicts:** do not overwrite or concatenate. Quote both. Recommend overwrite only if this session showed the old text was wrong (user correction, or following it caused the wasted iterations). Conflict with a Matt artifact → skip and point at that file.

**Done when:** every candidate is routed, skipped with a reason, or marked as a conflict.

## 7. Present, then write

Show four groups:

1. **Will write now (memory)**
2. **Needs confirmation** — instruction-file edits (including the pointer), new or edited project skills, instruction-file deletions. Unified diff.
3. **Conflicts**
4. **Skipped**

Then write group 1 immediately. Memory shape: dated one-claim bullets under topic headings (`- 2026-08-15: …`). Create the file if missing. Prune a memory bullet autonomously when this session evidenced it false and removing it would-have-shortened the next session.

Wait for **one** yes/no on group 2. On no: keep memory writes; leave instruction file and skills untouched.

Never `git add` or `git commit`.

**Done when:** memory writes that were going to happen have happened, and the user has answered the confirmation batch (or there was nothing to confirm).

## 8. Apply confirmation and report

On yes, apply group 2. Do not edit Matt's `## Agent skills` block except to add the memory pointer.

Report what was written and what was skipped. Leave git unstaged.

A later `/harvest` in this session is idempotent: only new candidates that still pass the bar and are not already in the stores.

**Done when:** the report is complete.

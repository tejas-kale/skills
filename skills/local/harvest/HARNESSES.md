# Harvest harnesses

One harness per run. Instruction-file exceptions, skill trees, native memories, and this session's transcript.

## Cursor

- **Skills:** `.cursor/skills` if that tree already exists.
- **Native memory (read-only):** Cursor user memories.
- **Transcript:** `~/.cursor/projects/<workspace>/agent-transcripts/<id>/<id>.jsonl`

## Claude Code

- **Skills:** `.claude/skills` if that tree already exists.
- **Native memory (read-only):** `~/.claude/projects/*/memory/`
- **Transcript:** `~/.claude/projects/<encoded-cwd>/<sessionId>.jsonl`

## Codex

- **Skills:** `.agents/skills` if that tree already exists.
- **Native memory (read-only):** Codex personal memories.
- **Transcript:** `~/.codex/sessions/YYYY/MM/DD/rollout-*.jsonl` (`session_meta` cwd / id)

## Copilot CLI

- **Instruction file:** `.github/copilot-instructions.md` when it exists (always-on repo instructions). Path-specific `.github/instructions/*.instructions.md` are read-only. Copilot also loads `AGENTS.md` when present.
- **Skills:** `.github/skills` if that tree already exists. New skills still go in `.agents/skills` unless `.github/skills` is already the project's tree. Personal library: `~/.copilot/skills`.
- **Native memory (read-only):** `~/.copilot/session-store.db` / Chronicle.
- **Transcript:** `~/.copilot/session-state/<id>/events.jsonl` (`workspace.yaml` for cwd; `$COPILOT_HOME` replaces `~/.copilot`). `/session` prints the path.

## Copilot in VS Code

Same instruction file, skills, and native memory as Copilot CLI.

- **Transcript:** `<user-data>/User/workspaceStorage/<hash>/GitHub.copilot-chat/transcripts/<id>.jsonl` — Linux `~/.config/Code`, macOS `~/Library/Application Support/Code`. Pick the hash whose `workspace.json` `folder` URI is this cwd. Fall back to `chatSessions/*.jsonl` in the same hash dir.

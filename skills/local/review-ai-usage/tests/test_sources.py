from __future__ import annotations

import shutil
from datetime import UTC, datetime
from pathlib import Path

from ai_transcripts.sources.claude_code import collect_claude_code
from ai_transcripts.sources.codex import collect_codex
from ai_transcripts.sources.copilot import collect_copilot
from ai_transcripts.sources.cursor import collect_cursor
from ai_transcripts.sources.vscode import collect_vscode

SINCE = datetime(2026, 9, 22, 0, 0, tzinfo=UTC)
UNTIL = datetime(2026, 9, 23, 0, 0, tzinfo=UTC)


def test_codex_emits_only_completed_turn(tmp_path: Path, fixtures: Path) -> None:
    target = tmp_path / "codex" / "sessions" / "2026" / "09" / "22"
    target.mkdir(parents=True)
    shutil.copy(fixtures / "codex" / "session.jsonl", target / "session.jsonl")

    report = collect_codex(tmp_path / "codex", SINCE, UNTIL)

    assert report.available
    assert {event.turn_id for event in report.events} == {"codex-turn"}
    assert {event.event_kind for event in report.events} == {"message", "tool_call", "tool_result"}


def test_claude_emits_messages_and_tools_from_completed_turn(tmp_path: Path, fixtures: Path) -> None:
    target = tmp_path / "claude" / "projects" / "project"
    target.mkdir(parents=True)
    shutil.copy(fixtures / "claude" / "session.jsonl", target / "session.jsonl")

    report = collect_claude_code(tmp_path / "claude", SINCE, UNTIL)

    assert {event.turn_id for event in report.events} == {"claude-turn"}
    assert [event.event_kind for event in report.events].count("tool_call") == 1
    assert [event.event_kind for event in report.events].count("tool_result") == 1


def test_copilot_classifies_vscode_agent_and_deduplicates_store(tmp_path: Path, fixtures: Path) -> None:
    target = tmp_path / "copilot" / "session-state" / "copilot-session"
    target.mkdir(parents=True)
    shutil.copy(fixtures / "copilot" / "events.jsonl", target / "events.jsonl")
    (target / "vscode.metadata.json").write_text("{}", encoding="utf-8")

    report = collect_copilot(tmp_path / "copilot", SINCE, UNTIL)

    assert report.events
    assert {event.interface for event in report.events} == {"copilot-vscode-agent"}
    assert len({event.event_id for event in report.events}) == len(report.events)


def test_cursor_reads_json_blobs_read_only(cursor_root: Path) -> None:
    database = next(cursor_root.glob("chats/*/*/store.db"))
    before = database.read_bytes()

    report = collect_cursor(cursor_root, SINCE, UNTIL)

    assert {event.turn_id for event in report.events} == {"turn-1"}
    assert {event.event_kind for event in report.events} == {"message", "tool_call", "tool_result"}
    assert database.read_bytes() == before


def test_vscode_reads_copilot_chat_transcripts(tmp_path: Path, fixtures: Path) -> None:
    workspace = tmp_path / "vscode" / "workspaceStorage" / "hash"
    target = workspace / "GitHub.copilot-chat" / "transcripts"
    target.mkdir(parents=True)
    shutil.copy(fixtures / "vscode" / "transcript.jsonl", target / "session.jsonl")
    (workspace / "workspace.json").write_text('{"folder": "/work/project"}\n', encoding="utf-8")

    report = collect_vscode(tmp_path / "vscode", SINCE, UNTIL)

    assert report.available
    assert {event.turn_id for event in report.events} == {"agent-turn"}
    assert [event.role for event in report.events] == ["user", "assistant", "tool", "assistant"]
    assert {event.interface for event in report.events} == {"copilot-vscode-agent"}
    assert {event.workspace for event in report.events} == {"/work/project"}
    assert "Still going." not in {event.text for event in report.events}


def test_vscode_replays_snapshot_and_ignores_incomplete_request(tmp_path: Path, fixtures: Path) -> None:
    target = tmp_path / "vscode" / "workspaceStorage" / "workspace" / "chatSessions"
    target.mkdir(parents=True)
    shutil.copy(fixtures / "vscode" / "session.jsonl", target / "session.jsonl")

    report = collect_vscode(tmp_path / "vscode", SINCE, UNTIL)

    assert {event.turn_id for event in report.events} == {"vscode-turn"}
    assert [event.role for event in report.events] == ["user", "assistant"]

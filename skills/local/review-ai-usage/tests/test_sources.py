from __future__ import annotations

import shutil
import json
import sqlite3
from datetime import UTC, datetime
from pathlib import Path

from ai_transcripts.sources.antigravity import collect_antigravity
from ai_transcripts.sources.claude_code import collect_claude_code
from ai_transcripts.sources.codex import collect_codex
from ai_transcripts.sources.copilot import collect_copilot
from ai_transcripts.sources.cursor import collect_cursor
from ai_transcripts.sources.vscode import collect_vscode

SINCE = datetime(2026, 9, 22, 0, 0, tzinfo=UTC)
UNTIL = datetime(2026, 9, 23, 0, 0, tzinfo=UTC)


def test_antigravity_emits_completed_turns_from_the_fuller_transcript(tmp_path: Path, fixtures: Path) -> None:
    logs = tmp_path / "agy" / "brain" / "agy-session" / ".system_generated" / "logs"
    logs.mkdir(parents=True)
    shutil.copy(fixtures / "antigravity" / "transcript_full.jsonl", logs / "transcript_full.jsonl")
    (logs / "transcript.jsonl").write_text(
        '{"step_index":0,"source":"USER_EXPLICIT","type":"USER_INPUT","status":"DONE",'
        '"created_at":"2026-09-22T10:00:00Z","content":"<USER_REQUEST>\\nfrom the truncated transcript\\n</USER_REQUEST>"}\n'
        '{"step_index":1,"source":"MODEL","type":"PLANNER_RESPONSE","status":"DONE",'
        '"created_at":"2026-09-22T10:00:01Z","content":"truncated answer"}\n',
        encoding="utf-8",
    )
    (tmp_path / "agy" / "history.jsonl").write_text(
        '{"timestamp":1790000000000,"workspace":"/work/project","type":"slash_command"}\n'
        '{"conversationId":"agy-session","timestamp":1790000001000,"workspace":"/work/project","display":"prompt"}\n',
        encoding="utf-8",
    )
    broken = tmp_path / "agy" / "brain" / "broken" / ".system_generated" / "logs"
    broken.mkdir(parents=True)
    (broken / "transcript_full.jsonl").write_text("not json\n", encoding="utf-8")

    report = collect_antigravity(tmp_path / "agy", SINCE, UNTIL)

    assert report.available
    assert report.failures
    assert [event.text for event in report.events if event.event_kind == "message"] == [
        "Check the report.",
        "The report is consistent.",
    ]
    assert [(event.event_kind, event.tool_name or event.event_id) for event in report.events] == [
        ("message", "2"),
        ("tool_call", "view_file"),
        ("tool_call", "list_dir"),
        ("tool_result", "4-0"),
        ("tool_result", "4-1"),
        ("message", "8"),
    ]
    assert report.events[1].tool_input == {"AbsolutePath": "report.md"}
    assert [event.tool_result for event in report.events if event.event_kind == "tool_result"] == ["file ok", "dir ok"]
    assert {event.workspace for event in report.events} == {"/work/project"}
    assert {event.session_id for event in report.events} == {"agy-session"}
    assert {event.turn_id for event in report.events} == {"2"}
    assert "private reasoning" not in {event.text for event in report.events}
    assert "Still working." not in {event.text for event in report.events}
    assert "truncated answer" not in {event.text for event in report.events}
    assert "Old answer." not in {event.text for event in report.events}


def test_antigravity_reads_transcript_jsonl_when_full_is_absent(tmp_path: Path) -> None:
    logs = tmp_path / "agy" / "brain" / "agy-session" / ".system_generated" / "logs"
    logs.mkdir(parents=True)
    (logs / "transcript.jsonl").write_text(
        '{"step_index":1,"source":"USER_EXPLICIT","type":"USER_INPUT","status":"DONE",'
        '"created_at":"2026-09-22T10:00:00Z","content":"Check the report."}\n'
        '{"step_index":2,"source":"MODEL","type":"PLANNER_RESPONSE","status":"DONE",'
        '"created_at":"2026-09-22T10:00:01Z","content":"The report is consistent."}\n',
        encoding="utf-8",
    )

    report = collect_antigravity(tmp_path / "agy", SINCE, UNTIL)

    assert [event.text for event in report.events] == ["Check the report.", "The report is consistent."]


def test_antigravity_without_transcripts_is_unavailable(tmp_path: Path) -> None:
    assert not collect_antigravity(tmp_path / "missing", SINCE, UNTIL).available
    (tmp_path / "agy").mkdir()
    assert not collect_antigravity(tmp_path / "agy", SINCE, UNTIL).available


def test_codex_emits_only_completed_turn(tmp_path: Path, fixtures: Path) -> None:
    target = tmp_path / "codex" / "sessions" / "2026" / "09" / "22"
    target.mkdir(parents=True)
    shutil.copy(fixtures / "codex" / "session.jsonl", target / "session.jsonl")

    report = collect_codex(tmp_path / "codex", SINCE, UNTIL)

    assert report.available
    assert {event.turn_id for event in report.events} == {"codex-turn"}
    assert {event.event_kind for event in report.events} == {"message", "tool_call", "tool_result"}


def test_codex_preserves_interface_value_from_source_metadata(tmp_path: Path) -> None:
    target = tmp_path / "codex" / "sessions" / "2026" / "09" / "22"
    target.mkdir(parents=True)
    (target / "session.jsonl").write_text(
        '{"type":"session_meta","payload":{"session_id":"s","source":{"type":"vscode"}}}\n'
        '{"type":"turn_context","payload":{"turn_id":"t"}}\n'
        '{"type":"response_item","timestamp":"2026-09-22T08:00:00Z","payload":{"type":"message","id":"m","role":"user","content":"hello"}}\n'
        '{"type":"event_msg","payload":{"type":"task_complete","turn_id":"t"}}\n',
        encoding="utf-8",
    )

    report = collect_codex(tmp_path / "codex", SINCE, UNTIL)

    assert report.events[0].interface == "vscode"


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


def test_cursor_filters_messages_by_their_own_timestamps(tmp_path: Path) -> None:
    session = tmp_path / "cursor" / "chats" / "workspace" / "session"
    session.mkdir(parents=True)
    (session / "meta.json").write_text(json.dumps({
        "updatedAtMs": 1790074860000,
        "cwd": "/work/project",
    }), encoding="utf-8")
    messages = [
        {"role": "user", "content": "old", "timestamp": "2026-09-21T10:00:00Z"},
        {"role": "assistant", "content": "old answer", "timestamp": "2026-09-21T10:01:00Z"},
        {"role": "user", "content": "new", "timestamp": "2026-09-22T10:00:00Z"},
        {"role": "assistant", "content": "new answer", "timestamp": "2026-09-22T10:01:00Z"},
    ]
    database = sqlite3.connect(session / "store.db")
    database.execute("CREATE TABLE blobs (id TEXT PRIMARY KEY, data BLOB)")
    for index, message in enumerate(messages):
        database.execute("INSERT INTO blobs (id, data) VALUES (?, ?)", (f"blob-{index}", json.dumps(message).encode()))
    database.commit()
    database.close()

    report = collect_cursor(tmp_path / "cursor", SINCE, UNTIL)

    assert [event.text for event in report.events] == ["new", "new answer"]


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

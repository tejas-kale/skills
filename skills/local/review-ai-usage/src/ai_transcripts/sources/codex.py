from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any

from ..content import json_value, text_content
from ..model import Event, SourceReport
from ..time import in_window, iso_timestamp
from .common import collect_files, read_jsonl


def collect_codex(root: Path, since: datetime | None, until: datetime | None) -> SourceReport:
    files = sorted(root.glob("sessions/**/*.jsonl")) + sorted(root.glob("archived_sessions/*.jsonl"))
    return collect_files("codex", files if root.exists() else [], _read_session, since, until)


def _read_session(path: Path, since: datetime | None, until: datetime | None) -> list[Event]:
    records = list(read_jsonl(path))
    session_id = path.stem
    workspace = ""
    interface = "codex"
    current_turn = ""
    completed_turns: set[str] = set()
    pending: list[tuple[int, dict[str, Any], str]] = []

    for line_number, record in records:
        kind = record.get("type")
        payload = record.get("payload", {})
        if kind == "session_meta":
            session_id = str(payload.get("session_id") or payload.get("id") or session_id)
            workspace = str(payload.get("cwd") or "")
            source_value = payload.get("source") or payload.get("originator") or "codex"
            interface = next(iter(source_value.values()), "codex") if isinstance(source_value, dict) else str(source_value)
        elif kind == "turn_context":
            current_turn = str(payload.get("turn_id") or current_turn)
            workspace = str(payload.get("cwd") or workspace)
        elif kind == "event_msg" and payload.get("type") == "task_started":
            current_turn = str(payload.get("turn_id") or current_turn)
        elif kind == "event_msg" and payload.get("type") == "task_complete":
            turn = str(payload.get("turn_id") or current_turn)
            if turn:
                completed_turns.add(turn)
        elif kind == "response_item" and current_turn:
            pending.append((line_number, record, current_turn))

    result: list[Event] = []
    for line_number, record, turn_id in pending:
        if turn_id not in completed_turns:
            continue
        timestamp = record.get("timestamp")
        if not in_window(timestamp, since, until):
            continue
        payload = record.get("payload", {})
        payload_type = payload.get("type")
        event_id = str(payload.get("id") or payload.get("call_id") or line_number)
        common = dict(
            source="codex",
            interface=interface,
            session_id=session_id,
            turn_id=turn_id,
            event_id=event_id,
            timestamp=iso_timestamp(timestamp),
            workspace=workspace,
            completed=True,
            source_metadata={"line": line_number},
        )
        if payload_type == "message" and payload.get("role") in {"user", "assistant"}:
            result.append(Event(
                **common,
                role=str(payload["role"]),
                event_kind="message",
                text=text_content(payload.get("content")),
            ))
        elif payload_type in {"function_call", "custom_tool_call"}:
            result.append(Event(
                **common,
                role="assistant",
                event_kind="tool_call",
                tool_name=str(payload.get("name") or ""),
                tool_input=json_value(payload.get("arguments", payload.get("input"))),
            ))
        elif payload_type in {"function_call_output", "custom_tool_call_output"}:
            result.append(Event(
                **common,
                role="tool",
                event_kind="tool_result",
                tool_result=json_value(payload.get("output")),
            ))
    return result

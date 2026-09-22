from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any

from ..content import text_content
from ..model import Event, SourceReport
from ..time import in_window, iso_timestamp
from .common import collect_files, read_jsonl


def collect_claude_code(root: Path, since: datetime | None, until: datetime | None) -> SourceReport:
    files = sorted(root.glob("projects/*/*.jsonl"))
    return collect_files("claude-code", files if root.exists() else [], _read_session, since, until)


def _is_human_prompt(record: dict[str, Any]) -> bool:
    if record.get("type") != "user" or record.get("isMeta"):
        return False
    content = record.get("message", {}).get("content")
    if isinstance(content, str):
        return bool(content.strip())
    if isinstance(content, list):
        return any(isinstance(item, dict) and item.get("type") == "text" for item in content)
    return False


def _read_session(path: Path, since: datetime | None, until: datetime | None) -> list[Event]:
    records = list(read_jsonl(path))
    session_id = path.stem
    workspace = ""
    current_turn = ""
    completed_turns: set[str] = set()
    pending: list[tuple[int, dict[str, Any], str]] = []

    for line_number, record in records:
        session_id = str(record.get("sessionId") or record.get("session_id") or session_id)
        workspace = str(record.get("cwd") or workspace)
        if _is_human_prompt(record):
            current_turn = str(record.get("uuid") or f"turn-{line_number}")
        if record.get("type") in {"user", "assistant"} and current_turn:
            pending.append((line_number, record, current_turn))
        if record.get("type") == "assistant":
            stop_reason = record.get("message", {}).get("stop_reason")
            if stop_reason in {"end_turn", "stop_sequence", "stop"}:
                completed_turns.add(current_turn)

    result: list[Event] = []
    for line_number, record, turn_id in pending:
        if turn_id not in completed_turns or not in_window(record.get("timestamp"), since, until):
            continue
        message = record.get("message", {})
        role = str(message.get("role") or record.get("type") or "")
        content = message.get("content")
        common = dict(
            source="claude-code",
            interface=str(record.get("entrypoint") or "claude-code"),
            session_id=session_id,
            turn_id=turn_id,
            timestamp=iso_timestamp(record.get("timestamp")),
            workspace=workspace,
            completed=True,
            source_metadata={"line": line_number},
        )
        message_text = text_content(content)
        if message_text:
            result.append(Event(
                **common,
                event_id=str(record.get("uuid") or line_number),
                role=role,
                event_kind="message",
                text=message_text,
            ))
        if isinstance(content, list):
            for index, item in enumerate(content):
                if not isinstance(item, dict):
                    continue
                if item.get("type") == "tool_use":
                    result.append(Event(
                        **common,
                        event_id=str(item.get("id") or f"{line_number}-{index}"),
                        role="assistant",
                        event_kind="tool_call",
                        tool_name=str(item.get("name") or ""),
                        tool_input=item.get("input"),
                    ))
                elif item.get("type") == "tool_result":
                    result.append(Event(
                        **common,
                        event_id=str(item.get("tool_use_id") or f"{line_number}-{index}"),
                        role="tool",
                        event_kind="tool_result",
                        tool_result=item.get("content"),
                    ))
    return result

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any

from ..content import text_content
from ..model import Event, SourceReport
from ..time import in_window, iso_timestamp
from .common import collect_files, read_jsonl


def collect_pi(root: Path, since: datetime | None, until: datetime | None) -> SourceReport:
    session_files = sorted(root.glob("sessions/*/*.jsonl"))
    legacy_files = sorted(root.glob("*.jsonl"))
    files = session_files + legacy_files
    return collect_files("pi", files if root.exists() else [], _read_session, since, until)


def _read_session(path: Path, since: datetime | None, until: datetime | None) -> list[Event]:
    records = list(read_jsonl(path))
    if not records:
        return []

    session_id = ""
    workspace = ""
    first_record = records[0][1]
    if first_record.get("type") == "session":
        session_id = str(first_record.get("id", ""))
        workspace = str(first_record.get("cwd", ""))

    current_turn = ""
    completed_turns: set[str] = set()
    pending: list[tuple[int, dict[str, Any], str]] = []

    for line_number, record in records:
        if record.get("type") == "session":
            continue
        message = record.get("message", {})
        role = str(message.get("role", ""))
        timestamp = record.get("timestamp")

        if role == "user" and text_content(message.get("content")):
            current_turn = str(record.get("id", f"turn-{line_number}"))

        if current_turn and in_window(timestamp, since, until):
            pending.append((line_number, record, current_turn))

        if role == "assistant":
            stop_reason = message.get("stopReason")
            end_turn = message.get("endTurn")
            if stop_reason in {"stop", "error", "aborted"} or end_turn is True:
                completed_turns.add(current_turn)

    result: list[Event] = []
    for line_number, record, turn_id in pending:
        if turn_id not in completed_turns:
            continue
        message = record.get("message", {})
        role = str(message.get("role", ""))
        content = message.get("content")
        timestamp = record.get("timestamp")

        common = dict(
            source="pi",
            interface="pi-agent",
            session_id=session_id,
            turn_id=turn_id,
            timestamp=iso_timestamp(timestamp),
            workspace=workspace,
            completed=True,
            source_metadata={"line": line_number},
        )

        if role == "user":
            message_text = text_content(content)
            if message_text:
                result.append(Event(
                    **common,
                    event_id=str(record.get("id", line_number)),
                    role="user",
                    event_kind="message",
                    text=message_text,
                ))
        elif role == "assistant":
            if isinstance(content, list):
                for index, item in enumerate(content):
                    if not isinstance(item, dict):
                        continue
                    item_type = item.get("type")
                    if item_type == "text":
                        text = str(item.get("text", ""))
                        if text:
                            result.append(Event(
                                **common,
                                event_id=str(record.get("id", f"{line_number}-{index}")),
                                role="assistant",
                                event_kind="message",
                                text=text,
                            ))
                    elif item_type == "toolCall":
                        tool_name = str(item.get("name", ""))
                        tool_input = item.get("arguments") or item.get("input")
                        result.append(Event(
                            **common,
                            event_id=str(item.get("id", f"{line_number}-{index}")),
                            role="assistant",
                            event_kind="tool_call",
                            tool_name=tool_name,
                            tool_input=tool_input,
                        ))
                    elif item_type == "thinking":
                        pass
        elif role == "toolResult":
            tool_call_id = str(message.get("toolCallId", ""))
            tool_name = str(message.get("toolName", ""))
            tool_result_text = text_content(message.get("content"))
            result.append(Event(
                **common,
                event_id=tool_call_id or str(line_number),
                role="tool",
                event_kind="tool_result",
                tool_name=tool_name,
                tool_result=tool_result_text,
            ))
        elif role == "bashExecution":
            command = str(message.get("command", ""))
            output = str(message.get("output", ""))
            exit_code = message.get("exitCode")
            result.append(Event(
                **common,
                event_id=f"{record.get('id', line_number)}-call",
                role="assistant",
                event_kind="tool_call",
                tool_name="bash",
                tool_input={"command": command},
            ))
            result.append(Event(
                **common,
                event_id=f"{record.get('id', line_number)}-result",
                role="tool",
                event_kind="tool_result",
                tool_name="bash",
                tool_result=f"{output}\n[exit {exit_code}]" if exit_code is not None else output,
            ))

    return result
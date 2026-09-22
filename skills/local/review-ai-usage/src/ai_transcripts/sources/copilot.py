from __future__ import annotations

from datetime import datetime
from pathlib import Path

from ..content import json_value, text_content
from ..model import Event, SourceReport
from ..time import in_window, iso_timestamp
from .common import collect_files, read_jsonl


def collect_copilot(root: Path, since: datetime | None, until: datetime | None) -> SourceReport:
    files = sorted(root.glob("session-state/*/events.jsonl"))
    return collect_files("copilot", files if root.exists() else [], _read_session, since, until)


def _read_session(path: Path, since: datetime | None, until: datetime | None) -> list[Event]:
    records = list(read_jsonl(path))
    session_id = path.parent.name
    workspace = ""
    completed_turns = {
        str(record.get("data", {}).get("turnId"))
        for _, record in records
        if record.get("type") == "assistant.turn_end"
    }
    interface = "copilot-vscode-agent" if (path.parent / "vscode.metadata.json").exists() else "copilot-cli"
    result: list[Event] = []
    for line_number, record in records:
        data = record.get("data", {})
        if record.get("type") == "session.start":
            session_id = str(data.get("sessionId") or session_id)
            context = data.get("context", {})
            if isinstance(context, dict):
                workspace = str(context.get("cwd") or context.get("workspace") or workspace)
            continue
        turn_id = str(data.get("turnId") or data.get("interactionId") or "")
        if not turn_id or turn_id not in completed_turns:
            continue
        if not in_window(record.get("timestamp"), since, until):
            continue
        event_type = str(record.get("type") or "")
        common = dict(
            source="copilot",
            interface=interface,
            session_id=session_id,
            turn_id=turn_id,
            event_id=str(record.get("id") or line_number),
            timestamp=iso_timestamp(record.get("timestamp")),
            workspace=workspace,
            completed=True,
            source_metadata={"line": line_number},
        )
        if event_type == "user.message":
            result.append(Event(**common, role="user", event_kind="message", text=text_content(data.get("content"))))
        elif event_type == "assistant.message":
            result.append(Event(**common, role="assistant", event_kind="message", text=text_content(data.get("content"))))
        elif event_type == "tool.execution_start":
            result.append(Event(
                **common,
                role="assistant",
                event_kind="tool_call",
                tool_name=str(data.get("toolName") or ""),
                tool_input=json_value(data.get("arguments")),
            ))
        elif event_type == "tool.execution_complete":
            result.append(Event(
                **common,
                role="tool",
                event_kind="tool_result",
                tool_result=data.get("result", data.get("error")),
            ))
    return result

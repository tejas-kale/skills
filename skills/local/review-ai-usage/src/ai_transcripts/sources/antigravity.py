from __future__ import annotations

import re
from datetime import datetime
from pathlib import Path
from typing import Any

from ..content import json_value
from ..model import Event, SourceReport
from ..time import in_window, iso_timestamp
from .common import collect_files, read_jsonl


_IGNORED = {"CHECKPOINT", "CONVERSATION_HISTORY"}
_USER_REQUEST = re.compile(r"<USER_REQUEST>(.*?)</USER_REQUEST>", re.DOTALL)


def collect_antigravity(root: Path, since: datetime | None, until: datetime | None) -> SourceReport:
    files = _transcript_files(root)
    workspaces = _workspaces(root / "history.jsonl")

    def read(path: Path, since_value: datetime | None, until_value: datetime | None) -> list[Event]:
        return _read_session(path, workspaces.get(_conversation_id(path), ""), since_value, until_value)

    return collect_files("antigravity-cli", files, read, since, until)


def _transcript_files(root: Path) -> list[Path]:
    brain = root / "brain"
    if not brain.is_dir():
        return []
    files: list[Path] = []
    for conversation in sorted(path for path in brain.iterdir() if path.is_dir()):
        logs = conversation / ".system_generated" / "logs"
        chosen = _choose_transcript(logs)
        if chosen is not None:
            files.append(chosen)
    return files


def _choose_transcript(logs: Path) -> Path | None:
    existing = [path for name in ("transcript_full.jsonl", "transcript.jsonl") if (path := logs / name).is_file()]
    if not existing:
        return None
    return max(existing, key=lambda path: (path.stat().st_size, path.name == "transcript_full.jsonl"))


def _workspaces(path: Path) -> dict[str, str]:
    workspaces: dict[str, str] = {}
    if not path.is_file():
        return workspaces
    try:
        records = list(read_jsonl(path))
    except (OSError, UnicodeError, ValueError):
        return {}
    for _, record in records:
        conversation_id = record.get("conversationId")
        workspace = record.get("workspace")
        if conversation_id and isinstance(workspace, str):
            workspaces[str(conversation_id)] = workspace
    return workspaces


def _conversation_id(path: Path) -> str:
    for parent in path.parents:
        if parent.name == ".system_generated":
            return parent.parent.name
    return path.stem


def _read_session(path: Path, workspace: str, since: datetime | None, until: datetime | None) -> list[Event]:
    session_id = _conversation_id(path)
    turns: list[list[tuple[int, dict[str, Any]]]] = []
    current: list[tuple[int, dict[str, Any]]] | None = None
    for line_number, record in read_jsonl(path):
        if record.get("type") == "USER_INPUT" and record.get("source") != "SYSTEM":
            current = []
            turns.append(current)
        if current is not None:
            current.append((line_number, record))
    events: list[Event] = []
    for turn in turns:
        if _completed(turn):
            events.extend(_turn_events(turn, session_id, workspace, since, until))
    return events


def _completed(records: list[tuple[int, dict[str, Any]]]) -> bool:
    pending = 0
    terminal = False
    for _, record in records:
        kind = record.get("type")
        if kind in _IGNORED or kind == "USER_INPUT":
            continue
        if kind == "PLANNER_RESPONSE":
            calls = _tool_calls(record)
            content = record.get("content")
            has_content = isinstance(content, str) and bool(content.strip())
            terminal = has_content and not calls and record.get("status") == "DONE" and pending == 0
            pending += len(calls)
        elif pending:
            pending -= 1
    return terminal and pending == 0


def _tool_calls(record: dict[str, Any]) -> list[dict[str, Any]]:
    calls = record.get("tool_calls")
    if not isinstance(calls, list):
        return []
    return [call for call in calls if isinstance(call, dict)]


def _turn_events(
    records: list[tuple[int, dict[str, Any]]],
    session_id: str,
    workspace: str,
    since: datetime | None,
    until: datetime | None,
) -> list[Event]:
    turn_id = _step_id(records[0][1], records[0][0])
    pending: list[str] = []
    events: list[Event] = []
    for line_number, record in records:
        kind = record.get("type")
        if kind in _IGNORED:
            continue
        visible = in_window(record.get("created_at"), since, until)
        timestamp = iso_timestamp(record.get("created_at"))
        step_id = _step_id(record, line_number)
        common = dict(
            source="antigravity-cli",
            interface="antigravity-cli",
            session_id=session_id,
            turn_id=turn_id,
            timestamp=timestamp,
            workspace=workspace,
            completed=True,
            source_metadata={"line": line_number},
        )
        if kind == "USER_INPUT":
            text = _user_text(record.get("content"))
            if visible and text:
                events.append(Event(**common, event_id=step_id, role="user", event_kind="message", text=text))
        elif kind == "PLANNER_RESPONSE":
            content = record.get("content")
            if visible and isinstance(content, str) and content.strip():
                events.append(Event(
                    **common,
                    event_id=step_id,
                    role="assistant",
                    event_kind="message",
                    text=content.strip(),
                ))
            for index, call in enumerate(_tool_calls(record)):
                event_id = f"{step_id}-{index}"
                pending.append(event_id)
                if visible:
                    events.append(Event(
                        **common,
                        event_id=event_id,
                        role="assistant",
                        event_kind="tool_call",
                        tool_name=str(call.get("name") or ""),
                        tool_input=json_value(call.get("args")),
                    ))
        elif pending:
            event_id = pending.pop(0)
            if visible:
                events.append(Event(
                    **common,
                    event_id=event_id,
                    role="tool",
                    event_kind="tool_result",
                    tool_result=record.get("content"),
                ))
    return events


def _step_id(record: dict[str, Any], line_number: int) -> str:
    step_index = record.get("step_index")
    return str(step_index if step_index is not None else line_number)


def _user_text(content: Any) -> str:
    if not isinstance(content, str):
        return ""
    match = _USER_REQUEST.search(content)
    return (match.group(1) if match else content).strip()

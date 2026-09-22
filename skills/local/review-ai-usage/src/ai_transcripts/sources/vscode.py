from __future__ import annotations

import copy
import json
from datetime import datetime
from pathlib import Path
from typing import Any

from ..content import json_value, text_content
from ..model import Event, SourceFailure, SourceReport
from ..time import in_window, iso_timestamp
from .common import read_jsonl


_CHAT_GLOBS = (
    "workspaceStorage/*/chatSessions/*.jsonl",
    "globalStorage/emptyWindowChatSessions/*.jsonl",
)
_TRANSCRIPT_GLOBS = (
    "workspaceStorage/*/GitHub.copilot-chat/transcripts/*.jsonl",
    "workspaceStorage/*/github.copilot-chat/transcripts/*.jsonl",
)
_TRANSCRIPT_EVENTS = {
    "user.message": ("user", "message"),
    "assistant.message": ("assistant", "message"),
    "tool.execution_start": ("assistant", "tool_call"),
    "tool.execution_complete": ("tool", "tool_result"),
}


def collect_vscode(root: Path, since: datetime | None, until: datetime | None) -> SourceReport:
    if not root.exists():
        return SourceReport("copilot-vscode", available=False)
    chats = _discover(root, _CHAT_GLOBS)
    transcripts = _discover(root, _TRANSCRIPT_GLOBS)
    if not chats and not transcripts:
        return SourceReport("copilot-vscode", available=False)
    events: list[Event] = []
    failures: list[SourceFailure] = []
    for path in chats:
        try:
            events.extend(_read_session(path, since, until))
        except (OSError, ValueError, TypeError, json.JSONDecodeError) as exc:
            failures.append(SourceFailure("copilot-vscode", str(path), str(exc)))
    for path in transcripts:
        try:
            events.extend(_read_transcript(path, since, until))
        except (OSError, ValueError, TypeError, json.JSONDecodeError) as exc:
            failures.append(SourceFailure("copilot-vscode", str(path), str(exc)))
    return SourceReport("copilot-vscode", available=True, events=tuple(events), failures=tuple(failures))


def _discover(root: Path, patterns: tuple[str, ...]) -> list[Path]:
    found: list[Path] = []
    seen: set[tuple[int, int]] = set()
    for pattern in patterns:
        for path in sorted(root.glob(pattern)):
            stat = path.stat()
            key = (stat.st_dev, stat.st_ino)
            if key in seen:
                continue
            seen.add(key)
            found.append(path)
    return found


def _apply_patch(state: dict[str, Any], keys: list[Any], value: Any) -> None:
    target: Any = state
    for key in keys[:-1]:
        if isinstance(target, list) and isinstance(key, int):
            while len(target) <= key:
                target.append({})
            target = target[key]
        elif isinstance(target, dict):
            target = target.setdefault(str(key), {})
        else:
            return
    if not keys:
        return
    last = keys[-1]
    if isinstance(target, list) and isinstance(last, int):
        while len(target) <= last:
            target.append(None)
        target[last] = value
    elif isinstance(target, dict):
        target[str(last)] = value


def _snapshot(path: Path) -> dict[str, Any]:
    state: dict[str, Any] = {}
    for _, record in read_jsonl(path):
        if record.get("kind") == 0 and isinstance(record.get("v"), dict):
            state = copy.deepcopy(record["v"])
        elif record.get("kind") == 1 and isinstance(record.get("k"), list):
            _apply_patch(state, record["k"], record.get("v"))
    return state


def _workspace(path: Path) -> str:
    workspace_json: Path | None = None
    for parent in path.parents:
        candidate = parent / "workspace.json"
        if candidate.is_file():
            workspace_json = candidate
            break
        if parent.name in {"workspaceStorage", "globalStorage"}:
            break
    if workspace_json is None:
        return ""
    try:
        value = json.loads(workspace_json.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return ""
    return str(value.get("folder") or value.get("workspace") or "") if isinstance(value, dict) else ""


def _read_session(path: Path, since: datetime | None, until: datetime | None) -> list[Event]:
    state = _snapshot(path)
    session_id = str(state.get("sessionId") or path.stem)
    workspace = _workspace(path)
    result: list[Event] = []
    requests = state.get("requests", [])
    if not isinstance(requests, list):
        return result
    for index, request in enumerate(requests):
        if not isinstance(request, dict):
            continue
        timestamp_value = request.get("timestamp") or request.get("requestTimestamp") or state.get("creationDate")
        response = request.get("response")
        completed = bool(request.get("result") is not None or response)
        if not completed or not in_window(timestamp_value, since, until):
            continue
        turn_id = str(request.get("requestId") or f"turn-{index + 1}")
        request_text = text_content(request.get("message", request.get("request", request.get("text", ""))))
        common = dict(
            source="copilot-vscode",
            interface="copilot-vscode-chat",
            session_id=session_id,
            turn_id=turn_id,
            timestamp=iso_timestamp(timestamp_value),
            workspace=workspace,
            completed=True,
            source_metadata={"request_index": index},
        )
        if request_text:
            result.append(Event(
                **common,
                event_id=f"{turn_id}-user",
                role="user",
                event_kind="message",
                text=request_text,
            ))
        response_text = (
            "\n".join(text_content(item) for item in response if text_content(item))
            if isinstance(response, list)
            else text_content(response)
        )
        if response_text:
            result.append(Event(
                **common,
                event_id=f"{turn_id}-assistant",
                role="assistant",
                event_kind="message",
                text=response_text,
            ))
    return result


def _read_transcript(path: Path, since: datetime | None, until: datetime | None) -> list[Event]:
    records = list(read_jsonl(path))
    session_id = path.stem
    producer = ""
    completed: set[str] = set()
    for _, record in records:
        data = record.get("data")
        if not isinstance(data, dict):
            continue
        if record.get("type") == "session.start":
            session_id = str(data.get("sessionId") or session_id)
            producer = str(data.get("producer") or producer)
        elif record.get("type") == "assistant.turn_end" and data.get("turnId") is not None:
            completed.add(str(data["turnId"]))
    interface = "copilot-vscode-agent" if not producer or "agent" in producer else "copilot-vscode-chat"
    workspace = _workspace(path)
    buffer: list[tuple[int, dict[str, Any]]] = []
    result: list[Event] = []

    def flush(turn_id: str) -> None:
        nonlocal buffer
        for line_number, record in buffer:
            data = record.get("data") if isinstance(record.get("data"), dict) else {}
            event_turn = str(data.get("turnId") or data.get("interactionId") or turn_id)
            if event_turn not in completed:
                continue
            event = _transcript_event(
                record, data, line_number, session_id, event_turn, workspace, interface, since, until,
            )
            if event:
                result.append(event)
        buffer = []

    for line_number, record in records:
        kind = record.get("type")
        if kind in {"session.start", "assistant.turn_start"}:
            continue
        if kind == "assistant.turn_end":
            data = record.get("data") if isinstance(record.get("data"), dict) else {}
            flush(str(data.get("turnId") or ""))
            continue
        if kind in _TRANSCRIPT_EVENTS:
            buffer.append((line_number, record))
    return result


def _transcript_event(
    record: dict[str, Any],
    data: dict[str, Any],
    line_number: int,
    session_id: str,
    turn_id: str,
    workspace: str,
    interface: str,
    since: datetime | None,
    until: datetime | None,
) -> Event | None:
    kind = str(record.get("type") or "")
    role, event_kind = _TRANSCRIPT_EVENTS[kind]
    timestamp = record.get("timestamp")
    if not in_window(timestamp, since, until):
        return None
    common = dict(
        source="copilot-vscode",
        interface=interface,
        session_id=session_id,
        turn_id=turn_id,
        event_id=str(record.get("id") or line_number),
        timestamp=iso_timestamp(timestamp),
        workspace=workspace,
        completed=True,
        source_metadata={"line": line_number},
    )
    if kind in {"user.message", "assistant.message"}:
        text = text_content(data.get("content"))
        if not text:
            return None
        return Event(**common, role=role, event_kind=event_kind, text=text)
    if kind == "tool.execution_start":
        return Event(
            **common,
            role=role,
            event_kind=event_kind,
            tool_name=str(data.get("toolName") or data.get("name") or ""),
            tool_input=json_value(data.get("arguments")),
        )
    return Event(
        **common,
        role=role,
        event_kind=event_kind,
        tool_result=data.get("result", data.get("error", data.get("success"))),
    )

from __future__ import annotations

import copy
import json
from datetime import datetime
from pathlib import Path
from typing import Any

from ..content import text_content
from ..model import Event, SourceFailure, SourceReport
from ..time import in_window, iso_timestamp
from .common import read_jsonl


def collect_vscode(root: Path, since: datetime | None, until: datetime | None) -> SourceReport:
    files = sorted(root.glob("workspaceStorage/*/chatSessions/*.jsonl"))
    files += sorted(root.glob("globalStorage/emptyWindowChatSessions/*.jsonl"))
    if not root.exists() or not files:
        return SourceReport("copilot-vscode", available=False)
    events: list[Event] = []
    failures: list[SourceFailure] = []
    for path in files:
        try:
            events.extend(_read_session(path, since, until))
        except (OSError, ValueError, TypeError, json.JSONDecodeError) as exc:
            failures.append(SourceFailure("copilot-vscode", str(path), str(exc)))
    return SourceReport("copilot-vscode", available=True, events=tuple(events), failures=tuple(failures))


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
    workspace_json = path.parent.parent / "workspace.json"
    if not workspace_json.exists():
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

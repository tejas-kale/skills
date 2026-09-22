from __future__ import annotations

import json
import sqlite3
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from ..content import text_content
from ..model import Event, SourceFailure, SourceReport
from ..time import in_window, iso_timestamp


def collect_cursor(root: Path, since: datetime | None, until: datetime | None) -> SourceReport:
    chat_files = sorted(root.glob("chats/*/*/store.db"))
    acp_files = sorted(root.glob("acp-sessions/*/store.db"))
    files = chat_files + acp_files
    if not root.exists() or not files:
        return SourceReport("cursor-cli", available=False)
    events: list[Event] = []
    failures: list[SourceFailure] = []
    for path in files:
        try:
            events.extend(_read_session(path, since, until))
        except (OSError, ValueError, sqlite3.Error, json.JSONDecodeError) as exc:
            failures.append(SourceFailure("cursor-cli", str(path), str(exc)))
    return SourceReport("cursor-cli", available=True, events=tuple(events), failures=tuple(failures))


def _metadata(path: Path) -> dict[str, Any]:
    meta_path = path.parent / "meta.json"
    if not meta_path.exists():
        return {}
    value = json.loads(meta_path.read_text(encoding="utf-8"))
    return value if isinstance(value, dict) else {}


def _message_rows(path: Path) -> list[tuple[int, str, dict[str, Any]]]:
    rows: list[tuple[Any, ...]] | None = None
    error: sqlite3.Error | None = None
    for option in ("mode=ro", "immutable=1"):
        connection: sqlite3.Connection | None = None
        try:
            connection = sqlite3.connect(f"file:{path}?{option}", uri=True)
            rows = connection.execute("SELECT rowid, id, data FROM blobs ORDER BY rowid").fetchall()
            break
        except sqlite3.Error as exc:
            error = exc
        finally:
            if connection is not None:
                connection.close()
    if rows is None:
        raise error or sqlite3.OperationalError(f"Unable to read {path}")
    messages: list[tuple[int, str, dict[str, Any]]] = []
    for rowid, blob_id, data in rows:
        raw = bytes(data) if isinstance(data, memoryview) else data
        if isinstance(raw, bytes):
            if not raw.startswith(b"{"):
                continue
            raw = raw.decode("utf-8")
        if not isinstance(raw, str) or not raw.startswith("{"):
            continue
        value = json.loads(raw)
        if isinstance(value, dict) and value.get("role") in {"user", "assistant", "tool"}:
            messages.append((int(rowid), str(blob_id), value))
    return messages


def _read_session(path: Path, since: datetime | None, until: datetime | None) -> list[Event]:
    meta = _metadata(path)
    session_id = str(meta.get("agentId") or path.parent.name)
    workspace = str(meta.get("cwd") or "")
    timestamp_value = meta.get("updatedAtMs") or path.stat().st_mtime
    if not in_window(timestamp_value, since, until):
        return []
    timestamp = iso_timestamp(timestamp_value)
    interface = "cursor-acp" if "acp-sessions" in path.parts else "cursor-cli"
    messages = _message_rows(path)
    turn_number = 0
    current_turn = ""
    grouped: dict[str, list[tuple[int, str, dict[str, Any]]]] = {}
    completed: set[str] = set()
    for rowid, blob_id, message in messages:
        role = message.get("role")
        if role == "user" and text_content(message.get("content")):
            turn_number += 1
            current_turn = f"turn-{turn_number}"
        if not current_turn:
            continue
        grouped.setdefault(current_turn, []).append((rowid, blob_id, message))
        if role == "assistant" and text_content(message.get("content")):
            completed.add(current_turn)

    result: list[Event] = []
    for turn_id, rows in grouped.items():
        if turn_id not in completed:
            continue
        for rowid, blob_id, message in rows:
            role = str(message.get("role"))
            content = message.get("content")
            common = dict(
                source="cursor-cli",
                interface=interface,
                session_id=session_id,
                turn_id=turn_id,
                timestamp=timestamp,
                workspace=workspace,
                completed=True,
                source_metadata={"rowid": rowid},
            )
            text = text_content(content)
            if role in {"user", "assistant"} and text:
                result.append(Event(
                    **common,
                    event_id=blob_id,
                    role=role,
                    event_kind="message",
                    text=text,
                ))
            if isinstance(content, list):
                for index, item in enumerate(content):
                    if not isinstance(item, dict):
                        continue
                    item_type = item.get("type")
                    if item_type in {"tool-call", "tool_use"}:
                        result.append(Event(
                            **common,
                            event_id=str(item.get("toolCallId") or item.get("id") or f"{blob_id}-{index}"),
                            role="assistant",
                            event_kind="tool_call",
                            tool_name=str(item.get("toolName") or item.get("name") or ""),
                            tool_input=item.get("input", item.get("args")),
                        ))
                    elif role == "tool" or item_type in {"tool-result", "tool_result"}:
                        result.append(Event(
                            **common,
                            event_id=str(item.get("toolCallId") or item.get("tool_use_id") or f"{blob_id}-{index}"),
                            role="tool",
                            event_kind="tool_result",
                            tool_result=item.get("output", item.get("content", item.get("result"))),
                        ))
    return result

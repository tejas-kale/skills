from __future__ import annotations

import json
import sqlite3
from pathlib import Path

import pytest


@pytest.fixture
def fixtures() -> Path:
    return Path(__file__).parent / "fixtures"


@pytest.fixture
def cursor_root(tmp_path: Path, fixtures: Path) -> Path:
    session = tmp_path / "cursor" / "chats" / "workspace" / "cursor-session"
    session.mkdir(parents=True)
    (session / "meta.json").write_text(json.dumps({
        "schemaVersion": 1,
        "createdAtMs": 1790074800000,
        "updatedAtMs": 1790074860000,
        "hasConversation": True,
        "cwd": "/work/project",
    }), encoding="utf-8")
    messages = json.loads((fixtures / "cursor" / "messages.json").read_text(encoding="utf-8"))
    connection = sqlite3.connect(session / "store.db")
    connection.execute("CREATE TABLE blobs (id TEXT PRIMARY KEY, data BLOB)")
    connection.execute("CREATE TABLE meta (key TEXT PRIMARY KEY, value TEXT)")
    for index, message in enumerate(messages):
        connection.execute(
            "INSERT INTO blobs (id, data) VALUES (?, ?)",
            (f"blob-{index}", json.dumps(message).encode()),
        )
    connection.commit()
    connection.close()
    return tmp_path / "cursor"

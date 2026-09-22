from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass(frozen=True, slots=True)
class Event:
    source: str
    interface: str
    session_id: str
    turn_id: str
    event_id: str
    timestamp: str
    workspace: str
    role: str
    event_kind: str
    text: str = ""
    tool_name: str = ""
    tool_input: Any = None
    tool_result: Any = None
    completed: bool = True
    source_metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class SourceFailure:
    source: str
    path: str
    message: str


@dataclass(frozen=True, slots=True)
class SourceReport:
    source: str
    available: bool
    events: tuple[Event, ...] = ()
    failures: tuple[SourceFailure, ...] = ()

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Iterable

from ..model import Event, SourceFailure, SourceReport


def read_jsonl(path: Path) -> Iterable[tuple[int, dict[str, Any]]]:
    with path.open(encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, 1):
            if not line.strip():
                continue
            value = json.loads(line)
            if isinstance(value, dict):
                yield line_number, value


def existing_roots(paths: Iterable[Path]) -> list[Path]:
    return [path for path in paths if path.exists()]


def collect_files(
    source: str,
    files: list[Path],
    reader: Callable[[Path, datetime | None, datetime | None], list[Event]],
    since: datetime | None,
    until: datetime | None,
    errors: tuple[type[BaseException], ...] = (OSError, ValueError, TypeError),
) -> SourceReport:
    """Run a source reader while isolating malformed sessions."""
    if not files:
        return SourceReport(source, available=False)
    events: list[Event] = []
    failures: list[SourceFailure] = []
    for path in files:
        try:
            events.extend(reader(path, since, until))
        except errors as exc:
            failures.append(SourceFailure(source, str(path), str(exc)))
    return SourceReport(source, available=True, events=tuple(events), failures=tuple(failures))

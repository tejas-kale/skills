from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Iterable


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

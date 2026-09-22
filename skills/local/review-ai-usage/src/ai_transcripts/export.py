from __future__ import annotations

import re
from datetime import datetime
from pathlib import Path

from .time import parse_timestamp

HEADING = re.compile(r"^(?P<stars>\*+)\s+(?P<title>.*?)\s+(?P<tags>:(?:[^:\s]+:)+)\s*$")
PROPERTY = re.compile(r"^:(?P<key>[A-Z_]+):\s*(?P<value>.*)$")


def confirmed_lessons(casebook: Path, since: datetime | None = None) -> list[str]:
    lines = casebook.read_text(encoding="utf-8").splitlines()
    exported: list[str] = []
    index = 0
    while index < len(lines):
        match = HEADING.match(lines[index])
        if not match or "LESSON" not in match.group("tags").split(":") or "CONFIRMED" not in match.group("tags").split(":"):
            index += 1
            continue
        level = len(match.group("stars"))
        title = match.group("title").strip()
        properties: dict[str, str] = {}
        body: list[str] = []
        index += 1
        while index < len(lines):
            next_heading = HEADING.match(lines[index])
            if next_heading and len(next_heading.group("stars")) <= level:
                break
            property_match = PROPERTY.match(lines[index])
            if property_match:
                properties[property_match.group("key")] = property_match.group("value")
            elif lines[index].strip() and not lines[index].startswith(":"):
                body.append(_strip_local_links(lines[index]))
            index += 1
        confirmed = properties.get("CONFIRMED") or properties.get("DATE") or ""
        if since and confirmed:
            parsed = parse_timestamp(confirmed)
            if parsed and parsed < since:
                continue
        exported.extend([
            f"* {title} :LESSON:CONFIRMED:",
            ":PROPERTIES:",
            f":MACHINE: {properties.get('MACHINE', 'unknown')}",
            f":CONFIRMED: {confirmed}",
            f":EVIDENCE_COUNT: {properties.get('EVIDENCE_COUNT', 'unknown')}",
            ":END:",
        ])
        exported.extend(line for line in body if not _sensitive_property(line))
        exported.append("")
    return exported


def _strip_local_links(line: str) -> str:
    return re.sub(r"\[\[(?:file:)?/[^]]+\](?:\[([^]]+)\])?\]", lambda match: match.group(1) or "local case", line)


def _sensitive_property(line: str) -> bool:
    upper = line.upper()
    return any(token in upper for token in ("SESSION_ID", "TURN_ID", "RUN_ID", "TRANSCRIPT"))

from __future__ import annotations

import re
from datetime import datetime
from pathlib import Path

from .time import parse_timestamp

HEADING = re.compile(r"^(?P<stars>\*+)\s+(?P<title>.*?)\s+(?P<tags>:(?:[^:\s]+:)+)\s*$")
PROPERTY = re.compile(r"^:(?P<key>[A-Z_]+):\s*(?P<value>.*)$")
ORG_LINK = re.compile(r"\[\[(?:file:)?([^\[\]\n]+)\](?:\[([^\[\]\n]+)\])?\]")
URL = re.compile(r"\b(?:https?|file)://\S+|\bwww\.\S+", re.IGNORECASE)
EMAIL = re.compile(r"\b[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}\b")
SECRET = re.compile(
    r"(?i)\b(?:api[_-]?key|token|secret|password|authorization)\b\s*[:=]\s*\S+|\bbearer\s+[A-Za-z0-9._\-]{8,}"
)
IDENTIFIER = re.compile(
    r"\b[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}\b"
    r"|\b[A-Za-z0-9+/]{32,}={0,2}\b"
)
PATH = re.compile(r"(?<![\w~])~?(?:/[\w.@+-]+)+")
PLACEHOLDER = re.compile(r"\[(?:url|email|secret|path)\]")
QUOTED_EXCERPT = re.compile(r"""^["'][^"']{20,}["']$""")


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
        in_excerpt = False
        index += 1
        while index < len(lines):
            next_heading = HEADING.match(lines[index])
            if next_heading and len(next_heading.group("stars")) <= level:
                break
            property_match = PROPERTY.match(lines[index])
            stripped = lines[index].strip()
            if property_match:
                properties[property_match.group("key")] = property_match.group("value")
            elif _excerpt_boundary(stripped, in_excerpt):
                in_excerpt = not in_excerpt
            elif in_excerpt or stripped.startswith(">") or QUOTED_EXCERPT.fullmatch(stripped):
                pass
            elif stripped and not stripped.startswith(":"):
                redacted = _redact_line(lines[index])
                if _lesson_text(redacted) and not _sensitive_property(redacted):
                    body.append(redacted)
            index += 1
        confirmed = properties.get("CONFIRMED") or properties.get("DATE") or ""
        if since and confirmed:
            parsed = parse_timestamp(confirmed)
            if parsed and parsed < since:
                continue
        exported.extend([
            f"* {_redact_line(title)} :LESSON:CONFIRMED:",
            ":PROPERTIES:",
            f":MACHINE: {properties.get('MACHINE', 'unknown')}",
            f":CONFIRMED: {confirmed}",
            f":EVIDENCE_COUNT: {properties.get('EVIDENCE_COUNT', 'unknown')}",
            ":END:",
        ])
        exported.extend(body)
        exported.append("")
    return exported


def _excerpt_boundary(stripped: str, in_excerpt: bool) -> bool:
    upper = stripped.upper()
    if stripped.startswith("```"):
        return True
    if upper.startswith("#+BEGIN_"):
        return not in_excerpt
    return in_excerpt and upper.startswith("#+END_")


def _redact_line(line: str) -> str:
    line = ORG_LINK.sub(lambda match: _link_label(match.group(2), match.group(1)), line)
    line = URL.sub("[url]", line)
    line = EMAIL.sub("[email]", line)
    line = SECRET.sub("[secret]", line)
    line = IDENTIFIER.sub("[secret]", line)
    line = PATH.sub("[path]", line)
    return line


def _link_label(label: str | None, target: str) -> str:
    if label and not _sensitive_property(label):
        return label
    if target.startswith(("http://", "https://", "file:", "/", ".", "~")):
        return "local case"
    return label or "local case"


def _lesson_text(line: str) -> bool:
    return bool(PLACEHOLDER.sub("", line).strip())


def _sensitive_property(line: str) -> bool:
    upper = line.upper()
    return any(token in upper for token in ("SESSION_ID", "TURN_ID", "RUN_ID", "TRANSCRIPT"))

from __future__ import annotations

import re
from datetime import UTC, datetime, timedelta


def parse_boundary(value: str | None, *, now: datetime | None = None) -> datetime | None:
    if value is None:
        return None
    current = now or datetime.now(UTC)
    match = re.fullmatch(r"(\d+)([hdw])", value)
    if match:
        amount = int(match.group(1))
        units = {"h": "hours", "d": "days", "w": "weeks"}
        return current - timedelta(**{units[match.group(2)]: amount})
    normalised = value.replace("Z", "+00:00")
    parsed = datetime.fromisoformat(normalised)
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=UTC)
    return parsed.astimezone(UTC)


def parse_timestamp(value: str | int | float | None) -> datetime | None:
    if value is None or value == "":
        return None
    if isinstance(value, (int, float)):
        seconds = value / 1000 if value > 10_000_000_000 else value
        return datetime.fromtimestamp(seconds, UTC)
    try:
        return parse_boundary(str(value))
    except (TypeError, ValueError, OverflowError):
        return None


def in_window(timestamp: str | int | float | None, since: datetime | None, until: datetime | None) -> bool:
    parsed = parse_timestamp(timestamp)
    if parsed is None:
        return since is None and until is None
    return (since is None or parsed >= since) and (until is None or parsed <= until)


def iso_timestamp(value: str | int | float | None) -> str:
    parsed = parse_timestamp(value)
    return parsed.isoformat().replace("+00:00", "Z") if parsed else ""

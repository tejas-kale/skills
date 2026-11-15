#!/usr/bin/env python3
"""Weekly numbers from Claude Code session logs: when the user typed, never what.

Usage: session_stats.py --since YYYY-MM-DD --until YYYY-MM-DD --tz <IANA zone> --bedtime HH:MM [--root DIR]

Reads <root>/*/*.jsonl (default root: ~/.claude/projects). From each line it takes the timestamp,
the working directory's last path segment and whether the line is a prompt the user typed in an
interactive session (headless `sdk` runs are skipped). It prints counts, project names and clock
times only.

A day runs from 04:00 to 04:00 local time, so a prompt at 01:15 belongs to the evening before.
"Past bedtime" counts prompts from the bedtime until that 04:00.
"""

import argparse
import json
import sys
from collections import defaultdict
from datetime import date, datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

DAY_START_HOUR = 4
PARALLEL_WINDOW_MINUTES = 30


def typed_prompts(path):
    """Yield (utc datetime, project name) for each prompt the user typed in one session log."""
    project = None
    with path.open(encoding="utf-8", errors="replace") as lines:
        for line in lines:
            try:
                entry = json.loads(line)
            except ValueError:
                continue
            if not isinstance(entry, dict) or entry.get("type") != "user" or "timestamp" not in entry:
                continue
            if entry.get("isMeta") or entry.get("isSidechain"):
                continue
            if str(entry.get("entrypoint", "")).startswith("sdk"):
                continue  # headless run started by a script or another agent
            message = entry.get("message")
            if not isinstance(message, dict) or not isinstance(message.get("content"), str):
                continue  # tool results and attachments arrive as lists; typed prompts as text
            try:
                when = datetime.fromisoformat(entry["timestamp"].replace("Z", "+00:00"))
            except (AttributeError, ValueError):
                continue
            # The session's first working directory names the project; later moves stay inside it.
            project = project or Path(entry.get("cwd") or path.parent.name).name
            yield when, project


def day_of(local):
    """The date whose 04:00-to-04:00 day holds this local time."""
    return (local - timedelta(hours=DAY_START_HOUR)).date()


def minutes_into_day(local):
    return ((local.hour - DAY_START_HOUR) % 24) * 60 + local.minute


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--since", required=True, type=date.fromisoformat)
    parser.add_argument("--until", required=True, type=date.fromisoformat)
    parser.add_argument("--tz", required=True)
    parser.add_argument("--bedtime", required=True)
    parser.add_argument("--root", type=Path, default=Path.home() / ".claude" / "projects")
    args = parser.parse_args(argv)

    zone = ZoneInfo(args.tz)
    bed_hour, bed_minute = (int(part) for part in args.bedtime.split(":"))
    bedtime_minutes = ((bed_hour - DAY_START_HOUR) % 24) * 60 + bed_minute

    days = defaultdict(list)  # date -> [(local datetime, project, session)]
    for path in sorted(args.root.glob("*/*.jsonl")):
        for when, project in typed_prompts(path):
            local = when.astimezone(zone)
            days[day_of(local)].append((local, project, path.stem))

    print(f"Session-log numbers, {args.since} to {args.until} ({args.tz}, bedtime {args.bedtime}, day starts 04:00)")
    print()
    print("| Day | Prompts | Projects | Sessions | Max parallel | Past bedtime | Last prompt |")
    print("|---|---|---|---|---|---|---|")
    total = late_days = most_parallel = 0
    all_projects = set()
    day = args.since
    while day <= args.until:
        prompts = sorted(days.get(day, []))
        projects = sorted({project for _, project, _ in prompts})
        sessions = {session for _, _, session in prompts}
        half_hours = defaultdict(set)  # half-hour slot -> sessions with a prompt in it
        for local, _, session in prompts:
            half_hours[minutes_into_day(local) // PARALLEL_WINDOW_MINUTES].add(session)
        parallel = max((len(active) for active in half_hours.values()), default=0)
        late = sum(1 for local, _, _ in prompts if minutes_into_day(local) >= bedtime_minutes)
        last = prompts[-1][0].strftime("%H:%M") if prompts else "-"
        project_cell = f"{len(projects)}: {', '.join(projects)}" if projects else "0"
        print(f"| {day:%a %Y-%m-%d} | {len(prompts)} | {project_cell} | {len(sessions)} | {parallel} | {late} | {last} |")
        total += len(prompts)
        late_days += 1 if late else 0
        most_parallel = max(most_parallel, parallel)
        all_projects.update(projects)
        day += timedelta(days=1)

    span = (args.until - args.since).days + 1
    names = f" ({', '.join(sorted(all_projects))})" if all_projects else ""
    print()
    print(
        f"Week: {total} prompts; {late_days} days with prompts past bedtime out of {span}; "
        f"{len(all_projects)} projects{names}; max parallel sessions {most_parallel}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())

"""Tests for session_stats.py, through its command line: a folder of session logs in, a report out."""

import json
import subprocess
import sys
from pathlib import Path

SCRIPT = Path(__file__).with_name("session_stats.py")


def prompt(ts, cwd="/Users/someone/Code/alpha", text="hello", **extra):
    return {"type": "user", "timestamp": ts, "cwd": cwd, "message": {"role": "user", "content": text}, **extra}


def write_session(root, project_dir, session, lines):
    d = root / project_dir
    d.mkdir(parents=True, exist_ok=True)
    (d / f"{session}.jsonl").write_text("".join(json.dumps(line) + "\n" for line in lines))


def report(root, *args):
    cmd = [sys.executable, str(SCRIPT), "--root", str(root), "--tz", "Europe/Berlin", "--bedtime", "23:00", *args]
    done = subprocess.run(cmd, capture_output=True, text=True)
    assert done.returncode == 0, done.stderr
    return done.stdout


def row(out, day):
    rows = [line for line in out.splitlines() if line.startswith(f"| {day} ")]
    assert len(rows) == 1, out
    return [cell.strip() for cell in rows[0].strip("|").split("|")]


def test_prompt_after_bedtime_counts_for_the_evening_it_belongs_to(tmp_path):
    # 21:00Z is 22:00 in Berlin (before bedtime); 22:30Z is 23:30; 00:15Z next day is 01:15, same evening.
    write_session(tmp_path, "-proj-alpha", "s1", [
        prompt("2026-11-10T21:00:00.000Z"),
        prompt("2026-11-10T22:30:00.000Z"),
        prompt("2026-11-11T00:15:00.000Z"),
    ])
    out = report(tmp_path, "--since", "2026-11-10", "--until", "2026-11-10")
    day, prompts, projects, sessions, parallel, late, last = row(out, "Tue 2026-11-10")
    assert prompts == "3"
    assert late == "2"
    assert last == "01:15"


def test_only_prompts_the_user_typed_are_counted_and_no_text_is_printed(tmp_path):
    tool_result = {"type": "user", "timestamp": "2026-11-10T10:01:00.000Z", "cwd": "/Users/someone/Code/alpha",
                   "message": {"role": "user", "content": [{"type": "tool_result", "content": "SECRET-TOOL-OUTPUT"}]}}
    write_session(tmp_path, "-proj-alpha", "s1", [
        prompt("2026-11-10T10:00:00.000Z", text="SECRET-PROMPT-TEXT"),
        tool_result,
        prompt("2026-11-10T10:02:00.000Z", text="SECRET-META-TEXT", isMeta=True),
        prompt("2026-11-10T10:03:00.000Z", text="SECRET-SUBAGENT-TEXT", isSidechain=True),
        {"type": "assistant", "timestamp": "2026-11-10T10:04:00.000Z", "message": {"content": "SECRET-REPLY"}},
        "not a json object",
    ])
    out = report(tmp_path, "--since", "2026-11-10", "--until", "2026-11-10")
    assert row(out, "Tue 2026-11-10")[1] == "1"
    assert "SECRET" not in out


def test_projects_sessions_and_parallel_sessions_per_day(tmp_path):
    # Berlin is UTC+1 in November. Sessions a1 and b1 both have a prompt between 10:00 and 10:30 local;
    # a2 is alone at 15:00. Two projects, three sessions, at most two sessions in one half hour.
    write_session(tmp_path, "-proj-alpha", "a1", [prompt("2026-11-10T09:05:00.000Z"), prompt("2026-11-10T09:20:00.000Z")])
    write_session(tmp_path, "-proj-alpha", "a2", [prompt("2026-11-10T14:00:00.000Z")])
    write_session(tmp_path, "-proj-beta", "b1", [prompt("2026-11-10T09:25:00.000Z", cwd="/Users/someone/Code/beta")])
    out = report(tmp_path, "--since", "2026-11-10", "--until", "2026-11-10")
    day, prompts, projects, sessions, parallel, late, last = row(out, "Tue 2026-11-10")
    assert projects == "2: alpha, beta"
    assert sessions == "3"
    assert parallel == "2"


def test_week_summary_counts_late_nights_and_ignores_days_outside_the_window(tmp_path):
    write_session(tmp_path, "-proj-alpha", "a1", [
        prompt("2026-11-08T12:00:00.000Z"),   # Sunday, before the window
        prompt("2026-11-09T22:30:00.000Z"),   # Monday 23:30, late
        prompt("2026-11-11T12:00:00.000Z"),   # Wednesday 13:00
    ])
    write_session(tmp_path, "-proj-beta", "b1", [
        prompt("2026-11-11T23:10:00.000Z", cwd="/Users/someone/Code/beta"),  # Thursday 00:10, Wednesday's evening, late
        prompt("2026-11-16T12:00:00.000Z", cwd="/Users/someone/Code/beta"),  # Monday after the window
    ])
    out = report(tmp_path, "--since", "2026-11-09", "--until", "2026-11-15")
    assert row(out, "Tue 2026-11-10")[1:] == ["0", "0", "0", "0", "0", "-"]
    assert "| Sun 2026-11-08 " not in out and "| Mon 2026-11-16 " not in out
    assert "Week: 3 prompts; 2 days with prompts past bedtime out of 7; 2 projects (alpha, beta); max parallel sessions 1" in out


def test_a_session_counts_as_one_project_even_when_its_working_directory_moves(tmp_path):
    write_session(tmp_path, "-proj-alpha", "a1", [
        prompt("2026-11-10T09:00:00.000Z", cwd="/Users/someone/Code/alpha"),
        prompt("2026-11-10T09:10:00.000Z", cwd="/Users/someone/Code/alpha/docs/notes"),
    ])
    out = report(tmp_path, "--since", "2026-11-10", "--until", "2026-11-10")
    assert row(out, "Tue 2026-11-10")[2] == "1: alpha"


def test_headless_runs_started_by_scripts_are_not_the_user_typing(tmp_path):
    write_session(tmp_path, "-proj-alpha", "a1", [prompt("2026-11-10T09:00:00.000Z", entrypoint="cli")])
    write_session(tmp_path, "-proj-alpha", "auto", [prompt("2026-11-10T23:30:00.000Z", entrypoint="sdk-cli")])
    out = report(tmp_path, "--since", "2026-11-10", "--until", "2026-11-10")
    day, prompts, projects, sessions, parallel, late, last = row(out, "Tue 2026-11-10")
    assert (prompts, sessions, late) == ("1", "1", "0")

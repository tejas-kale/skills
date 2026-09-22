from __future__ import annotations

import json
import shutil
from pathlib import Path

from click.testing import CliRunner

from ai_transcripts.cli import _filtered_events, main
from ai_transcripts.config import Config
from ai_transcripts.model import Event, SourceReport


def write_config(path: Path, casebook: Path, sources: dict[str, Path]) -> None:
    source_lines = "\n".join(f'{json.dumps(name)} = {json.dumps(str(value))}' for name, value in sources.items())
    path.write_text(
        f'machine = "personal"\ncasebook = {json.dumps(str(casebook))}\n'
        f'state_path = {json.dumps(str(path.parent / "state.json"))}\n'
        f'enabled_sources = {json.dumps(list(sources))}\nexcluded_workspaces = []\n\n'
        f'[source_paths]\n{source_lines}\n',
        encoding="utf-8",
    )


def test_collect_outputs_healthy_source_when_another_source_fails(tmp_path: Path, fixtures: Path) -> None:
    codex = tmp_path / "codex" / "sessions" / "2026" / "09" / "22"
    codex.mkdir(parents=True)
    shutil.copy(fixtures / "codex" / "session.jsonl", codex / "session.jsonl")
    claude = tmp_path / "claude" / "projects" / "broken"
    claude.mkdir(parents=True)
    (claude / "broken.jsonl").write_text("not json\n", encoding="utf-8")
    config = tmp_path / "config.toml"
    write_config(config, tmp_path / "casebook.org", {"codex": tmp_path / "codex", "claude-code": tmp_path / "claude"})

    result = CliRunner().invoke(main, [
        "collect", "--config", str(config), "--since", "2026-09-22", "--until", "2026-09-23",
    ])

    assert result.exit_code == 2
    records = [json.loads(line) for line in result.stdout.splitlines()]
    assert records
    assert {record["source"] for record in records} == {"codex"}
    assert "ERROR claude-code" in result.stderr
    assert "OK codex" in result.stderr


def test_excluded_workspace_is_not_emitted(tmp_path: Path, fixtures: Path) -> None:
    codex = tmp_path / "codex" / "sessions" / "2026" / "09" / "22"
    codex.mkdir(parents=True)
    shutil.copy(fixtures / "codex" / "session.jsonl", codex / "session.jsonl")
    config = tmp_path / "config.toml"
    write_config(config, tmp_path / "casebook.org", {"codex": tmp_path / "codex"})
    text = config.read_text(encoding="utf-8").replace("excluded_workspaces = []", 'excluded_workspaces = ["/work"]')
    config.write_text(text, encoding="utf-8")

    result = CliRunner().invoke(main, [
        "collect", "--config", str(config), "--since", "2026-09-22", "--until", "2026-09-23",
    ])

    assert result.exit_code == 0
    assert result.stdout == ""


def test_init_creates_local_config_and_state(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv("XDG_STATE_HOME", str(tmp_path / "state-home"))
    config = tmp_path / "config" / "config.toml"
    casebook = tmp_path / "usage.org"

    result = CliRunner().invoke(main, [
        "init", "--machine", "personal", "--casebook", str(casebook), "--config", str(config),
    ])

    assert result.exit_code == 0
    assert config.exists()
    state = tmp_path / "state-home" / "ai-transcript-review" / "state.json"
    state_value = json.loads(state.read_text(encoding="utf-8"))
    assert state_value["version"] == 1
    assert state_value["machine"] == "personal"


def test_export_learnings_omits_pending_and_local_links(tmp_path: Path) -> None:
    casebook = tmp_path / "usage.org"
    casebook.write_text(
        "* Review :AI_REVIEW:COMPLETE:\n"
        "** Keep verification bounded :LESSON:CONFIRMED:\n"
        ":PROPERTIES:\n:MACHINE: personal\n:CONFIRMED: 2026-09-22\n:EVIDENCE_COUNT: 3\n:SESSION_ID: secret\n:END:\n"
        "Use [[/private/work/case.org][the supporting case]].\n"
        "** Unconfirmed lesson :LESSON:PENDING:\nPending text.\n",
        encoding="utf-8",
    )

    result = CliRunner().invoke(main, ["export-learnings", "--casebook", str(casebook)])

    assert result.exit_code == 0
    assert "Keep verification bounded" in result.stdout
    assert "supporting case" in result.stdout
    assert "/private/work" not in result.stdout
    assert "SESSION_ID" not in result.stdout
    assert "Unconfirmed lesson" not in result.stdout


def test_deduplication_is_scoped_to_a_session(tmp_path: Path) -> None:
    def event(session_id: str, event_kind: str = "message") -> Event:
        return Event(
            source="cursor-cli",
            interface="cursor-cli",
            session_id=session_id,
            turn_id="turn-1",
            event_id="message-1",
            timestamp="2026-09-22T10:00:00Z",
            workspace="/work/project",
            role="assistant",
            event_kind=event_kind,
            text="Complete.",
        )

    config = Config("personal", tmp_path / "casebook.org", (), (), {}, tmp_path / "state.json")
    report = SourceReport(
        "cursor-cli",
        available=True,
        events=(event("one"), event("two"), event("one", "tool_result")),
    )

    assert len(_filtered_events([report], config)) == 3

from __future__ import annotations

import json
import os
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

import click

from .config import SOURCE_NAMES, Config, default_config_path, load_config, write_config
from .export import confirmed_lessons
from .model import Event, SourceReport
from .sources import COLLECTORS
from .time import parse_boundary


@click.group()
def main() -> None:
    """Read local AI-agent transcripts without modifying their stores."""


@main.command("init")
@click.option("--machine", required=True, type=click.Choice(["personal", "work"]))
@click.option("--casebook", required=True, type=click.Path(path_type=Path))
@click.option(
    "--source-path", "source_paths", multiple=True, nargs=2,
    type=(click.Choice(SOURCE_NAMES), click.Path(path_type=Path)),
    help="Override a source path; may be repeated.",
)
@click.option(
    "--exclude-workspace", "excluded_workspaces", multiple=True,
    help="Exclude a workspace prefix; may be repeated.",
)
@click.option("--config", "config_path", type=click.Path(path_type=Path), default=default_config_path, show_default=True)
def initialise(
    machine: str,
    casebook: Path,
    source_paths: tuple[tuple[str, Path], ...],
    excluded_workspaces: tuple[str, ...],
    config_path: Path,
) -> None:
    """Create machine-local configuration and state."""
    if config_path.exists():
        raise click.ClickException(f"Configuration already exists: {config_path}")
    config = write_config(
        config_path,
        machine=machine,
        casebook=casebook,
        source_paths=dict(source_paths),
        excluded_workspaces=excluded_workspaces,
    )
    click.echo(f"Configuration: {config_path}")
    click.echo(f"State: {config.state_path}")
    detected = [name for name in config.enabled_sources if config.source_paths[name].exists()]
    click.echo("Detected sources: " + (", ".join(detected) if detected else "none"))


@main.command("config")
@click.option("--config", "config_path", type=click.Path(path_type=Path), default=default_config_path, show_default=True)
def show_config(config_path: Path) -> None:
    """Show resolved local configuration without transcript content."""
    if not config_path.exists():
        raise click.ClickException(f"Configuration not found: {config_path}")
    config = load_config(config_path)
    click.echo(json.dumps({
        "machine": config.machine,
        "casebook": str(config.casebook),
        "state_path": str(config.state_path),
        "enabled_sources": list(config.enabled_sources),
        "excluded_workspaces": list(config.excluded_workspaces),
        "source_paths": {name: str(path) for name, path in config.source_paths.items()},
    }, indent=2, sort_keys=True))


@main.command("collect")
@click.option("--since", help="ISO timestamp/date or relative duration such as 24h.")
@click.option("--until", help="ISO timestamp/date or relative duration.")
@click.option("--source", "sources", multiple=True, type=click.Choice(SOURCE_NAMES))
@click.option("--format", "output_format", type=click.Choice(["jsonl"]), default="jsonl", show_default=True)
@click.option("--output", type=click.Path(path_type=Path), help="Persist JSONL explicitly instead of writing it to stdout.")
@click.option("--config", "config_path", type=click.Path(path_type=Path), default=default_config_path, show_default=True)
def collect(since: str | None, until: str | None, sources: tuple[str, ...], output_format: str, output: Path | None, config_path: Path) -> None:
    """Emit normalised events from completed turns."""
    del output_format
    if not config_path.exists():
        raise click.ClickException(f"Configuration not found: {config_path}")
    config = load_config(config_path)
    now = datetime.now(UTC)
    since_value = parse_boundary(since, now=now) if since else now - timedelta(hours=24)
    until_value = parse_boundary(until, now=now) if until else now
    if since_value and until_value and since_value > until_value:
        raise click.ClickException("--since must not be later than --until")
    selected = sources or config.enabled_sources
    unknown = [name for name in selected if name not in COLLECTORS]
    if unknown:
        raise click.ClickException(f"Unknown source: {', '.join(unknown)}")

    reports = [COLLECTORS[name](config.source_paths[name], since_value, until_value) for name in selected]
    events = _filtered_events(reports, config)
    rendered = "".join(json.dumps(event.to_dict(), ensure_ascii=False, sort_keys=True) + "\n" for event in events)
    if output:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(rendered, encoding="utf-8")
    else:
        click.echo(rendered, nl=False)

    failures = 0
    for report in reports:
        if not report.available:
            click.echo(f"INFO {report.source}: unavailable", err=True)
        elif report.failures:
            failures += len(report.failures)
            for failure in report.failures:
                click.echo(f"ERROR {report.source}: {failure.path}: {failure.message}", err=True)
        else:
            click.echo(f"OK {report.source}: {len(report.events)} events", err=True)
    if failures:
        raise click.exceptions.Exit(2)


def _filtered_events(reports: list[SourceReport], config: Config) -> list[Event]:
    excluded = tuple(os.path.normpath(str(Path(value).expanduser())) for value in config.excluded_workspaces)
    seen: set[tuple[str, str, str, str]] = set()
    result: list[Event] = []
    for report in reports:
        for event in report.events:
            if _workspace_excluded(event.workspace, excluded):
                continue
            source = "copilot" if event.source in {"copilot", "copilot-vscode"} else event.source
            identity = (source, event.session_id, event.event_kind, event.event_id)
            if identity in seen:
                continue
            seen.add(identity)
            result.append(event)
    return sorted(result, key=lambda event: (event.timestamp, event.source, event.session_id, event.event_id))


def _workspace_excluded(workspace: str, excluded: tuple[str, ...]) -> bool:
    if not workspace or not excluded:
        return False
    candidate = Path(os.path.normpath(os.path.expanduser(workspace)))
    for prefix in excluded:
        root = Path(prefix)
        if candidate == root:
            return True
        try:
            candidate.relative_to(root)
        except ValueError:
            continue
        return True
    return False


@main.command("export-learnings")
@click.option("--since", help="Only export lessons confirmed on or after this date.")
@click.option("--casebook", type=click.Path(path_type=Path), help="Override the configured casebook.")
@click.option("--config", "config_path", type=click.Path(path_type=Path), default=default_config_path, show_default=True)
def export_learnings(since: str | None, casebook: Path | None, config_path: Path) -> None:
    """Export privacy-safe confirmed lessons as an Org fragment."""
    if casebook is None:
        if not config_path.exists():
            raise click.ClickException(f"Configuration not found: {config_path}")
        casebook = load_config(config_path).casebook
    if not casebook.exists():
        raise click.ClickException(f"Casebook not found: {casebook}")
    since_value = parse_boundary(since) if since else None
    click.echo("\n".join(confirmed_lessons(casebook, since_value)), nl=True)


if __name__ == "__main__":
    main()

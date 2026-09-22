from __future__ import annotations

import json
import os
import socket
import tomllib
from dataclasses import dataclass
from pathlib import Path

SOURCE_NAMES = ("codex", "claude-code", "copilot", "cursor-cli", "copilot-vscode")


def default_config_path() -> Path:
    return Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config")) / "ai-transcript-review" / "config.toml"


def default_state_path() -> Path:
    return Path(os.environ.get("XDG_STATE_HOME", Path.home() / ".local" / "state")) / "ai-transcript-review" / "state.json"


def default_source_paths() -> dict[str, Path]:
    home = Path.home()
    copilot_home = Path(os.environ.get("COPILOT_HOME", home / ".copilot"))
    return {
        "codex": home / ".codex",
        "claude-code": home / ".claude",
        "copilot": copilot_home,
        "cursor-cli": home / ".cursor",
        "copilot-vscode": home / "Library" / "Application Support" / "Code" / "User",
    }


@dataclass(frozen=True, slots=True)
class Config:
    machine: str
    casebook: Path
    enabled_sources: tuple[str, ...]
    excluded_workspaces: tuple[str, ...]
    source_paths: dict[str, Path]
    state_path: Path


def load_config(path: Path) -> Config:
    with path.open("rb") as handle:
        data = tomllib.load(handle)
    sources = default_source_paths()
    for name, value in data.get("source_paths", {}).items():
        if name in SOURCE_NAMES:
            sources[name] = Path(value).expanduser()
    return Config(
        machine=str(data["machine"]),
        casebook=Path(data["casebook"]).expanduser(),
        enabled_sources=tuple(data.get("enabled_sources", SOURCE_NAMES)),
        excluded_workspaces=tuple(data.get("excluded_workspaces", [])),
        source_paths=sources,
        state_path=Path(data.get("state_path", default_state_path())).expanduser(),
    )


def write_config(path: Path, *, machine: str, casebook: Path) -> Config:
    path.parent.mkdir(parents=True, exist_ok=True)
    state_path = default_state_path()
    source_paths = default_source_paths()
    enabled = [name for name, source_path in source_paths.items() if source_path.exists()]
    lines = [
        f'machine = {json.dumps(machine)}',
        f'casebook = {json.dumps(str(casebook.expanduser()))}',
        f'state_path = {json.dumps(str(state_path))}',
        f'enabled_sources = {json.dumps(enabled)}',
        'excluded_workspaces = []',
        "",
        "[source_paths]",
    ]
    for name, source_path in source_paths.items():
        lines.append(f'{json.dumps(name)} = {json.dumps(str(source_path))}')
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    state_path.parent.mkdir(parents=True, exist_ok=True)
    if not state_path.exists():
        state_path.write_text(json.dumps({"version": 1, "machine": machine, "host": socket.gethostname(), "sources": {}, "runs": []}, indent=2) + "\n", encoding="utf-8")
    return load_config(path)

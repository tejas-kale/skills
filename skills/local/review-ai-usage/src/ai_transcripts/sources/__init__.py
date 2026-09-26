from .antigravity import collect_antigravity
from .claude_code import collect_claude_code
from .codex import collect_codex
from .copilot import collect_copilot
from .cursor import collect_cursor
from .vscode import collect_vscode

COLLECTORS = {
    "codex": collect_codex,
    "claude-code": collect_claude_code,
    "copilot": collect_copilot,
    "cursor-cli": collect_cursor,
    "copilot-vscode": collect_vscode,
    "antigravity-cli": collect_antigravity,
}

__all__ = ["COLLECTORS"]

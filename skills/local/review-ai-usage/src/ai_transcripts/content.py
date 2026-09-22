from __future__ import annotations

import json
from typing import Any


def text_content(content: Any) -> str:
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts: list[str] = []
        for item in content:
            if isinstance(item, str):
                parts.append(item)
            elif isinstance(item, dict):
                item_type = item.get("type", "")
                if item_type in {"text", "input_text", "output_text"}:
                    value = item.get("text") or item.get("value") or ""
                    if isinstance(value, str):
                        parts.append(value)
        return "\n".join(part for part in parts if part)
    if isinstance(content, dict):
        for key in ("text", "value", "content"):
            if key in content:
                return text_content(content[key])
    return ""


def json_value(value: Any) -> Any:
    if isinstance(value, str):
        try:
            return json.loads(value)
        except json.JSONDecodeError:
            return value
    return value

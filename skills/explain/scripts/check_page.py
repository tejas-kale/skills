#!/usr/bin/env python3
"""Check a page written with the explain skill. Usage: check_page.py <page.html>...

Prints one line per finding and exits 1 when any finding is an error.
"""

from __future__ import annotations

import os
import re
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass, field
from html.parser import HTMLParser


@dataclass(frozen=True)
class Finding:
    level: str  # "error" or "warning"
    code: str
    message: str


# Attributes that make the browser load a file: (tag, attribute).
LOADERS = {
    ("script", "src"), ("link", "href"), ("img", "src"), ("iframe", "src"), ("video", "src"),
    ("audio", "src"), ("source", "src"), ("embed", "src"), ("object", "data"), ("image", "href"),
    ("use", "href"), ("image", "xlink:href"), ("use", "xlink:href"),
}
CSS_LOAD = re.compile(r"@import\b|url\(\s*['\"]?(?!data:|#)", re.I)
JS_LOAD = re.compile(r"\bfetch\s*\(|XMLHttpRequest|\bWebSocket\s*\(|\bEventSource\s*\(|\bimportScripts\s*\(|\bimport\s*\(")


@dataclass
class Page:
    """What the checks need from one parse of the page."""

    tags: list[tuple[str, dict[str, str]]] = field(default_factory=list)
    css: str = ""
    scripts: list[tuple[str, str]] = field(default_factory=list)  # (type attribute, source)
    nav_links: int = 0  # links inside data-part="nav", not counting data-sub ones
    text: list[str] = field(default_factory=list)  # text outside style and script
    open_words: int = 0  # words a reader sees without opening a <details>


class _Reader(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.page = Page()
        self._raw: tuple[str, str] | None = None  # (tag, type attribute) while inside style or script
        self._buf: list[str] = []
        self._nav: list[str] = []  # the nav element's tag, once per open element of that tag inside it
        self._folded = 0  # depth of closed <details>

    def handle_starttag(self, tag, attrs):
        a = {k: (v or "") for k, v in attrs}
        self.page.tags.append((tag, a))
        if a.get("data-part") == "nav" or (self._nav and tag == self._nav[0]):
            self._nav.append(tag)
        elif self._nav and tag == "a" and "data-sub" not in a:
            self.page.nav_links += 1
        if tag in ("style", "script"):
            self._raw, self._buf = (tag, a.get("type", "")), []
        if tag == "details" and (self._folded or "open" not in a):
            self._folded += 1

    def handle_data(self, data):
        if self._raw:
            self._buf.append(data)
        else:
            self.page.text.append(data)
            if not self._folded:
                self.page.open_words += len(data.split())

    def handle_endtag(self, tag):
        if tag == "details" and self._folded:
            self._folded -= 1
        if self._nav and tag == self._nav[0]:
            self._nav.pop()
        if self._raw and tag == self._raw[0]:
            text = "".join(self._buf)
            if tag == "style":
                self.page.css += text + "\n"
            else:
                self.page.scripts.append((self._raw[1], text))
            self._raw = None


def read_page(html: str) -> Page:
    reader = _Reader()
    reader.feed(html)
    reader.close()
    return reader.page


def _is_code(script_type: str) -> bool:
    return script_type in ("", "module", "text/javascript", "application/javascript")


def _network(page: Page) -> list[Finding]:
    out = []
    for tag, attrs in page.tags:
        for attr, value in attrs.items():
            local = value.startswith(("data:", "#")) or not value
            if (tag, attr) in LOADERS and not local:
                out.append(Finding("error", "network", f'<{tag} {attr}="{value}"> loads a file; inline it'))
        if CSS_LOAD.search(attrs.get("style", "")):
            out.append(Finding("error", "network", f"<{tag}> style attribute loads a file; inline it"))
    if CSS_LOAD.search(page.css):
        out.append(Finding("error", "network", "the CSS loads a file (@import or url()); inline it"))
    for kind, source in page.scripts:
        hit = JS_LOAD.search(source) if _is_code(kind) else None
        if hit:
            out.append(Finding("error", "network", f"a script calls {hit.group(0).strip()}; embed the data in the page"))
    return out


GET_BY_ID = re.compile(r"getElementById\(\s*(['\"])([^'\"]+)\1\s*\)")


def _ids(page: Page) -> list[Finding]:
    out, seen = [], set()
    for _, attrs in page.tags:
        if "id" in attrs:
            if attrs["id"] in seen:
                out.append(Finding("error", "dup-id", f'id="{attrs["id"]}" is used more than once'))
            seen.add(attrs["id"])
    for tag, attrs in page.tags:
        target = attrs.get("href", "")
        if tag == "a" and target.startswith("#") and len(target) > 1 and target[1:] not in seen:
            out.append(Finding("error", "dead-link", f'<a href="{target}"> points at no element'))
        if tag == "label" and attrs.get("for") and attrs["for"] not in seen:
            out.append(Finding("error", "dead-link", f'<label for="{attrs["for"]}"> points at no element'))
    for kind, source in page.scripts:
        for match in GET_BY_ID.finditer(source if _is_code(kind) else ""):
            if match.group(2) not in seen:
                out.append(Finding("error", "dead-id", f'a script looks up id "{match.group(2)}", which the page lacks'))
    return out


TOKEN_USE = re.compile(r"var\(\s*(--[\w-]+)\s*\)")  # a var() with a fallback is safe and is skipped
TOKEN_DEF = re.compile(r"(--[\w-]+)\s*:|setProperty\(\s*['\"](--[\w-]+)")


def _theme(page: Page) -> list[Finding]:
    out = []
    if "prefers-color-scheme: dark" not in re.sub(r"\s+", " ", page.css):
        out.append(Finding("error", "theme", "no dark tokens under @media (prefers-color-scheme: dark)"))
    elif not re.search(r"\[data-theme=['\"]?dark['\"]?\]", page.css):
        out.append(Finding("error", "theme", 'no dark tokens under :root[data-theme="dark"]'))
    everything = [page.css] + [source for _, source in page.scripts]
    everything += [value for _, attrs in page.tags for value in attrs.values()]
    defined = {a or b for text in everything for a, b in TOKEN_DEF.findall(text)}
    used = {name for text in everything for name in TOKEN_USE.findall(text)}
    for name in sorted(used - defined):
        out.append(Finding("error", "token", f"var({name}) is used but {name} is never defined"))
    return out


FRAME = ("answer", "nav", "next", "provenance")
PROVENANCE = ("prompt", "sources", "not-checked")
MAX_NAV = 7


def _frame(page: Page) -> list[Finding]:
    out = []
    parts = {attrs.get("data-part") for _, attrs in page.tags}
    deck = any(tag == "body" and attrs.get("data-kind") == "deck" for tag, attrs in page.tags)
    for part in ("provenance",) if deck else FRAME:
        if part not in parts:
            out.append(Finding("error", "frame", f'no element with data-part="{part}"'))
    if "provenance" in parts:
        entries = {attrs.get("data-prov") for _, attrs in page.tags}
        for entry in PROVENANCE:
            if entry not in entries:
                out.append(Finding("error", "provenance", f'the provenance footer lacks data-prov="{entry}"'))
    if page.nav_links > MAX_NAV:
        out.append(Finding("error", "nav", f"the nav lists {page.nav_links} sections; the limit is {MAX_NAV}"))
    return out


def _reply(page: Page) -> list[Finding]:
    has = {key for _, attrs in page.tags for key in attrs if key.startswith(("data-reply", "data-pick"))}
    if "data-reply" in has and "data-pick" not in has:
        return [Finding("error", "reply", "a reply box (data-reply) without any data-pick control")]
    if "data-pick" in has and not {"data-reply", "data-reply-text", "data-reply-copy"} <= has:
        return [Finding("error", "reply", "data-pick controls need data-reply, data-reply-text and data-reply-copy")]
    return []


def _placeholders(page: Page) -> list[Finding]:
    values = page.text + [value for _, attrs in page.tags for value in attrs.values()]
    left = sorted({m for value in values for m in re.findall(r"\{\{fill:[^{}]*\}\}", value)})
    return [Finding("error", "placeholder", f"template placeholder left in the page: {m}") for m in left]


def _scripts(page: Page) -> list[Finding]:
    code = [(kind, source) for kind, source in page.scripts if _is_code(kind) and source.strip()]
    if not code:
        return []
    node = shutil.which("node")
    if node is None:
        return [Finding("warning", "js-skipped", "node is not installed; the scripts were not syntax-checked")]
    out = []
    for kind, source in code:
        with tempfile.NamedTemporaryFile("w", suffix=".mjs" if kind == "module" else ".js", delete=False) as handle:
            handle.write(source)
        try:
            run = subprocess.run([node, "--check", handle.name], capture_output=True, text=True, timeout=30)
        finally:
            os.unlink(handle.name)
        if run.returncode != 0:
            where = [line for line in run.stderr.splitlines() if "Error" in line]
            out.append(Finding("error", "js", f"a script does not parse: {where[0] if where else run.stderr.strip()[:200]}"))
    return out


NAME = re.compile(r"\d{4}-\d{2}-\d{2}-[a-z0-9]+(-[a-z0-9]+)*\.html")
WORDS_PER_MINUTE = 230
MAX_OPEN_MINUTES = 8  # the target is about 5; past this the page should fold detail or split


def _shape(page: Page, name: str) -> list[Finding]:
    out = []
    if name and not NAME.fullmatch(os.path.basename(name)):
        out.append(Finding("warning", "name", f"{os.path.basename(name)}: name the file <YYYY-MM-DD>-<slug>.html"))
    minutes = page.open_words / WORDS_PER_MINUTE
    if minutes > MAX_OPEN_MINUTES:
        out.append(Finding("warning", "length", f"about {minutes:.0f} minutes of open text; fold detail or split the page"))
    return out


def check_page(html: str, name: str = "") -> list[Finding]:
    """Every finding for one page. `name` is the file name; empty skips the name check."""
    page = read_page(html)
    return (
        _network(page) + _ids(page) + _theme(page) + _frame(page) + _reply(page) + _placeholders(page)
        + _scripts(page) + _shape(page, name)
    )


def main(paths: list[str]) -> int:
    if not paths:
        print(__doc__.strip(), file=sys.stderr)
        return 2
    failed = False
    for path in paths:
        with open(path, encoding="utf-8") as handle:
            html = handle.read()
        findings = check_page(html, path)
        page = read_page(html)
        for finding in findings:
            print(f"{path}: {finding.level}: [{finding.code}] {finding.message}")
        errors = sum(f.level == "error" for f in findings)
        failed = failed or errors > 0
        minutes = max(1, round(page.open_words / WORDS_PER_MINUTE))
        print(f"{path}: {errors} errors, {len(findings) - errors} warnings, about {minutes} min of open text")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

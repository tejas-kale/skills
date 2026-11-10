#!/usr/bin/env python3
"""Hard checks for a Data Insight draft: title length, body length, chart count, source line.

Usage: check_insight.py <post-dir | draft-file>

A post dir is searched for one draft.{md,qmd,markdown,org}. Markdown (with or without YAML
front matter) and Org drafts are parsed. Exit status: 0 all checks pass, 1 a check fails,
2 the draft cannot be found or read.
"""

import re
import sys
from pathlib import Path

TITLE_MAX = 100
BODY_MAX = 850
DRAFT_SUFFIXES = (".md", ".qmd", ".markdown", ".org")
IMAGE_EXT = r"\.(?:png|svg|jpe?g|webp|gif)"

SOURCE_RE = re.compile(r"^[*_]{0,2}(?:data\s+)?sources?[*_]{0,2}\s*:[*_]{0,2}\s*(.*)$", re.I)
MD_IMAGE_RE = re.compile(r"!\[[^\]]*\]\([^)]*\)")
HTML_IMAGE_RE = re.compile(r"<img\b[^>]*>", re.I)
SHORTCODE_RE = re.compile(r"\{\{<\s*figure\b[^>]*>\}\}")
ORG_IMAGE_RE = re.compile(r"\[\[(?:file:)?[^\]]+" + IMAGE_EXT + r"\](?:\[[^\]]*\])?\]", re.I)


def find_draft(arg: Path) -> Path:
    if arg.is_file():
        return arg
    if arg.is_dir():
        found = sorted(p for p in arg.glob("draft.*") if p.suffix in DRAFT_SUFFIXES)
        if len(found) == 1:
            return found[0]
        names = ", ".join(p.name for p in found) or "none"
        fail(f"expected one draft.{{md,qmd,markdown,org}} in {arg}, found: {names}")
    fail(f"no such file or directory: {arg}")


def fail(msg: str):
    print(f"error: {msg}", file=sys.stderr)
    sys.exit(2)


def count_images(line: str) -> int:
    return sum(len(r.findall(line)) for r in (MD_IMAGE_RE, HTML_IMAGE_RE, SHORTCODE_RE, ORG_IMAGE_RE))


def strip_inline(text: str) -> str:
    """Reduce inline markup to the text a reader sees."""
    text = re.sub(r"\[\[[^\]]+\]\[([^\]]+)\]\]", r"\1", text)  # org [[url][text]]
    text = re.sub(r"\[\[([^\]]+)\]\]", r"\1", text)  # org [[url]]
    text = re.sub(r"\[([^\]]+)\]\([^)]*\)", r"\1", text)  # md [text](url)
    text = re.sub(r"<[^>]+>", "", text)  # html tags
    text = re.sub(r"(\*\*|__)(.+?)\1", r"\2", text)  # md bold
    text = re.sub(r"(?<![\w*])([*_])(?!\s)(.+?)(?<!\s)\1(?![\w*])", r"\2", text)  # md italic, org bold
    text = re.sub(r"(?<![\w/])([/=~+])(?!\s)(.+?)(?<!\s)\1(?![\w/])", r"\2", text)  # org /i/ =c= ~c~ +s+
    text = re.sub(r"`([^`]*)`", r"\1", text)  # inline code
    return re.sub(r"[ \t]+", " ", text).strip()


def parse(path: Path) -> dict:
    lines = path.read_text(encoding="utf-8").splitlines()
    is_org = path.suffix == ".org"
    title, sources, charts = None, [], 0
    paragraphs, current = [], []
    i = 0

    if not is_org and lines and lines[0].strip() == "---":  # YAML front matter
        end = next((j for j in range(1, len(lines)) if lines[j].strip() in ("---", "...")), None)
        if end is not None:
            for fm in lines[1:end]:
                m = re.match(r"^title\s*:\s*(.+)$", fm)
                if m:
                    title = m.group(1).strip().strip("'\"")
            i = end + 1

    def flush():
        if current:
            paragraphs.append(strip_inline(" ".join(current)))
            current.clear()

    in_block = None
    for line in lines[i:]:
        s = line.strip()
        if in_block:
            if re.match(in_block, s, re.I):
                in_block = None
            continue
        if s.startswith("```") or s.startswith("~~~"):
            flush()
            in_block = r"^" + re.escape(s[:3])
            continue
        if re.match(r"^#\+begin_(\w+)", s, re.I):
            flush()
            in_block = r"^#\+end_" + re.match(r"^#\+begin_(\w+)", s, re.I).group(1)
            continue
        if s.startswith("<!--"):
            flush()
            if "-->" not in s:
                in_block = r".*-->"
            continue
        if is_org and re.match(r"^#\+title:", s, re.I):
            title = title or s.split(":", 1)[1].strip()
            continue
        if is_org and (s.startswith("#+") or s.startswith(":")):
            continue
        heading = re.match(r"^(#{1,6}|\*+)\s+(.*)$", s) if (not is_org and s.startswith("#")) or (is_org and s.startswith("*")) else None
        if heading:
            flush()
            if title is None:
                title = strip_inline(heading.group(2))
            continue
        n = count_images(s)
        if n:
            flush()
            charts += n
            continue
        m = SOURCE_RE.match(s)
        if m and s:
            flush()
            sources.append(strip_inline(m.group(1)))
            continue
        if not s:
            flush()
            continue
        current.append(s)
    flush()

    return {"title": title or "", "body": "\n\n".join(p for p in paragraphs if p), "charts": charts, "sources": sources}


def main() -> int:
    if len(sys.argv) != 2:
        print(__doc__.strip(), file=sys.stderr)
        return 2
    draft = find_draft(Path(sys.argv[1]))
    d = parse(draft)
    t, b = len(d["title"]), len(d["body"])

    checks = [
        ("title", t <= TITLE_MAX and t > 0, f"{t} / {TITLE_MAX} characters" + ("" if t else " (no title found)")),
        ("body", b <= BODY_MAX, f"{b} / {BODY_MAX} characters, spaces included, paragraph breaks count 2"),
        ("charts", d["charts"] == 1, f"{d['charts']} (need exactly 1)"),
    ]
    if not d["sources"]:
        checks.append(("source", False, "no line starting 'Source:' or 'Data source:'"))
    elif len(d["sources"]) > 1:
        checks.append(("source", False, f"{len(d['sources'])} source lines (need 1)"))
    elif not d["sources"][0]:
        checks.append(("source", False, "source line is empty"))
    else:
        checks.append(("source", True, f'"{d["sources"][0]}" (confirm it names producer and dataset)'))

    print(f"draft: {draft}")
    for name, ok, detail in checks:
        print(f"{'PASS' if ok else 'FAIL'}  {name:<7} {detail}")
        if name == "body" and b > BODY_MAX:
            print(f"      {'':<7} {b - BODY_MAX} over")
    print(f"\n--- parsed title ---\n{d['title']}\n--- parsed body ---\n{d['body']}")
    return 0 if all(ok for _, ok, _ in checks) else 1


if __name__ == "__main__":
    sys.exit(main())

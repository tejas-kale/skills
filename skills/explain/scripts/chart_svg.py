"""Render matplotlib figures (plotnine too: `ggplot.draw()` returns one) as inline SVG for an explain page.

    use_page_style()                         # once, before any figure is made
    fig, ax = plt.subplots(figsize=(7, 3.2))
    ax.plot(x, y, color=COLORS["series-1"])
    put_chart("2026-11-16-readout.html", "lift", fig)

The page holds one slot per chart: <!-- chart:lift --><!-- /chart:lift -->. The figure is drawn in
placeholder colours that are swapped for the page's tokens (var(--series-1), var(--muted), ...), so
the chart follows the light and the dark theme. Colours from a colormap are kept as they are.
"""

from __future__ import annotations

import io
import re
from pathlib import Path

# token -> placeholder colour the figure is drawn in
COLORS = {
    "text": "#010203", "muted": "#010204", "border": "#010205", "surface": "#010206",
    "good": "#010207", "warn": "#010208", "bad": "#010209", "accent": "#01020a",
    "series-1": "#010211", "series-2": "#010212", "series-3": "#010213", "series-4": "#010214", "series-5": "#010215",
}


def use_page_style() -> None:
    """Set matplotlib defaults so new figures use the placeholder colours and the page's plain look."""
    import matplotlib as mpl
    from cycler import cycler

    mpl.rcParams.update({
        "svg.fonttype": "none",  # text stays text: selectable, and it takes the page font
        "figure.facecolor": "none", "axes.facecolor": "none", "savefig.facecolor": "none",
        "text.color": COLORS["text"], "axes.titlecolor": COLORS["text"],
        "axes.labelcolor": COLORS["muted"], "xtick.color": COLORS["muted"], "ytick.color": COLORS["muted"],
        "axes.edgecolor": COLORS["border"], "grid.color": COLORS["border"],
        "legend.frameon": False, "legend.labelcolor": COLORS["text"],
        "axes.spines.top": False, "axes.spines.right": False,
        "axes.prop_cycle": cycler(color=[COLORS[f"series-{n}"] for n in range(1, 6)]),
        "font.size": 10, "axes.titlesize": 11, "axes.titleweight": "bold", "axes.titlelocation": "left",
        "lines.linewidth": 2,
    })


def page_svg(fig, label: str) -> str:
    """The figure as an <svg> fragment. `label` is read by screen readers and keeps ids apart."""
    import matplotlib as mpl
    import matplotlib.pyplot as plt

    buffer = io.StringIO()
    with mpl.rc_context({"svg.hashsalt": label}):
        fig.savefig(buffer, format="svg", transparent=True, bbox_inches="tight")
    plt.close(fig)
    svg = buffer.getvalue()
    svg = svg[svg.index("<svg"):]
    svg = re.sub(r"<metadata>.*?</metadata>\s*", "", svg, flags=re.S)
    opening, rest = svg.split(">", 1)
    opening = re.sub(r'\s(?:width|height)="[^"]*"', "", opening)
    salt = re.sub(r"[^a-z0-9]+", "-", label.lower()).strip("-")
    rest = re.sub(r'\bid="([^"]+)"', rf'id="{salt}-\1"', rest)
    rest = re.sub(r"url\(#([^)]+)\)", rf"url(#{salt}-\1)", rest)
    rest = re.sub(r'href="#([^"]+)"', rf'href="#{salt}-\1"', rest)
    rest = re.sub(r"<style[^>]*>.*?</style>\s*", "", rest, flags=re.S)  # it would apply to the whole page
    rest = re.sub(r"font-family: [^;\"]+", "font-family: var(--font-body, system-ui, sans-serif)", rest)
    joins = 'style="stroke-linejoin: round; stroke-linecap: butt"'
    svg = f'{opening} role="img" aria-label="{_attr(label)}" {joins}>{rest}'
    for token, placeholder in COLORS.items():
        svg = re.sub(re.escape(placeholder), f"var(--{token})", svg, flags=re.I)
    return svg.strip()


def put_chart(page: str | Path, name: str, fig, label: str | None = None) -> None:
    """Write the figure into the page's slot <!-- chart:NAME --> ... <!-- /chart:NAME -->, replacing what is there."""
    page = Path(page)
    html = page.read_text(encoding="utf-8")
    start, end = f"<!-- chart:{name} -->", f"<!-- /chart:{name} -->"
    if start not in html or end not in html:
        raise ValueError(f"{page.name} has no slot {start}{end}")
    head, tail = html.split(start, 1)[0], html.split(end, 1)[1]
    page.write_text(f"{head}{start}\n{page_svg(fig, label or name)}\n{end}{tail}", encoding="utf-8")


def _attr(text: str) -> str:
    return text.replace("&", "&amp;").replace('"', "&quot;").replace("<", "&lt;")

"""Tests for chart_svg: a matplotlib figure becomes inline SVG that follows the page's colour tokens."""

import re

import pytest

plt = pytest.importorskip("matplotlib.pyplot")

from chart_svg import COLORS, page_svg, put_chart, use_page_style  # noqa: E402


def line_figure():
    use_page_style()
    fig, ax = plt.subplots(figsize=(6, 3))
    ax.plot([1, 2, 3], [2, 4, 3], label="treatment")
    ax.plot([1, 2, 3], [1, 2, 2], label="control")
    ax.set_xlabel("week")
    ax.legend()
    return fig


def test_the_svg_takes_its_colours_from_the_page_tokens():
    svg = page_svg(line_figure(), "conversion by week")
    assert "var(--series-1)" in svg and "var(--series-2)" in svg and "var(--muted)" in svg
    assert not any(sentinel in svg for sentinel in COLORS.values())


def test_the_svg_is_an_inline_fragment_that_scales_with_the_page():
    svg = page_svg(line_figure(), "conversion by week")
    assert svg.startswith("<svg") and svg.rstrip().endswith("</svg>")
    opening = svg[: svg.index(">")]
    assert "viewBox=" in opening and "width=" not in opening and 'aria-label="conversion by week"' in opening
    assert "DejaVu" not in svg and "<metadata" not in svg and ">week<" in svg
    assert "<style" not in svg, "a <style> inside inline SVG would restyle the whole page"
    assert "font-family: var(--font-body," in svg


def test_two_charts_on_one_page_share_no_ids():
    ids = [re.findall(r'\bid="([^"]+)"', page_svg(line_figure(), name)) for name in ("first", "second")]
    assert ids[0] and not set(ids[0]) & set(ids[1])


def test_put_chart_fills_its_slot_and_a_rerun_replaces_it(tmp_path):
    page = tmp_path / "2026-11-16-readout.html"
    page.write_text("<figure><!-- chart:lift --><!-- /chart:lift --><figcaption>c</figcaption></figure>")
    put_chart(page, "lift", line_figure())
    put_chart(page, "lift", line_figure())
    html = page.read_text()
    assert html.count("<svg") == 1 and html.endswith("<!-- /chart:lift --><figcaption>c</figcaption></figure>")


def test_put_chart_names_the_missing_slot(tmp_path):
    page = tmp_path / "p.html"
    page.write_text("<figure></figure>")
    with pytest.raises(ValueError, match="chart:lift"):
        put_chart(page, "lift", line_figure())

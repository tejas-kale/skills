"""Tests for check_page: each test feeds one page to the checker and reads the finding codes."""

import pathlib
import shutil

import pytest

from check_page import check_page

CSS = """
:root { --bg: #fff; --text: #111; }
@media (prefers-color-scheme: dark) { :root:not([data-theme="light"]) { --bg: #111; --text: #eee; } }
:root[data-theme="dark"] { --bg: #111; --text: #eee; }
body { background: var(--bg); color: var(--text); }
"""

BODY = """
<nav data-part="nav"><a href="#why">Why</a><a href="#how">How</a></nav>
<main>
  <h1>Title</h1>
  <div data-part="answer">The answer in two lines.</div>
  <h2 id="why">Why</h2><p>Because.</p>
  <h2 id="how">How</h2><p>Like this.</p>
  <div data-part="next">Next: run the tests.</div>
  <footer data-part="provenance">
    <div data-prov="prompt">explain x</div>
    <div data-prov="sources">a.py:1</div>
    <div data-prov="not-checked">nothing</div>
  </footer>
</main>
"""


def page(css=CSS, body=BODY, head="", script="", body_attrs=""):
    return (
        '<!doctype html><html lang="en"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width, initial-scale=1">'
        f"<title>Title</title>{head}<style>{css}</style></head>"
        f"<body{body_attrs}>{body}<script>{script}</script></body></html>"
    )


def codes(html, name="2026-11-16-title.html", level=None):
    return [f.code for f in check_page(html, name) if level in (None, f.level)]


def test_a_complete_page_has_no_findings():
    assert codes(page()) == []


@pytest.mark.parametrize(
    "head",
    [
        '<script src="https://cdn.example.com/plot.js"></script>',
        '<link rel="stylesheet" href="//fonts.example.com/a.css">',
        '<link rel="stylesheet" href="local.css">',
    ],
)
def test_a_page_that_loads_another_file_is_an_error(head):
    assert codes(page(head=head)) == ["network"]


def test_images_must_be_inline():
    assert codes(page(body=BODY + '<img src="chart.png" alt="">')) == ["network"]
    assert codes(page(body=BODY + '<img src="data:image/png;base64,AAAA" alt="">')) == []


def test_css_and_js_may_not_fetch():
    assert codes(page(css=CSS + '@import url("https://x.example/a.css");')) == ["network"]
    assert codes(page(css=CSS + "body { background-image: url(bg.png); }")) == ["network"]
    assert codes(page(script='fetch("/api/data").then(r => r.json());')) == ["network"]


def test_links_to_sources_are_allowed():
    assert codes(page(body=BODY + '<a href="https://example.com/paper">paper</a>')) == []


def test_a_link_to_a_missing_section_is_an_error():
    assert codes(page(body=BODY + '<a href="#gone">jump</a>')) == ["dead-link"]


def test_a_script_that_looks_up_a_missing_id_is_an_error():
    assert codes(page(script='document.getElementById("copy").focus();')) == ["dead-id"]
    assert codes(page(body=BODY + '<button id="copy">copy</button>', script='document.getElementById("copy").focus();')) == []


def test_an_id_used_twice_is_an_error():
    assert codes(page(body=BODY + '<p id="why">again</p>')) == ["dup-id"]


def test_a_page_without_a_dark_theme_is_an_error():
    light_only = ":root { --bg: #fff; --text: #111; } body { background: var(--bg); color: var(--text); }"
    assert codes(page(css=light_only)) == ["theme"]


def test_dark_tokens_must_follow_the_os_and_the_data_theme_switch():
    os_only = CSS.replace(':root[data-theme="dark"] { --bg: #111; --text: #eee; }', "")
    assert codes(page(css=os_only)) == ["theme"]


def test_a_token_that_is_used_but_never_defined_is_an_error():
    assert codes(page(css=CSS + "h1 { color: var(--accent); }")) == ["token"]
    assert codes(page(css=CSS + "h1 { color: var(--accent, red); }")) == []
    assert codes(page(body=BODY + '<svg><path stroke="var(--series-1)"/></svg>')) == ["token"]


@pytest.mark.parametrize("part", ["answer", "next", "provenance"])
def test_a_page_missing_a_part_of_the_frame_is_an_error(part):
    assert codes(page(body=BODY.replace(f'data-part="{part}"', ""))) == ["frame"]


@pytest.mark.parametrize("entry", ["prompt", "sources", "not-checked"])
def test_provenance_needs_prompt_sources_and_not_checked(entry):
    assert codes(page(body=BODY.replace(f'data-prov="{entry}"', ""))) == ["provenance"]


def test_the_nav_holds_at_most_seven_sections():
    links = "".join(f'<a href="#why">s{i}</a>' for i in range(8))
    assert codes(page(body=BODY.replace('<a href="#why">Why</a>', links))) == ["nav"]


def test_a_deck_is_exempt_from_the_frame_but_keeps_provenance():
    slides = '<section>one</section><footer data-part="provenance"><i data-prov="prompt">p</i><i data-prov="sources">s</i><i data-prov="not-checked">n</i></footer>'
    assert codes(page(body=slides, body_attrs=' data-kind="deck"')) == []
    assert codes(page(body="<section>one</section>", body_attrs=' data-kind="deck"')) == ["frame"]


def test_a_reply_box_needs_picks_and_picks_need_a_reply_box():
    box = '<div data-reply><pre data-reply-text></pre><button data-reply-copy>copy</button></div>'
    pick = '<label><input type="checkbox" data-pick="Option 1"> Option 1</label>'
    assert codes(page(body=BODY + box)) == ["reply"]
    assert codes(page(body=BODY + pick)) == ["reply"]
    assert codes(page(body=BODY + pick + box)) == []


def test_a_placeholder_left_from_the_template_is_an_error():
    assert codes(page(body=BODY + "<p>{{fill: one-line answer}}</p>")) == ["placeholder"]


def test_double_braces_in_a_code_sample_are_not_placeholders():
    assert codes(page(body=BODY + "<pre>select * from {{ ref('orders') }}</pre>")) == []


def test_the_template_fails_only_on_its_own_placeholders():
    template = (pathlib.Path(__file__).parent.parent / "template.html").read_text(encoding="utf-8")
    assert set(codes(template, name="2026-11-16-title.html")) == {"placeholder"}


@pytest.mark.skipif(shutil.which("node") is None, reason="needs node")
def test_a_script_with_a_syntax_error_is_an_error():
    assert codes(page(script="function broken( { return 1; }")) == ["js"]
    assert codes(page(script="const ok = [1, 2].map(n => n * 2);")) == []


def test_json_data_blocks_are_not_checked_as_code():
    data = '<script type="application/json" id="data">{"rows": [1, 2]}</script>'
    assert codes(page(body=BODY + data)) == []


def test_without_node_the_script_check_is_reported_as_skipped(monkeypatch):
    monkeypatch.setattr(shutil, "which", lambda _: None)
    assert codes(page(script="const ok = 1;")) == ["js-skipped"]
    assert codes(page(script="const ok = 1;"), level="error") == []


def test_the_file_name_is_a_date_and_a_slug():
    assert codes(page(), name="rate limiting.html") == ["name"]
    assert codes(page(), name="docs/explain/2026-11-16-rate-limiting.html") == []


def test_a_page_far_beyond_five_minutes_of_open_text_gets_a_warning():
    long_body = BODY.replace("<p>Because.</p>", "<p>" + "word " * 2600 + "</p>")
    folded = BODY.replace("<p>Because.</p>", "<details><summary>more</summary>" + "word " * 2600 + "</details>")
    assert codes(page(body=long_body)) == ["length"]
    assert codes(page(body=long_body), level="error") == []
    assert codes(page(body=folded)) == []

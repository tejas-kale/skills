---
name: explain
description: Write a self-contained HTML page into the project - an explanation, report, brainstorm, exploration, decision page, plan, review or slide deck, for software, data, statistics or ML work. Use when the user asks for a page, HTML, an artifact, a report or a deck, or types /explain.
---

# Explain

A **page** is one self-contained `.html` file that answers one question better than a wall of text: the reader sees the conclusion first, looks at figures instead of imagining them, and answers by clicking. Everything the page needs is inside the file, so it opens offline from disk, in any browser, for as long as the file exists.

This skill's directory holds `template.html` (the house style and every component), `PATTERNS.md` (one recipe per kind of page), `FIGURES.md` (diagrams and charts) and `scripts/`.

## 1. Pick the kind

Read `PATTERNS.md` and choose the recipe that fits the request. Say the kind in one line and start writing. Ask one question first only when you cannot tell which analysis the page belongs to, or when two kinds would give the user two different pages.

A page answers one question in about 5 minutes of reading: 4 to 7 sections. When the topic needs more, write the first page and name the second in its next-action box.

Done when you have told the user the kind and the question the page answers.

## 2. Place the file

`<root>` is the directory the session was started in.

| `<root>` has | The page goes to |
|---|---|
| no `analyses/` directory | `<root>/docs/explain/` |
| `analyses/`, and the page is about one analysis | `<root>/analyses/<slug>/explain/` |
| `analyses/`, and the page belongs to no analysis | `<root>/analyses/explain/` |

Name it `<YYYY-MM-DD>-<slug>.html`: today's date and 2 to 4 kebab-case words. A change to an existing page edits that file; a new question gets a new file. Git is the user's: write the file and leave staging, committing and ignore rules to them.

Done when the target path is fixed.

## 3. Gather, keeping the source of every claim

Read the code, run the queries, read the documents. For each fact you will put on the page, keep where it came from: `file.py:10-80`, `catalog.schema.table`, the query, the URL, the command and its output. A claim you could not trace goes on the **not checked** list.

Done when every claim planned for the page has a source or sits on the not-checked list.

## 4. Write the page

Copy `template.html` to the target path and fill it.

- **Frame.** Every page has the answer box first (the conclusion in 2 to 3 lines), a nav of at most 7 sections, one next-action box, and the provenance footer with the user's prompt verbatim, the date, your agent and model name, the sources and the not-checked list. A deck keeps only the provenance, in its last slide.
- **Components.** Use the ones the recipe names, and delete every other component together with its block in the script. Detail a reader may skip goes into a closed fold.
- **Style.** Colours, fonts and radii come from the template's tokens, unchanged. A new element is styled with the same tokens.
- **Self-contained.** CSS, JavaScript, figures and data are inline. Links to sources are fine; everything the page renders is in the file.
- **Figures.** When the page has a diagram or a chart, read `FIGURES.md`.
- **Reply box.** A page that asks the reader to choose (a brainstorm, an exploration, a plan, a decision page) gets pick controls and the reply box, so the reader's clicks become a text to paste back to you. Each `data-pick` value reads on its own, without the page. Explainers, reports and decks have none.
- **Words.** Write for someone who was not in the session: full sentences, numbers with their unit, period and population, file names as `code`. The page states what you found; how you worked belongs in provenance.

Done when no `{{fill: ...}}` is left and every section of the recipe is on the page.

## 5. Check

Run `python3 <this skill's directory>/scripts/check_page.py <page>` and fix the page until it reports 0 errors. Read each warning and fix it or keep it for the hand-over. When your harness can open a browser, also look at the page in light and dark and at phone width.

Done when the checker prints `0 errors`.

## 6. Hand over

Reply with, in this order:

1. `open <path to the page>`, as the first line.
2. The answer-box conclusion in one or two lines.
3. On a page with a reply box: "Pick on the page and paste the reply here."
4. Any checker warning you kept, and that the layout is unseen when you had no browser.

Publish the page anywhere (Claude Code's Artifact tool included) only when the user asks for it in this session.

## Changing a page

Edit the same file. Add the new request under the prompt in the provenance footer with its date, update sources and not-checked, rerun the chart script if the data or a chart changed, and run step 5 again.

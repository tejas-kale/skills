---
name: owid-insight-editor
description: One editing pass on a Data Insight draft in Our World in Data style, ending in at most 5 ranked fixes and a publish verdict. Use when the user asks to edit, review or check a Data Insight draft.
---

# OWID insight editor

The user publishes a weekly Data Insight on their blog to test their fit for OWID's Writer role (<https://ourworldindata.org/hiring-writer-2026>, reporting to Hannah Ritchie). Each insight tests one popular claim with OWID data. Edit to the standard of a published OWID insight: a reader should finish it knowing whether the claim holds and by how much.

The pass ends in a **fix list** the user acts on in about 10 minutes: at most 5 fixes, each a paste-in rewrite. The user applies the fixes; the draft file stays as it is.

## 1. Find the post

Drafts live in the blog repo as `posts/<slug>/`: the draft (`draft.md`, `draft.qmd` or `draft.org`), the plotting script and the data CSV. Take the slug from the request; when none is given and more than one post is in progress, ask which.

**Done when:** you have the paths of the draft, the plotting script and the CSV.

## 2. Run the hard checks

```bash
python3 <this skill's dir>/scripts/check_insight.py posts/<slug>
```

It checks title ≤ 100 characters, body ≤ 850 characters (spaces included, paragraph breaks count 2), exactly 1 chart embed, and one `Source:` / `Data source:` line, and prints the parsed title and body. Compare the parsed text with the draft: a heading, caption or note that landed in the body skews the count. Confirm by reading that the source line names both the producer and the dataset, in OWID's form `Producer, Dataset (year)` (e.g. "IHME, Global Burden of Disease (2025)").

**Done when:** you have the four results with their actual counts, and every FAIL is a candidate fix.

## 3. Read the evidence

- The CSV: entities, years, units, and whether values are totals, per capita, shares or age-standardised.
- The plotting script: what it plots, every transform, the chart title, subtitle and axis labels.
- The rendered chart, if the draft embeds an image file: open it.
- [`references/examples.md`](references/examples.md): three published insights by Hannah Ritchie, for format and voice.

**Done when:** you can state in one sentence what the chart plots (metric, unit, entities, years), and every number in the text is traced to a CSV row or marked untraced.

## 4. Apply the editorial checklist

Mark each item pass or fail, quoting the line it rests on.

1. **Claim title.** The title states the claim the insight tests, as a sentence a reader could dispute. "China reduced extreme poverty fast, but Indonesia hasn't been far behind" is a claim; "Poverty in Asia" is a topic.
2. **Concrete stake.** The opening gives a reader a reason to care in concrete terms: a count of people, a share of deaths, a familiar belief being tested.
3. **One number.** A single number carries the claim and the chart shows it. It matches the CSV, with its year and unit.
4. **Fair comparison.** Compared entities share a metric that removes size and age effects (per capita, shares, age-standardised rates), the same years and the same definitions. Counts across countries of different sizes, or crude rates across populations of different ages, fail.
5. **Plain caveat.** The main limitation of the data or metric is stated in one plain sentence, as in "Note that the international poverty line is extremely low".
6. **Evidence, not sermon.** The text reports what the data shows and leaves the reader to judge; "should", "must" and "shameful" are fails.
7. **Chart agrees with text.** The chart title makes the same claim as the insight title, the subtitle names the metric the text uses, and axis units and years match the numbers in the text.

**Done when:** all 7 items are marked, each fail with its quoted line.

## 5. Rank and write the fixes

Candidates are the hard-check FAILs and the checklist fails. Rank by impact:

1. The data does not support the claim, or the comparison is unfair (items 3, 4).
2. Hard-check failures.
3. Title, stake and number (items 1, 2, 3).
4. Caveat and chart agreement (items 5, 7).
5. Wording (item 6, and anything else).

Keep the top 5. For each, quote the exact line (from the draft, or from the plotting script for a chart fix), give the rewrite, and one line on why. Write rewrites in the voice of the examples: short sentences, plain words, numbers with units and years.

Then copy the draft to a scratch file, apply every fix, and run `check_insight.py` on the copy.

**Done when:** you have at most 5 fixes, each with a quoted line and a rewrite, and the patched copy passes every hard check.

## 6. Give the verdict

- **publish**: every hard check and checklist item passes; any fixes listed are optional polish.
- **publish after fixes**: the listed fixes are enough to pass every check.
- **rethink the angle**: the data does not settle the claim, or a fix needs new data or a different chart. Say in one line what to change.

## Output

```
Hard checks
PASS title 87/100 · FAIL body 912/850 (62 over) · PASS charts 1 · PASS source "IHME, Global Burden of Disease (2025)"

Fixes
1. [Fair comparison] "<exact line>"
   → "<rewrite>"
   Why: <one line>
2. ...

Verdict: publish after fixes
```

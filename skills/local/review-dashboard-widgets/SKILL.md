---
name: review-dashboard-widgets
description: Audit a Databricks Lakeview dashboard's widgets against the SQL that actually powers them, producing a findings document of claim vs. compute.
disable-model-invocation: true
---

# Review dashboard widgets

Audit an existing Databricks Lakeview dashboard: for every widget, compare its
**claim** — the title and description a reader sees — against what it
**computes** — the reconstructed query over the view it reads. A gap between
the two is a finding.

Use this to check a dashboard someone else built (or built a while ago), not
while designing a new one — that is `databricks-aibi-dashboards`.

The output is a single Org document a reader can trust in place of clicking
through the dashboard themselves, with executable source blocks: every
reconstructed widget query is a `databricks-sql` block (`#+begin_src
databricks-sql`), so a reader can re-run it and get a fresh `#+RESULTS:`
without leaving the file. Reserve `bash` blocks for CLI calls that are not
themselves SQL — pulling the dashboard JSON in step 2 is the only one.

## 1. Preflight

Get the dashboard ID and SQL warehouse ID (from its URL or the caller). Pick
the output document's path and confirm the review directory exists. Do the
review on its own branch (or worktree) so it can be dropped or merged as one
unit when step 9 closes it out.

Settle the review's **contract** before reading a single widget — what
"correct" means and where "intended" comes from — since both are ambiguous
by default and change what counts as a finding. If the request does not
already say, put it to the requester rather than assuming:

- Which layers count: SQL semantics (right tables, joins, filters, grain),
  visual encoding (does the chart type/axis/filter scope match the title), or
  numerical agreement (re-derive the number independently and compare)? Any
  combination is valid — get it explicit.
- What "intended" means: the dashboard's own titles and descriptions, by
  default — an external spec only if the requester names one.

A genuinely open-ended request ("review this dashboard") is exactly the shape
`grilling`/`grill-to-plan` exists for — reach for it rather than guessing.

Run dashboard and warehouse CLI calls from a terminal, not a notebook kernel —
a kernel process often cannot reach the OS keyring, and `databricks` then
returns empty output with no error.

**Done when:** you have a dashboard ID, a warehouse ID, an output path, and an
explicit contract for what counts as a finding.

## 2. Pull the definitions

```bash
databricks lakeview get <dashboard-id> --profile <profile> -o json > dashboard.json
```

For each dataset in the JSON, check its query. A bare `SELECT * FROM <view>`
means the real definition lives in the view, not the dashboard — pull it with
`SHOW CREATE TABLE <view>` (or the equivalent on the warehouse in use) and
read the definition, not just the dashboard JSON, before writing anything
about what a widget computes. A dataset with real column expressions
(aggregates, `CASE`, window functions) carries part of the definition itself —
record those expressions verbatim rather than paraphrasing them.

**Done when:** every dataset's query is either a bare `SELECT *` with its
backing view's definition pulled, or a dataset with its own expressions
recorded verbatim.

## 3. Write the Understanding section

One short section: what the dashboard reports, page and widget counts, how
many datasets back it, and its own stated purpose (usually a header text
widget) quoted verbatim. Keep it to a handful of sentences — it orients the
reader, it does not re-describe every widget; that is the next section's job.

**Done when:** a reader who has never opened the dashboard knows what it is
for and how big it is.

## 4. Reconstruct and run each widget's query

A dashboard stores a widget as dataset + fields + filters + encoding, not as
SQL, so there is no query to copy — reconstruct one from those parts and run
it. For each widget, write:

- what it means in plain terms, one or two sentences;
- the reconstructed query, as a `databricks-sql` block;
- its result, inline as the block's `#+RESULTS:`;
- which filters reach it and which do not — a widget on a different dataset
  than the filter often silently ignores it.

Group findings by which datasets a widget uses; widgets sharing a dataset
usually share the same filter blind spots and window rules.

**Done when:** every widget has a plain-language explanation, a runnable
query, and a recorded result.

## 5. Compare claim against compute

For every widget, hold its claim (title, description, axis label) against
what its query actually returns, and its filters against what actually
governs it. Read [the common failure patterns](references/patterns.md) before
this pass — they name the shapes these gaps tend to take (unit mismatches,
window mismatches, partial-period artifacts, and more) so you recognize one
without having to rediscover it from scratch.

A finding is any gap between claim and compute, however small — record it
even if it looks cosmetic. Whether it is worth fixing is a decision for step
7, not a filter here. A title or description too thin to judge the widget
against is itself a finding — write "intent unstated" against it rather than
inferring what it probably meant; an inferred intent you invented is not part
of the contract from step 1.

Treat every finding as provisional until step 6 has had a chance to break it
— re-examine one that looks too clean, the way a "these two counters are
identical" claim can dissolve into "same expression, different filter" on a
second look. Recording a wrong finding is worse than recording none.

**Done when:** every widget has been checked against every pattern in the
reference, and every gap found is written down.

## 6. Verify beyond the dashboard's own definitions

The dashboard JSON, and the dataset it points at, are both things the
dashboard *says* — neither is proof of what a reader actually sees or what
the data actually holds. Check three things beyond them, and refute or
confirm each claim sourced from the JSON alone explicitly in the document
rather than silently editing it — a claim that looked true from the JSON and
false on the page is itself worth recording:

- **The rendered page.** Open the dashboard in a browser. Does a filter
  actually reach the widgets it claims to? Does a counter's description match
  a forced refresh, not just the number on load — the page can serve a
  cached result that is tens of minutes stale. Is there a **draft/published**
  split, and which one is live for readers — a draft can differ from
  published in both its numbers and the warehouse it runs on.
- **The raw source, bypassing any materialized view.** If a dataset reads a
  materialized view, re-derive the same number straight from the source
  table the view is built on. A gap between the two usually means the MV's
  refresh schedule is decoupled from the dashboard, and a resulting lag
  concentrates in the most recent, least-complete period.

**Done when:** every claim sourced from the JSON alone has been checked
against the live page, and every dataset built on a materialized view has
been cross-checked against its raw source.

## 7. Write the findings

One table, one row per finding: number, widget, claim, what it computes, and
a status. Below the table, one subsection per finding with the evidence
(queries, counts, excerpted view logic) that proves it. Leave the status open
and the issue-tracker column blank for now — step 9 fills both once a finding
has actually been filed and dispositioned, not before.

**Done when:** every finding from steps 5 and 6 has a table row and a
subsection.

## 8. Second pass

Re-read the findings once, specifically for two things the first pass tends
to miss because it is busy checking numeric correctness: chart *encoding*
(axis scale, whether comparable charts share one) and *data completeness*
(the current period's last point, cached loads). Add any findings this
surfaces to the same table and renumber to keep it in finding order.

**Done when:** encoding and completeness have been checked across the whole
dashboard, not just the widgets already flagged.

## 9. Close out

File each finding on whatever tracker the project already uses, matching an
existing precedent's style if one exists — but only findings that survived
step 6; a finding that never got its live-page or raw-source check is not
ready to file. Get the requester to disposition every filed item explicitly
(fixed, accepted as designed, or skipped, each with a one-line reason) rather
than leaving them open by default, then mirror that disposition back into the
finding's status in the document so the tracker and the document agree — a
short status (five to ten words) is enough; the subsection above it already
carries the evidence.

Once every finding is either filed-and-dispositioned or resolved directly in
the document, merge the review's branch and remove its worktree.

**Done when:** every finding's status in the document matches its tracker
disposition (or has none, because it was resolved in the document directly),
and the working branch is merged.

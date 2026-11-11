---
name: review-workflow
description: How the analyst reviews Claude's data work in Assay. Use before writing SQL for a new question, when a finding changes an analysis's answer, method or evidence, when asked whether a method, a query or an output is right, and at wrap-up.
---

# Review workflow

The analyst judges Claude's work from the top: specs, overviews, checks and trusted pieces, never by reading whole
queries. The design and its reasons are in `WORKFLOW.md` at the root. This skill is the procedure.

## New question → spec-back

1. If the question is still broad (an investigation), explore first: run a few cheap queries, show the results, and
   grill the analyst until you agree on 2–3 target questions. Ask in rounds of 2–4 questions, each with your
   recommended answer first.
2. Write the spec to `analyses/<slug>/lib/specs/<name>.md`, one per query:
   - the question;
   - the unit and grain;
   - the population (each filter, by its dictionary name);
   - each metric's definition;
   - the trusted blocks it will include.
   Link the spec from the analysis overview.
3. Ask the analyst to approve it. Write SQL only once it is approved. Any gap in the spec goes back to the analyst as a
   question; fill no gap silently.
4. In the SQL, include blocks and definitions by name. When you write the same cross-table logic a second time,
   propose a block (Assay's `propose-trusted` skill has the file format).

Done when the spec is approved and every run cites it.

## A query that feeds a decision → the three checks

Run each check separately and record its result as one line in the overview's Evidence section:

- **Method right?** Write the scenarios: one per assumption in the five-point brief that could break, plus 2
  anchors (a big unit far worse than the threshold must be caught; one far better must not). The analyst approves
  the list and the true values. Simulate the scenarios, run the method and a simple rule on them, and show one table
  of bad units caught and good units wrongly caught, per rule and unit size.
- **Built right?** Hand the approved spec, and only the spec, to a model from a different family than yours, which
  builds its own version: Codex first; if Codex is unavailable, an Opus model in Copilot. If you are that model, pick
  the other one. Run both versions on the same data and trace every unit that differs. Add checks short
  enough to read at a glance (row counts, grain, totals).
- **Output right?** Show three things:
  - a backtest: did units flagged in the past stay bad?
  - the result against the system overview's Normal values;
  - a diff against the previous version, with every changed decision grouped by cause.

## Finding changes the picture → rewrite the overview

1. Rewrite the affected section of `analyses/<slug>/overview.md`. Move a fact that will outlast the analysis up to
   `systems/<system>.md`. Keep the analysis overview's sections in this order:
   1. Question (and the decision it feeds);
   2. Answer (at most 5 sentences);
   3. Method (a diagram and the five-point brief, one line per point);
   4. Evidence (one line per check, at most one table, each number cited `[<slug> q N]`);
   5. Open questions (one line each, with who must rule).
2. Write in the present tense, as a short paper states its result. History lives in notes, threads and git.
3. Keep each overview to about 50 lines (the tab turns amber above that). Move longer material, such as formulas, to a
   note and link it.
4. Tell the analyst which sections changed. They review the change in the Overview tab's diff (`d`).

## Explaining a method → five-point brief

Explain any method in five points:

1. the problem it solves;
2. why it beats a simpler method;
3. what it assumes;
4. where it breaks;
5. the evidence that it works here.

Give a formula only when asked. Leave out details that change no decision, and say that you left them out.

## Threads

Park a thread only for a ruling a person must make, and name who must rule. Questions about understanding are
answered in the reply or written into the overview.

## Wrap-up

When the session wraps up (in Assay, after its `wrap-up` skill), check that both overviews match the notes:

- every Evidence line cites a run that a note also cites;
- every open question is an open thread, or is marked as needing a ruling.

Fix any mismatch before you stop.

# Patterns

One recipe per kind of page. Each lists the sections in reading order (they sit between the answer box and the next-action box) and the template components to use. "Example" is a page from <https://thariqs.github.io/html-effectiveness/>; fetch it when you want to see the pattern rendered, and take its structure, never its colours.

| The user wants | Kind |
|---|---|
| to understand an idea, a method, a domain | Concept explainer, Method explainer |
| to understand code, a feature, a pipeline, a query | Code explainer |
| options to choose from | Side-by-side options, Brainstorm |
| their unknowns found before work starts | Blindspot pass, Interview |
| proof they understood a change or a topic | Quiz |
| a plan, a change described, a run recorded | Plan, Change writeup, Run notes |
| findings, results, state | Analysis report, Experiment readout, Model evaluation, Status report, Incident report |
| something to present | Deck |

## Explain

### Concept explainer
Teaches an idea well enough that the reader's next prompt uses a professional's words.
1. The mental model: 3 to 5 steps in one strip (`stats` or an SVG).
2. A live figure the reader can change, with the cause and the effect both visible.
3. Vocabulary ladder: a table of term, plain meaning, and one sentence that uses it the way a practitioner would.
4. Common mistakes, each a `note warn`.
5. Compared with the neighbouring ideas: a table.

Example: `15-research-concept-explainer.html`, `unknowns/02-color-grading-explainer.html`.

### Method explainer (statistics, ML)
A concept explainer whose live figure is a **simulation**: the reader moves sample size, effect size, noise, regularisation or a threshold and watches the estimate, the interval or the decision boundary respond.
1. The question the method answers, with one concrete case from the user's own data or domain.
2. The simulation, with a "resample" button so variation is felt.
3. What each parameter does: one fold per parameter, each ending in "raise it when".
4. Assumptions, and what breaks when each fails (`note warn`).
5. Vocabulary ladder, then how to run it: a `tabs` block with the code in the project's language.

### Code explainer
How a feature, module, pipeline or query works in this repo.
1. A map: SVG boxes and arrows, the hot path highlighted, real names on every box.
2. The path step by step: one fold per step with `file:line` in its `where`, the first one open.
3. How to change or configure it: `tabs` with the files involved.
4. Gotchas (`note warn`), then questions a newcomer asks, as folds.

For SQL or a data pipeline, the map is the lineage (source tables to output) and each step states the grain after it.
Example: `14-research-feature-explainer.html`, `04-code-understanding.html`, `13-flowchart-diagram.html`.

## Explore (reply box)

### Side-by-side options
2 to 4 ways to do one thing, rendered next to each other on the **same** input so only the approach varies.
1. The shared case every option is shown on.
2. `options`: per option the code or mock, what it costs, when it wins; one radio `data-pick` each.
3. A comparison table on the 3 to 5 properties that differ.
4. Your recommendation, labelled as yours, with the fact that would change it.

Example: `01-exploration-code-approaches.html`, `unknowns/03-design-directions.html`.

### Brainstorm
The whole option space, ordered cheapest to most ambitious, each idea grounded in something that exists.
1. What you searched and the pattern you found.
2. A spectrum figure: the ideas as numbered dots from "this afternoon" to "a quarter".
3. One card per idea: where it lives (`file` or table), the evidence, the expected effect, the size (S/M/L); one checkbox `data-pick` each.

Number the ideas; the reply names them by number and title.
Example: `unknowns/05-churn-brainstorm.html`.

## Decide (reply box)

### Blindspot pass
What the user does not know they do not know about the area they are about to touch.
1. What they asked for, and what they are walking into: two short boxes.
2. `stats`: counts by type (landmines, unwritten conventions, missing concepts, earlier attempts).
3. One card per blindspot: the evidence (`file:line`, commit, incident), why it bites, and a sentence to add to the prompt; a checkbox `data-pick` whose value is that sentence.

The reply is the better prompt, assembled from the picked sentences.
Example: `unknowns/01-blindspot-pass.html`.

### Interview
The open questions about a vague request, ordered by how much the answer changes the design.
1. One card per question: why it matters, 2 to 4 answers as radio `data-pick` (group = the question), your recommended answer marked.
2. What you will assume for anything left unanswered.

Example: `unknowns/06-interview.html`.

### Quiz
A report the reader must prove they read.
1. The mental model: one before-and-after figure.
2. What changed, and why, in 3 to 4 sections.
3. 5 to 7 `quiz` questions on consequences ("what happens when ...") whose `data-explain` names the section to reread.

A quiz has no reply box: the score is the result.
Example: `unknowns/11-change-quiz.html`.

## Plan and review

### Plan (reply box)
Sorted by how likely the reader is to change each part, with the mechanical work last.
1. `stats`: effort, files touched, risk, migrations.
2. Decisions you will probably change: per decision the choice, the alternative considered (`tabs` to compare), and a `data-pick` for each.
3. Build order: a `timeline` of slices, each reviewable alone.
4. Risks: a table of risk, likelihood, how it is caught.
5. Mechanical work: one closed fold.

Example: `unknowns/08-implementation-plan.html`, `16-implementation-plan.html`.

### Change writeup
A change described for its reviewers: a PR, a refactor, a migration.
1. Why, and the behaviour before and after (`tabs` or two columns).
2. A tour file by file, in reading order: one fold per file with the reason for the change and the diff lines that matter (`pre` with `add` and `del`).
3. Where to look hardest: the 2 to 3 places you are least sure of.
4. How it was tested, with the command output.

Example: `17-pr-writeup.html`, `03-code-review-pr.html`.

### Run notes
The log of a long task: what matched the plan and what did not.
1. `stats`: entries, deviations, items that need the user's judgement.
2. A `timeline`, each entry tagged as planned, discovery or deviation; a deviation states the conservative call you made.
3. For the next attempt: 3 bullets to put into the next prompt.

Example: `unknowns/09-implementation-notes.html`.

## Report

Every number on a report carries its unit, period and population, and traces to a query, a file or a command listed in provenance.

### Analysis report
One analytical question answered from data.
1. `stats`: the 3 to 5 numbers that carry the answer.
2. The evidence: one figure per claim, the claim as the section heading ("Churn is concentrated in week 1").
3. Method: population, filters, metric definitions, period; the SQL behind each number in a closed fold.
4. Caveats and what could overturn the answer (`note warn`).

### Experiment readout
An A/B test or a causal estimate, written so the decision is clear.
1. The decision and the effect with its interval, in the answer box.
2. Design: hypothesis, unit of randomisation, arms and sample sizes, dates, primary and guardrail metrics.
3. Validity checks: sample-ratio mismatch, pre-period balance, exposure; each tagged good, warn or bad.
4. Results: a figure of effect and interval per metric (primary first, guardrails after), then a table with the numbers.
5. Segments, marked as exploratory.
6. What the result does not show.

### Model evaluation
1. `stats`: the headline metric against the baseline, on which data, of which date.
2. Metrics table: the model and the baseline side by side, with intervals.
3. Where it fails: performance by slice as a figure, worst slices first.
4. Calibration or threshold trade-off: a figure, live when the threshold is a choice.
5. Error examples: a few real cases per error type in folds.
6. Data and leakage checks; what was not evaluated.

### Status report
1. `stats`: the period's counts with the change against the last period.
2. Shipped, slipped, next: three short lists or a table with a `tag` per row.
3. One small chart of the trend that matters.
4. Risks and asks.

Example: `11-status-report.html`.

### Incident report
1. `stats`: severity, duration, impact.
2. A `timeline` by the minute, with log excerpts in folds.
3. Root cause, then what made it worse.
4. Follow-ups: a table of action, owner, date.

Example: `12-incident-report.html`.

## Deck

One claim per slide, the claim as the slide's heading, at most 10 slides. Slide 1 is the title and the conclusion; the last slide is the ask plus the provenance fold. Figures follow `FIGURES.md`. Arrow keys move between slides; printing gives one slide per page.

Example: `09-slide-deck.html`, `unknowns/10-pitch-doc.html`.

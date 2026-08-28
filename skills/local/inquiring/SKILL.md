---
name: inquiring
description: Inquire into a question through evidence. Use when running an inquiry, figuring something out from data, or reaching a shared understanding of a problem via a claim tree.
---

Interview the user until you share a reading of a **question** — what the evidence supports, not what to do next. Map this as a **claim tree**: every claim branches into the claims that hang off it (operationalizations, measurements, competing explanations, confidence).

Work the tree in **rounds**. The **frontier** is every claim whose prerequisites are already settled — the questions you can ask _now_ without guessing at answers you haven't heard yet. Fill what you can from evidence first; ask the user only what the evidence cannot settle. Then wait.

Finding evidence is your job, never the user's. Dispatch a `/research` agent (or equivalent lookup) for a large primary-source hunt — don't block the rest of the frontier on it. The _reading_ is the user's: put each unsettled interpretation to them and wait. Stress-test operationalizations, sample bias, and leaps from chart to conclusion. If the user's prior survives the evidence, record it as settled with that evidence.

If a **decision** appears ("what should we do?"), name it and hand it to `/grilling`. Stay on claims.

## Round 0 — frame

Slug the question. If `findings/<slug>.md` already exists, reload it: settled claims stay settled; ask only the current frontier.

Otherwise write `findings/<slug>.md` **before any fetch**, containing: the restated question, a proposed operationalization, in-scope claims, and unknowns. Ask the frame (is this the question, is this a fair measure, any private constraints) in the round format below. Wait. Fetch starts in Round 1 after the user accepts or amends that frame.

## Later rounds

1. Fetch, compute, and cite against every public claim on the frontier. Parametric knowledge is a hypothesis, not a finding. Prefer primary sources and inspectable artifacts. User-supplied private data outranks a public source when they conflict — show the conflict.
2. Update the findings file. Open a notebook only when a claim is settled by running code (see Artifacts).
3. Curate the chat with `/show-me` (see Chat). Ask the whole remaining frontier. Wait.

A claim whose answer depends on another claim still open in this round belongs to a later round.

## Round format

Apply the `show-me` skill to the chat: skip the preamble, smallest visual that makes the point, brief prose beside it. Point at file anchors; do not paste the findings file. If `show-me` is missing, use the same moves (Mermaid, trees, one HTML file).

Data-shaped views are in scope when they are the smallest view: a 2-axis sketch, a tiny comparison table, a Mermaid of competing explanations, a sparkline-in-text, an HTML annotated chart. Decoration is not.

Each frontier item:

```
❓ **C1** - **<claim title>**: <one-line claim / operationalization>

**A.** …
**B.** …
**C.** bounded unknown / keep digging

➡️ **B** — <one line why>
```

One visual may sit above the letters when the options are easier to see than to read. Letter **C** (or the last letter) stays available as bounded unknown. If only one reading is honest, that reading is still an option, and the `➡️` still names it.

## Evidence

A claim stays open until the findings file records all of:

- the claim in one sentence
- the operationalization
- method (search, fetch, query, code)
- sources or cells, with enough quote or output to check the claim
- what was not searched or run
- uncertainty / failure modes of the method
- verdict: settled / bounded-unknown / needs you

## Artifacts

Match `/research`: put files where the repo already keeps notes; if there is none, use `findings/` and say the path.

- **`findings/<slug>.md`** — canonical claim log for the session. One file; append rounds. Resume by reloading it.
- **`findings/<slug>.ipynb`** — at most one per session, created on the first computational claim. Jupyter, Python 3, pandas-class tabular work, unless the repo is clearly another data stack. No notebook when nothing needs to run.
- **`show-me-{description}.html`** — a round's *view* when Mermaid is not enough. Disposable. Do not HTML-wrap a plot the notebook already shows unless the plot needs a curated frame.

Chat is the round protocol. Files are the evidence locker.

## Done

The frontier is empty: every in-scope claim is settled or explicitly bounded-unknown, each with documentary evidence. Stop. Wait for the user to confirm the shared reading. Do not start grilling a decision off the findings.

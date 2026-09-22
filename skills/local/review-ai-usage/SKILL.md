---
name: review-ai-usage
description: Review local AI-agent transcripts into a personal Org casebook.
disable-model-invocation: true
---

# Review AI usage

Review newly completed work from Codex, Claude Code, Copilot CLI, Cursor CLI,
and Copilot in VS Code. Keep transcripts, configuration, state, manifests, and
the casebook on this machine.

The directory containing this file is the **skill directory**.

## 1. Preflight

Run `command -v ai-transcripts`. If it is absent, stop and give the user this
command, replacing `<skill-directory>` with the resolved directory:

```text
uv tool install <skill-directory>
```

Run `ai-transcripts config`. If configuration is absent, ask only for the
machine label (`personal` or `work`) and casebook path, then run
`ai-transcripts init --machine <label> --casebook <path>`. Stop after reporting
the detected sources so the user can review exclusions before the first scan.

**Done when:** the executable and reviewed local configuration exist.

## 2. Establish the boundary

Read the state path shown by `ai-transcripts config`. The `collect` command is
deliberately stateless: use each source's last successful watermark from the
state index to calculate the boundary passed to it. A source without a
watermark starts 24 hours before the run. A user-supplied period or source list
overrides this boundary for the run.
Resolve relative boundaries to timestamps and record those timestamps in the
run manifest. Treat the first seven days as a supervised pilot; scan no earlier
history unless the user asks for a bounded backfill.

Run `ai-transcripts collect` with the chosen boundary and enabled sources.
Capture stdout for analysis and stderr for source status. Treat an unavailable
source as informational. A detected source that cannot be read is a failure.

Analyse every emitted event, grouping related sessions into projects or tasks.
Use completed turns only. Follow [the evidence rules](references/evidence.md).

**Done when:** every collected conversation is grouped, skipped with a reason,
or attached to a visible source failure.

## 3. Write a pending run

Append one neutral run to the configured Org casebook:

```org
* AI usage review — DD.MM.YYYY — MACHINE :AI_REVIEW:PENDING:
:PROPERTIES:
:RUN_ID:   UUID
:END:

** Conversations
** Cases
** Interventions
** Lessons
** Extraction
```

Under `Cases`, use the natural `Project — Task` title. Put `new-case` or
`update` in a `CHANGE` property and the exact existing heading in `TARGET` when
applicable. Tag machine-generated cases or updates `PENDING`.

```org
*** Project — Task :PENDING:
:PROPERTIES:
:CHANGE: new-case
:END:

*** Existing project — Existing task :PENDING:
:PROPERTIES:
:CHANGE: update
:TARGET: Existing project — Existing task
:END:
```

Under `Lessons`, use a concise lesson as the heading and tag it
`:LESSON:PENDING:`. Record the machine, evidence count, and supporting case
headings in properties:

```org
*** Prefer bounded verification :LESSON:PENDING:
:PROPERTIES:
:MACHINE: personal
:EVIDENCE_COUNT: 1
:CASES: Project — Task
:END:
```

Keep work content privacy-safe.

Under `Extraction`, list every source as healthy, unavailable, or failed. Under
`Conversations`, include a compact skipped list as well as included sessions.

Read [the state contract](references/state.md). After the pending Org run is
written, write the run manifest beside the configured state file, then update
the state index atomically. Neither contains message text. Do not advance state
before the casebook and manifest exist; `collect` itself must not advance it.

After the casebook and manifest both exist, advance watermarks for healthy
sources to their latest emitted event. Leave failed-source watermarks unchanged.

**Done when:** the pending run, manifest, and healthy-source watermarks agree on
the same run ID and evidence set.

## 4. Present the review

Show, in this order:

1. conversations examined and source status;
2. case findings and intended destinations;
3. work observed from the agent and the user;
4. substantive interventions;
5. facts requiring the user's confirmation;
6. candidate lessons;
7. skipped conversations and failures.

Ask for one response covering approval, corrections, and rejections. Accept
natural-language decisions.

**Done when:** the user has decided every pending case, update, and lesson.

## 5. Resolve the run

Apply approved new cases as stable `:AI_LOG:CONFIRMED:` level-one headings.
Apply approved updates as dated `:CONFIRMED:` level-two headings under the exact
target case. Existing untagged `AI_LOG` entries are already confirmed.

Keep confirmed lessons under the run and change their state to
`:LESSON:CONFIRMED:`, adding a `CONFIRMED` property in `YYYY-MM-DD` form. Remove
rejected material. Replace duplicated case details in the run with a compact
decision summary, and change the run state from `PENDING` to `COMPLETE`. Record
every decision in the private manifest.

For cross-machine reconciliation, run `ai-transcripts export-learnings`. Give
the user the Org fragment for manual review; never import or merge it
automatically.

**Done when:** no `PENDING` item remains in the run and the casebook and manifest
contain matching decisions.

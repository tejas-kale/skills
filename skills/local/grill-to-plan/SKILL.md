---
name: grill-to-plan
description: Grill a data-analysis or software request into an agreed plan for delegated work.
disable-model-invocation: true
---

# Grill to plan

Turn the request into an agreed plan. Do not implement it.

## Choose the flow

Classify the request by its primary uncertainty:

- **Data analysis:** evidence, populations, metrics, methods, or interpretation. Read [the data-analysis flow](references/data-analysis.md), then run a `/grilling` session with those additional rules.
- **Software design:** system behaviour, interfaces, or architecture. Run `/grilling` using `/domain-modeling`, as `/grill-with-docs` does.
- **Mixed:** settle the data-analysis branch first, then run the software-design branch. Do not design software around unsettled data assumptions.

When a data-analysis branch contains a factual question that available evidence can settle, use `/inquiring` for that claim. Return its findings to the design tree. Keep claims in inquiry and decisions in grilling.

Reuse the named skills rather than restating their instructions. If a required skill is unavailable, name the missing capability and tell the user the next manual action. Do not invent a substitute workflow.

## Finish

Wait until the design-tree frontier is empty and the user confirms the shared understanding. Then write the agreed artefact. For a data-analysis or mixed flow, copy and complete [the Org plan template](references/plan-template.org). Follow an existing repository convention; otherwise write `plans/<analysis-slug>.org`.

For a software-only flow, the confirmed conversation and any glossary or ADR updates are the agreed plan for `/to-spec`; do not force them into the data-analysis template.

Write plain, literal prose in complete sentences. Put the main point first. Use familiar words and one stable term for each concept. Define technical terms when needed.

End by naming the plan status and the exact next action. Do not invoke `/to-spec`, `/to-tickets`, `/inquiring`, implementation, or review automatically.

# Data-analysis flow

Use this reference only for data-analysis and mixed requests. The `/grilling` skill supplies the interview protocol, rounds, frontier, and confirmation gate.

## Completion gates

A `ready` data-analysis branch requires all of these gates:

1. The analysis aim and intended use.
2. The risk tier.
3. The Data Understanding Record.
4. The method and its assumptions.
5. The Verification Contract.
6. The human review boundary and Review Map.
7. The Return Contract.
8. Every unknown is classified.
9. The user confirms the shared understanding.

These are gates, not a fixed interview order. Work the design-tree frontier from `/grilling`.

If missing evidence prevents a gate from being settled, complete everything that can be settled, classify the blocking claims, and recommend `investigation-required`. If the work should remain human-led, recommend `do-not-delegate`. In either case, ask the user to confirm that stopping point before writing the interim plan. Do not pretend that the unopened gates passed.

## Analysis aim

Settle the question, intended use, audience, population, and decision that the result may inform. State what the analysis cannot support. A descriptive analysis may have no immediate decision, but it still needs an intended use.

## Risk tier

Recommend a tier and explain the consequence that determines it. The user decides.

- **Exploratory:** reversible work used to learn. Reproducible retrieval and basic plausibility checks remain compulsory.
- **Decision-support:** results influence a personal or organisational decision. Require reconciliation, sensitivity checks, and explicit uncertainty.
- **Production or external:** repeated, automated, published, or consequential output. Require durable inputs, automated validation, regression evidence, and an independent checking route.

## Data Understanding Record

Settle every item below. Use `not applicable` with a reason or `bounded unknown` with its consequence. Leave nothing silently assumed.

- Exact source and reproducible retrieval method.
- Population and unit of observation.
- Grain, keys, and expected cardinality.
- Field and metric meanings.
- Time semantics, timezone, and observation window.
- Null, sentinel, duplicate, and late-arriving-data behaviour.
- Filters, exclusions, and expected join loss.
- Freshness, coverage, and known bias.
- At least one reconciliation or independent plausibility check.

For Databricks or other tables, also record the catalogue and table identity, snapshot or Delta version when available, extraction query, partitioning, update cadence, join cardinalities, and access-enforced filters.

For internet or API data, also record the canonical URL or endpoint, retrieval time, parameters, pagination, revision or version, licence or usage constraints, raw snapshot or hash when permitted, and known coverage limits.

When access is restricted, prepare the smallest exact query or inspection procedure that would settle the claim. Explain the required result and mark the branch blocked. Ask the user to run it or provide an approved summary. Do not infer private table semantics.

Use the smallest inspectable evidence for sensitive data. Prefer schemas, counts, distributions, aggregates, and redacted samples. Record access constraints and row or column policies. Keep secrets and raw sensitive records out of plans, tickets, and logs. State when privacy limits weaken verification.

## Method

Classify the analysis before testing its assumptions:

- descriptive or diagnostic;
- forecasting or predictive modelling;
- experiment analysis;
- causal or observational inference;
- optimisation or decision modelling.

Use method-specific checks. Generic data checks do not settle leakage, confounding, multiple comparisons, temporal validation, objective choice, or other method-specific risks. Investigate unsettled factual claims through `/inquiring`.

Record analysis-specific choices in a concise **Decision Ledger**. Put durable domain and metric meanings in the project's glossary when one exists. Use ADRs only in the software-design branch when `/domain-modeling` says the decision qualifies. Do not create analysis ADRs.

## Verification Contract

Write every material verification as:

```text
Claim -> Evidence -> Acceptance rule -> Independence -> Human action
```

Tests passing is supporting evidence, not a complete claim.

Scale independence with risk:

- **Exploratory:** use a different view of the same data, such as samples plus aggregate checks.
- **Decision-support:** use a materially different calculation, query, aggregation path, or hand-computed fixture.
- **Production or external:** use an independently implemented check or authoritative reconciliation that does not reuse the claim-critical transformation.

Name shared assumptions between the main route and the checking route.

Choose suitable oracles for each material claim:

- **Micro-fixture:** a small, hand-checkable example with a known answer.
- **Invariant:** a property such as conservation, uniqueness, bounds, monotonicity, or cardinality.
- **Reconciliation:** comparison with an authoritative total or independently computed route.

## Human review boundary

Use two layers:

- **Claim-critical logic:** any code or configuration that can change the data, result, uncertainty, or decision.
- **Human-review-critical logic:** claim-critical logic that can produce plausible but wrong output and lacks a strong automated oracle.

Test all claim-critical logic. Concentrate human review on the human-review-critical subset. Loud failures and decisive automated checks may move code outside the human review boundary.

Automated verification removes code from human review only when the plan names:

1. The plausible failure.
2. An oracle independent of the implementation.
3. A test that fails when that fault is introduced.
4. Evidence that the delegated workflow runs the test.

Keep human-review-critical logic inside the smallest coherent **review boundary** with explicit inputs and outputs. Keep retrieval adapters, persistence, presentation, orchestration, and generic utilities outside when they carry no residual silent-failure risk. Name every component inside the boundary and justify critical logic left elsewhere.

Treat presentation as human-review-critical when a plausible choice in axes, denominators, binning, uncertainty, or selection could change the interpretation without looking broken.

## Org source and generated code

Follow repository instructions first. Otherwise, in a personal analysis repository:

- Put exploratory work in Org.
- Put human-review-critical code in Org.
- Treat the Org source block as authoritative when it tangles to Python.
- Mark tangled Python as generated and never edit it directly.
- Provide one documented tangle command and check generated code for drift.
- Exercise the tangled module in tests where practical.

For production or external work, ordinary source modules may remain authoritative when the repository requires them. Use Org as the review cockpit and avoid duplicating logic.

The agreed Org plan is a living review cockpit. Commit the agreed plan, then let implementation add source blocks, results, evidence links, and Return Contract results beneath the agreed sections. Any changed assumption must be marked explicitly.

## Review Map

Lead the user through claims, not files. For each human-review item, record:

```text
Question to answer
-> Org heading or source block
-> relevant evidence or test
-> expected invariant
-> consequence if wrong
```

Order the map from data selection and semantics, through transformations and method, to uncertainty and conclusions. Include decision-facing tables, charts, and claims. Omit generated and supporting code unless it carries residual silent-failure risk.

## Reproducible execution

Use the repository's existing environment and dependency tools. Record:

- environment and dependency source;
- one command or documented sequence to tangle and run the analysis;
- parameters and date ranges;
- random seeds or stated non-determinism;
- expected generated artefacts;
- one command or sequence to run verification checks.

Do not introduce a new environment manager merely for this plan.

## Return Contract

Require the implementing agent to return:

- the implemented outcome;
- the exact data version or retrieval evidence;
- checks run and their results;
- unresolved or changed assumptions;
- the completed Review Map;
- locations of human-review-critical Org blocks;
- generated or tangled artefacts and the drift check;
- claims it cannot verify for the user;
- the Git review baseline and final commit SHA.

## Unknowns and outcome

Classify every unknown:

- **Blocking unknown:** it could materially change the population, method, result, or interpretation. Implementation must not begin.
- **Bounded unknown:** its consequence is understood and accepted. Record the bound, risk, planned check, and owner.
- **Deferred choice:** it does not affect the current slice. Put it out of scope.

Choose one plan status:

- **`ready`:** no blocking unknown remains.
- **`investigation-required`:** named evidence work must happen before planning can finish.
- **`do-not-delegate`:** the judgement, ambiguity, or risk is too high for delegating the whole task.

For `investigation-required`, finish with this reminder, filled with actual paths and claims:

```text
Next: run /inquiring for the blocking claims under "Unknowns and out of scope" in <plan-path>. Afterwards, resume /grill-to-plan with <plan-path> and the findings file.
```

For `do-not-delegate`, divide the work into human-owned judgements, safe agent-owned preparation, required independent review, and conditions that would make further delegation safe.

For `ready`, state the next handoff:

- In the same conversation, the user may invoke `/to-spec`, then `/to-tickets`.
- In a later conversation, tell the agent to read the complete Org plan and treat it as agreed context before invoking `/to-spec`.

Do not copy or modify those externally owned skills.

## Git delegation gate

Git is compulsory. A `ready` plan cannot enter implementation until:

1. The plan and any local ticket artefacts are committed.
2. The working tree is clean.
3. The implementing agent captures `git rev-parse HEAD` before its first implementation change.

The agent records that review baseline and the final commit SHA in the completed Return Contract. GitHub issues do not change the working tree and may be created before the baseline is captured.

After implementation, remind the user to:

1. Run `/code-review` against the review baseline, using the Org plan or resulting spec as the specification source.
2. Follow the Review Map, inspect every human-review-critical block, and perform the human actions in the Verification Contract.

# Skill mechanics

The skill-specific branch of [`writing-for-agents`](SKILL.md): what a skill
_is_, then frontmatter, invocation, and router skills. Everything else about
writing it is the universal reference in `SKILL.md`.

Write the prose of this file in the voice in
[`../../local/plain-writing/SKILL.md`](../../local/plain-writing/SKILL.md).

## Procedural anchor

A skill is a **procedural anchor**: ordered steps, tool sequence, intermediate
checks, recurring pitfalls. It stabilises how the agent acts. Facts, decisions,
and one-line corrections belong in memory or an instruction file.

Write a skill when the reusable thing is operational: environment setup,
output/schema, service lifecycle, command patterns. A better algorithm, a
one-task path, or a plea to verify harder is not a skill.

When you write or edit a skill:

- Distill. Keep the procedure. Drop failed branches, exploration, and
  harness-specific residue.
- Keep outcomes explicit: which path worked, which failed.
- Prefer **edit** an existing skill over a near-duplicate. Similar descriptions
  confuse later retrieval.
- Name when it applies and the check that says stop following it.

## Invocation

Two choices, trading the two loads.

A **model-invoked** skill keeps a `description`, so the agent can fire it
autonomously, and other skills can reach it. You can still type its name.
Model-invocation always includes user reach. A description only ever adds
agent discovery. It never removes the human's. The description is the skill's
top-level context pointer, forced to stay loaded at all times: permanent
context load in exchange for discoverability. A model-invoked skill whose
content is all reference is also one home for shared reference. Another skill
can invoke it, so reference needed by several skills lives in one place.
Mechanics: omit `disable-model-invocation`, and write a model-facing
description carrying the trigger branches. The pointer-writing rules in
`SKILL.md` apply in full.

A **user-invoked** skill strips the description from the agent's reach. Only
the human typing its name can invoke it. No other skill can fire it. Zero
context load, but it spends cognitive load. You are the index that must
remember it exists. Mechanics: set `disable-model-invocation: true`. The
`description` becomes human-facing: a one-line summary, trigger lists stripped.

Pick model-invocation only when the agent must reach the skill on its own, or
another skill must. If it only ever fires by hand, make it user-invoked and pay
no context load.

Shared reference that two user-invoked skills both need can live in neither.
With no descriptions, neither can fire the other. Push it to a plain file
outside the skill system: external reference any skill can point at. That is
how [`writing-for-agents`](SKILL.md) reaches `plain-writing`: it points at the
markdown file.

## Splitting by invocation

The invocation cut of splitting (the sequence cut lives in `SKILL.md`): split
off a model-invoked skill when you have a distinct leading word that should
trigger it on its own, a trigger word you actually use in your prompts, or
another skill must reach it. You pay context load for the new always-loaded
description, so that independent reach has to be worth it.

## Router skills

When user-invoked skills multiply past what you can remember, that piled-up
cognitive load is cured by a **router skill**: one user-invoked skill that
names the others and when to reach for each, so the human has one skill to
remember instead of many. It can only hint, never fire them. User-invoked
skills have no model-facing description, so nothing but the human can reach
them.

---
name: plain-writing
description: Plain, boring prose for people.
disable-model-invocation: true
---

# Plain writing

The user typed `/plain-writing`. Draft or edit the prose they named. If they
also said **deslopify**, read [`DESLOPIFY.md`](DESLOPIFY.md) and rewrite the
previous reply. Apply to the words around code, not to code.

## Voice

Write **plain**, **boring**, and **literal** prose in **complete** sentences. Put
the main point in the first sentence of a paragraph, then support it.

**Plain.** Everyday words a coworker would say out loud. Keep one term for one
thing. Domain terms already in the work are fine. Define them once if the
reader may not know them.

Before: We leverage the cache to unlock a more robust query experience.
After: We use the cache to make repeated queries faster.

**Boring.** Descriptive and explanatory. Headings and labels name the thing.

Before: Legal requirements as a floor.
After: Applicable legal constraints.

**Literal.** Describe the thing itself. Name the person or process that acts.

Before: The feature index is like a card catalog that the optimizer can flip
through.
After: The feature index is a list of named features. The optimizer can look
up which feature matches a request.

**Complete.** Each sentence has a subject and a verb. Join related ideas with
"and", "because", or "so".

Before: The agent polls the file and reacts to changes, and the team meets on
Tuesdays.
After: The agent polls the file and reacts to changes. The team meets on
Tuesdays.

## Checkable set

A pass is done when every heading, sentence, and list item would survive a
native-speaker edit for this voice.

- Everyday words and stable terms already in the work. Contractions are fine.
  One name for one thing. No coined label, hyphenated invention, or metaphor.
- Complete sentences. Ranges use "to". Join clauses with a period or "and",
  not an em dash.
- A paragraph opens with the point, then support. In chat, one or two
  sentences of problem context, then what changed. Skip the setup in an
  essay.
- Headings are sentence case. Lists stay at three or four points. Nest the
  rest.
- Precise: say who does what, or by what mechanism. Cut padding clauses
  ("as we move forward", "before we call the work done").

Before: Upload the document. The file is parsed, and the record is saved.
After: Upload the document. The document is parsed and saved.

Before: The exporter now waits on the reset header, and `dotnet test` is green.
After: The Okta System Log exporter was rereading whole hours, so a retry
could write the same event twice. It now waits using the response reset
header, and the six acceptance tests pass.

If a line still reads as a slogan, a guess, or a flourish, rewrite it until it
states a fact.

Common model tells: [`TELLS.md`](TELLS.md). Punctuation trivia (colons, curly
quotes, middle dots): [`PUNCTUATION.md`](PUNCTUATION.md).

## Sequence and length

**Order.** When the reader must execute steps, put them in order. Number them
only then. Ordinary explanation can stay in running prose.

Before: The groups the features were sorted into were the authors' own
reading, the example posts were written by hand, and finer detail meant
training extra small models and labeling again.
After: The authors sorted the features into groups from their own reading.
They wrote the example posts by hand. When they wanted finer detail, they
trained another small model and labeled the posts again.

**Explain out loud.** Prefer longer sentences with commas over a stack of
fragments. A sentence can hold one or two related clauses. If you need more
points, start a new sentence or a short list. Do not require "Moreover" or
"For example" as a connective.

Before: The gate runs on every merge. It blocks regressions. Nobody bypasses
it.
After: The gate runs on every merge, and it blocks changes that fail a
regression case. A regression cannot make it to production unless someone
deliberately overrides the check.

Before: Most renders are fast. For example, the parser skips files with no
changes, so the server returns early. Moreover, the cache keeps the previous
output, so a repeated render does no work.
After: Most renders are fast. The parser skips files with no changes, so the
server returns early. The cache keeps the previous output, so a repeated
render does no work.


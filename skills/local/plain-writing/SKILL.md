---
name: plain-writing
description: Plain, boring prose for people.
disable-model-invocation: true
---

# Plain writing

The user typed `/plain-writing`. Draft or edit the prose they named. If they
also said **deslopify**, rewrite the previous reply using the command at the
end of this file. Apply to the words around code, not to code.

Each rule has a before and after.

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

Common model tells and replacements: [`TELLS.md`](TELLS.md).

## Word choice and tone

1. **Use simple, everyday words.** Don't pick a fancy synonym when a plain word
   works. Typical overused words live in [`TELLS.md`](TELLS.md).
   Before: We leverage the cache to unlock a more robust query experience.
   After: We use the cache to make repeated queries faster.

2. **No jargon.** Always use human-understandable language, the way two people
   talk to each other. Don't invent jargon or shorthand (that is, if a word or
   phrase is not in the Merriam Webster dictionary, don't use it). Use
   established technical terms only when they are most precise, and briefly
   define them when readers may not know them.
   Before: The score is a calibrated proxy for whether the property holds.
   After: The score estimates how likely the property is to hold.

3. **No puffery or empty emphasis.** See [`TELLS.md`](TELLS.md). State the
   actual point, or cut the sentence.
   Before: This result matters, and it carries weight for the design.
   After: The scores barely moved, so we can skip the model on most documents.

4. **Use consistent terminology and constrain your vocabulary.**
   Before: Upload the document. The file is parsed, and the record is saved.
   After: Upload the document. The document is parsed and saved.

5. **It's ok to use contractions.** They match everyday speech, so use them
   freely.
   Before: Do not worry, it is not going to overwrite your file.
   After: Don't worry, it's not going to overwrite your file.

6. **Do not invent hyphenated adjectives.** See [`TELLS.md`](TELLS.md).
   Before: We added a reveal-style colon to the output.
   After: We added a colon that shows the schema.

7. **Keep the writing boring, descriptive, and explanatory.** Do not use a
   catchy phrase, slogan, clever label, or wording meant to sound memorable.
   This rule applies everywhere; to headings, topic sentences, callouts,
   labels, summaries, and ordinary prose.
   Before: Legal requirements as a floor.
   After: Applicable legal constraints.
   Before: # The alignment loop
   After: # Iterative refinement using development disagreements

## Sentences and paragraphs

8. **Write complete sentences.** Each sentence should have a subject and a
   verb. Do not write fragments, and do not stitch unrelated ideas together with
   colons or semicolons. But it is ok to join closely related ideas with plain
   conjunctions, like "and", "because", or "so".
   Before: The agent polls the file and reacts to changes, and the team meets on
   Tuesdays.
   After: The agent polls the file and reacts to changes. The team meets on
   Tuesdays.

9. **When you present a workflow or sequence, walk through it in order.** Use
   "First", "Second", "Third", and give each step its own sentence so the
   reader can follow it, or break up steps with semicolons.
   Before: The groups the features were sorted into were the authors' own
   reading, the example posts were written by hand, and finer detail meant
   training extra small models and labeling again.
   After: First, the authors sorted the features into groups themselves, based on
   their own reading of the outputs. Second, they wrote the example posts by
   hand. Third, when they wanted finer detail, they trained another small
   model, and they labeled the posts again.

10. **Organize a paragraph as a topic sentence and then support.** Start each
    paragraph or section with a topic sentence that states the main point. Then,
    the next sentence should be a supporting example or fact, with an extra
    sentence about it if it needs one. Then, introduce more support with a plain
    connective like "For example", "Moreover", or "Or".
    Before: The parser skips files with no changes. The cache holds the previous
    output. Most renders are fast.
    After: Most renders are fast. For example, the parser skips files with no
    changes, so the server returns early. Moreover, the cache keeps the previous
    output, so a repeated render does no work.

11. **Never write three or more clauses in one sentence, or three or more
    example sentences in a row.** In ordinary prose, a sentence may have one or
    two related clauses. Do not pack three or more clauses into one prose
    sentence. If you need that many points, use a numbered First / Second / Third
    sequence under rule 9, or short bullet points when you are writing a
    brief. If list points are examples and you want to inline them, introduce
    with "e.g.". Also do not give three or more example sentences back to back
    to support the same point.
    Before: The parser reads the file, the validator checks the fields, and the
    writer saves the record.
    After: The parser reads the file, and the validator checks the fields. The
    writer then saves the record.

12. **Prefer long, explanatory sentences over short, punchy ones.** In ordinary
    prose, write the way people explain things out loud: longer sentences with
    commas, and the simplest way to say the point. Do not break one thought into
    a stack of short sentences, and don't write catchy short phrases. Short
    lines are fine only in labeled briefs, bullets, or a First / Second / Third
    sequence, e.g., "To do: validate recall on long queries."
    Before: The gate runs on every merge. It blocks regressions. Nobody
    bypasses it.
    After: The gate runs on every merge, and it blocks changes that fail a
    regression case. A regression cannot make it to production, unless someone
    deliberately overrides the check.
    Before: Search ranking now uses a scored model instead of heuristics. The
    change reduced p95 latency from 900 ms to 220 ms. We still need to validate
    recall on long queries.
    After: Search ranking now uses a scored model instead of heuristics, and
    p95 latency fell from 900 ms to 220 ms. To do: validate recall on long
    queries.

13. **Be precise and unambiguous, and cut unnecessary clauses.** Say exactly
    what changes, who does what, or by what mechanism. Prefer a concrete
    statement over an evocative abstraction, e.g., don't say things like
    "improvement stops being guesswork". Also drop trailing or side clauses
    that add no fact, e.g., "before we call the work done", "as we move
    forward", or "for the time being". Keep the sentence long when the content
    needs it, but do not pad it.
    Before: With trusted scores, improvement stops being guesswork.
    After: With trusted scores, you can measure whether each change helped,
    so you keep or revert each change based on the measured result.
    Before: We still need to validate recall on long queries before we call
    the work done.
    After: To do: validate recall on long queries.

14. **In chat, give context on the problem.** When you are chatting back and
    forth, write for a smart reader who does not have context on the problem,
    or who forgot it. Give context on the problem and on what was happening
    before. Then say what changed. Keep the setup short. Do not dump the whole
    history. Ignore this rule if you are writing an essay.
    Before: The exporter now waits on the reset header, and `dotnet test` is
    green.
    After: The Okta System Log exporter was rereading whole hours, so a retry
    could write the same event twice. It now waits using the response reset
    header, and the six acceptance tests pass.

## Punctuation and formatting

15. **No dashes or middle dots.** Do not use em dashes or en dashes, including in
    number ranges. Join clauses with a period or "and", and write ranges with
    "to". Do not use the middle dot (·) as a separator; use a comma, "and", or
    separate lines instead.
    Before: The build is fast — it finishes in 10 to 20 seconds.
    After: The build is fast. It finishes in 10 to 20 seconds.

16. **Don't use colons to join clauses in ordinary prose.** Do not use a colon
    to glue two clauses or to set up a point in essay-like writing. A colon is
    fine when you introduce a list. A colon is also fine as a short label in
    updates, briefs, status notes, and PR descriptions, e.g., "Summary:",
    "Changes:", or "Remaining work:".
    Before: Read for the schema: the feature fires.
    After: Read for the schema. The feature fires.
    Before (allowed in a PR or update): Summary: Replace em dashes in
    generated docs.
    After (same text is fine): Summary: Replace em dashes in generated docs.

17. **Use straight quotes, not curly quotes.**
    Before: The system logs each “event” as it happens.
    After: The system logs each "event" as it happens.

18. **Keep the formatting plain.** Use sentence case in headings. Do not use
    bold for decoration.
    Before: ## How To Install The Skill
    After: ## How to install the skill

19. **You can use lists, but do not overuse them.** Keep a list to three or
    four points, and nest extra points if you need more. When you are writing
    an essay, use lists and tables very sparingly.
    Before: Shipped this week:
    - dark mode
    - an invite link fix
    - a schema mismatch that blocked analytics export
    - renderer cleanup
    - copy edits
    - a scored ranking model
    - a p95 drop from 900 ms to 220 ms
    - untested recall on long queries
    After: Search ranking now uses a scored model, and p95 latency fell from
    900 ms to 220 ms. The old heuristic path is still in the repo as a
    fallback.
    - Shipped
      - Dark mode
      - Invite link fix
    - Still open
      - Test recall on long queries
      - Unblock analytics export

## Patterns to avoid

Leftover bans (fake agency, "not just X but Y", stacked questions, vague
demonstratives, opening with a count) live in [`TELLS.md`](TELLS.md).

21. **No analogies or imagery.** Do not explain by comparing to something else,
    and do not use metaphor. Describe the actual thing in literal terms. Write
    in a boring way.
    Before: The feature index is like a card catalog that the optimizer can flip
    through.
    After: The feature index is a list of named features. The optimizer can look
    up which feature matches a request.

## The deslopify command

When the user says `/plain-writing deslopify`, rewrite the previous agent
response, or the text after the command, for a sharp CEO or technical reader
who has no project context. Return only the rewrite.

Start with the main conclusion, then cover the background, how it works, and
present all information logically and sequentially. Include technical details
the reader needs (standardize on existing well-known terminology, not new
terminology), and define unfamiliar terms.

Follow the plain-writing rules above.

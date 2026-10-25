# Templates

The formats of the files in `learning/`. Placeholders are in `<angle brackets>`; dates are `YYYY-MM-DD`, times `HH:MM` from `date`.

## `learning/plan.md`

One block per chapter, 0 to 24, grouped under the skeleton's part headings. `Build` is the chapter's line from `plan-skeleton.md`, after its estimate.

```markdown
# Fluent Python plan

Status: not started | in progress | done. Sessions: used / estimated.

## Week 0

### 00 Crude loop
- Status: not started
- Sessions: 0 / 2
- Build: <the skeleton line>

## Part I: Data Structures

### 01 Data model
- Status: not started
- Sessions: 0 / 2
- Build: <the skeleton line>
```

## `learning/book-index.md`

```markdown
# Book index

PDF pages, 1-based from the start of the file (not printed page numbers).

## Fluent Python, 2nd edition (`book/fluent-python-2e.pdf`)

| Ch | Title | Pages |
|---|---|---|
| 1 | The Python Data Model | 33–56 |

### Sections

#### 1 The Python Data Model
- What's New in This Chapter: 34
- A Pythonic Card Deck: 35–39

## Clean Code (`book/clean-code.pdf`)

| Ch | Title | Pages |
|---|---|---|
| 2 | Meaningful Names | 47–64 |
```

## `learning/chapters/chNN.md`

`NN` is two digits: `ch00.md` to `ch24.md`. Section references give the title and PDF pages from `book-index.md`. Task status is `todo`, `in progress` or `passed`.

```markdown
# Ch NN <chapter title>: <component>

## Concepts
- <concept>: §<section title> (pp. <a>–<b>)

## Component
<What to build, and how it fits the current code: the modules and names in src/ it changes or adds, and the crude code it refactors.>

## Tasks

### T1 <title>
- Status: todo
- Goal: <one sentence>
- Interface: <the public names the acceptance tests call, with module path and signature, e.g. `agent.conversation.Conversation.__len__(self) -> int`; nothing more>
- Acceptance criteria:
  - A1 <an observable behaviour>
- Required tests (the user writes these):
  - R1 <the behaviour the test checks>
- Revisit: §<section title> (pp. <a>–<b>)
- Hints: 0
- Decisions: <answers to clarifying questions that refine the spec>

## Out of scope
- <skeleton concept left out, and why>

## Verification history

| Date | Task | Result | Gaps |
|---|---|---|---|
| <date> | T1 | fail | R3 missing; A2: <behaviour not met> |

## Review notes
- <date> T1 [<rubric item>] <note>. Read: Clean Code ch <n> <title> (pp. <a>–<b>). Follow-up: open
```

## `learning/log.md` entry

Append at session start with `End` blank; complete at wrap-up. Newest last.

```markdown
## <date> ch<NN> T<n>
- Start: <HH:MM>
- End:
- Done: <what was built or verified>
- Resume: <where to pick up, and the next concrete step>
- Weak concepts: <concepts, or none>
- Recurring review issues: <rubric items seen before, or none>
```

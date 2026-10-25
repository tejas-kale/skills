# Templates

The formats of the files in `learning/`. Placeholders are in `<angle brackets>`; dates are `YYYY-MM-DD`, times `HH:MM` from `date`.

## `learning/plan.md`

One block per chapter, 1 to 16, grouped under the backlog's part headings. `Build` is the chapter's line from `plan-backlog.md`, after its estimate. `Swap` and `Follow-up` appear only when there is one.

```markdown
# Total TypeScript plan

Status: not started | in progress | done. Sessions: used / estimated.

## Diagnostics

| Run | Status | Date | Score |
|---|---|---|---|
| Week 0 | not started | | |
| After ch 5 | not started | | |
| After ch 10 | not started | | |
| After ch 16 | not started | | |

## Part I: Setup

### 01 Kickstart Your TypeScript Setup
- Status: not started
- Sessions: 0 / 3
- Build: <the backlog line>

## Part II: Fundamentals

### 05 Unions, Literals, and Narrowing
- Status: in progress
- Sessions: 1 / 2
- Build: <the user's project>
- Swap: replaces <the backlog project>; stretches: <what was added to cover the chapter, and any dependency kept>
- Follow-up: <project split off the spec>, sessions 0 / <n>
```

## `learning/book-index.md`

```markdown
# Book index

PDF pages, 1-based from the start of the file (not printed page numbers).

## Total TypeScript: The Essentials (`book/total-typescript.pdf`)

| Ch | Title | Pages |
|---|---|---|
| 5 | Unions, Literals, and Narrowing | 81–112 |

### Sections

#### 5 Unions, Literals, and Narrowing
- <section title>: 82–85

## Clean Code (`book/clean-code.pdf`)

| Ch | Title | Pages |
|---|---|---|
| 2 | Meaningful Names | 47–64 |

## Exploring JavaScript, ES2025 edition (web)

Added as sections are looked up.

| Topic | Chapter › section | URL |
|---|---|---|
| `this` in a method passed as a callback | <chapter> › <section> | <url> |
```

## `learning/chapters/chNN.md`

`NN` is two digits: `ch01.md` to `ch16.md`. Section references give the title and PDF pages from `book-index.md`. Task status is `todo`, `in progress` or `passed`.

```markdown
# Ch NN <chapter title>: <project>

## Concepts
- <concept>: §<section title> (pp. <a>–<b>)

## Project
<What to build, and how it fits the existing packages: the package it adds or changes, the modules in it, what it imports from other packages (the FakeExtensionAPI, agent-utils), and the existing code it refactors.>

- pi API: <the names used, from docs/extensions.md of <package>@<version>>, or n/a
- Link script: <what it must learn, or nothing, and why>

## Tasks

### T1 <title>
- Status: todo
- Goal: <one sentence>
- Interface: <the exported names the acceptance tests call, with module path and signature, e.g. `packages/permission-gate/src/decide.ts: decide(event: ToolEvent, policy: Policy): Decision`; nothing more>
- Acceptance criteria:
  - A1 <an observable behaviour>
- Required tests (the user writes these):
  - R1 <the behaviour the test checks>
- Revisit: §<section title> (pp. <a>–<b>)
- Hints: 0
- Decisions: <answers to clarifying questions that refine the spec>

## JS runtime pitfalls
- T1 <the runtime behaviour the task meets>: <what to check>. Read: <Exploring JavaScript chapter › section> (<url>)
- T2 <pitfall> (weak): <what to check>. Read: <section> (<url>)

## Out of scope
- <backlog concept left out, and why>

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
- Weak concepts (TypeScript): <concepts, or none>
- Weak concepts (JavaScript): <concepts with their Exploring JavaScript section, or none>
- Recurring review issues: <rubric items seen before, or none>
```

Diagnostic variant:

```markdown
## <date> diagnostic <week 0 | after ch NN>
- Start: <HH:MM>
- End:
- Diagnostic: <asked> asked, <right> right; misses: Q<n>, …
- Score: <right> / <total>
- Weak concepts (JavaScript): <each miss as a specific behaviour, with its Exploring JavaScript section>
- Cleared: <earlier weak JavaScript concepts answered right this run, or none>
- Resume: <questions left, or none>
```

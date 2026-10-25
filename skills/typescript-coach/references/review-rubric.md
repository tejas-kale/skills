# Review rubric

The code-quality review in Verify. It is **advisory**: it never blocks a pass. Review the task's code (`git diff HEAD` plus untracked files in the affected packages) and work the checks in order; every check runs on every review. A check that names a feature applies from the chapter that teaches it (the feature gate in `plan-backlog.md`); before that, the crude version is expected, and is later chapters' material.

## 1. The chapter's concept

The most important check. For each concept in `chNN.md`'s Concepts, find where the code should use it and confirm it does. A chain of `if`s on a string where the chapter teaches a discriminated union, a hand-written type beside a schema where it teaches `Static<typeof schema>`, an `as` where it teaches `satisfies`: each is a note, citing the Total TypeScript section instead of a Clean Code chapter. Also flag a concept from an earlier chapter that the new code ignores.

## 2. Idiom: TypeScript

These decide what is idiomatic, and they win any conflict with section 4:

- Discriminated unions over class hierarchies for data.
- Narrowing over `as`; `as` only where the code proves what the compiler cannot, with a comment saying why.
- `unknown` over `any` at every boundary (JSON, stdin, event payloads).
- Types derived from a single source of truth (a schema, a `const` array, a function) over parallel hand-written types.
- `readonly` and `as const` where nothing should mutate.

## 3. Python habits carried over

The user's Python reflexes, each a JavaScript runtime trap. Cite the *Exploring JavaScript* section (from `book-index.md`, or looked up as in `js-diagnostic.md`):

- A plain object used as a dictionary with arbitrary or user-supplied keys, where a `Map` fits.
- A floating promise: a call returning a Promise that nothing awaits, returns or `.catch`es.
- `try`/`catch` around async code whose Promise is not awaited inside the `try`, so the rejection escapes.
- Loose equality (`==`, `!=`), or truthiness standing in for a check on `null`/`undefined` where `0` or `""` are valid.
- `for...in` over an array.
- Mutating a shared object or array (an argument, module state, event payload) in place.
- `this` expected to bind like Python's `self`: a method passed as a callback, or a `function` where an arrow keeps the outer `this`.
- An exception thrown for an expected outcome (not found, denied, invalid input) where a union or `Result` type fits.

## 4. Clean Code

Apply these, citing the chapter (look up its pages in `book-index.md`):

| Check | Clean Code chapter |
|---|---|
| Names reveal intent; no encodings or noise words | 2 Meaningful Names |
| A function does one thing, at one level of abstraction | 3 Functions |
| A class or module has a single responsibility | 10 Classes |
| Errors are meaningful: specific error types, messages with context, nothing swallowed | 7 Error Handling |
| Third-party code (pi's API, `fetch`, `child_process`) sits behind a boundary of the project's own | 8 Boundaries |
| Tests are clean: one concept per test, readable arrange/act/assert | 9 Unit Tests |
| Duplication and other smells | 17 Smells and Heuristics |

Leave out Clean Code's Java-specific advice: getters and setters, functions shortened past readability, an interface for everything, and classes where a function or a module of functions does the job. TypeScript has structural types, plain functions and modules.

## Writing a note

One line per note, in `chNN.md`'s review-notes format: the rubric item, what and where (file and line), why, and what to read (a Clean Code chapter with pages, a Total TypeScript section for check 1, an *Exploring JavaScript* section for check 3). Describe the change in words or a one-line shape, never as code. Before writing a note, look for the same rubric item in earlier review notes: if it is there, mark the note recurring, and wrap-up logs it under recurring review issues.

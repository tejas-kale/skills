# Review rubric

The code-quality review in Verify. It is **advisory**: it never blocks a pass. Review the task's code (`git diff HEAD` plus untracked files in `src/` and `tests/`) and work the checks in order; every check runs on every review.

## 1. The chapter's concept

The most important check. For each concept in `chNN.md`'s Concepts, find where the code should use it and confirm it does. A hand-rolled loop where the chapter teaches `bisect`, a getter where it teaches `__len__`, a dict of dicts where it teaches `ChainMap`: each is a note, citing the Fluent Python section instead of a Clean Code chapter. Also flag a concept from an earlier chapter that the new code ignores.

## 2. Idiom: Fluent Python and PEP 8

These decide what is Pythonic, and they win any conflict with section 3:

- Dunders over getters: `len(registry)`, not `registry.count()`.
- Comprehensions and generator expressions over accumulate-in-a-loop.
- Duck typing over type checks; EAFP (`try`/`except KeyError`) over look-before-you-leap.
- Dataclasses (from chapter 5) over hand-written `__init__`/`__repr__`/`__eq__`.
- Standard library first: `collections`, `itertools`, `functools`, `contextlib`.
- PEP 8 naming and layout beyond what ruff already enforces.

## 3. Clean Code

Apply these, citing the chapter (look up its pages in `book-index.md`):

| Check | Clean Code chapter |
|---|---|
| Names reveal intent; no encodings or noise words | 2 Meaningful Names |
| A function does one thing, at one level of abstraction | 3 Functions |
| A class has a single responsibility | 10 Classes |
| Errors are meaningful: specific exceptions, messages with context, nothing swallowed | 7 Error Handling |
| Third-party code (httpx, subprocess) sits behind a boundary of the agent's own | 8 Boundaries |
| Tests are clean: one concept per test, readable arrange/act/assert | 9 Unit Tests |
| Duplication and other smells | 17 Smells and Heuristics |

Leave out Clean Code's Java-specific advice: getters and setters, functions shortened past readability, an interface for everything, and comment bans that conflict with docstrings. Python has properties, Protocols arrive in chapter 13, and docstrings are idiomatic.

## Writing a note

One line per note, in `chNN.md`'s review-notes format: the rubric item, what and where (file and line), why, and what to read (a Clean Code chapter with pages, or a Fluent Python section for check 1). Describe the change in words or a one-line shape, never as code. Before writing a note, look for the same rubric item in earlier review notes: if it is there, mark the note recurring, and wrap-up logs it under recurring review issues.

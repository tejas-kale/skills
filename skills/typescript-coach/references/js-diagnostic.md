# JavaScript runtime diagnostic

A predict-the-output quiz that finds the user's JavaScript runtime gaps. The user answers from their head; nobody runs code but you. Generate the questions fresh on every run, so none can be memorised: never reuse a snippet, and never write one into `learning/`.

## Runs

| Run | When | Questions |
|---|---|---|
| Week 0 | after bootstrap, before chapter 1 | 20 |
| After ch 5, after ch 10, after ch 16 | once that chapter is done, before the next | 8 |

Each run is a row in `plan.md`'s diagnostics table: not started, due, in progress or done, with its score.

## Topic areas

1. `===` vs `==` and type coercion
2. `undefined` vs `null`, and truthiness
3. `let`, `const` and `var`, and closures in loops
4. How `this` binds in methods, callbacks and arrow functions
5. Prototypes behind classes
6. Event-loop ordering: synchronous code, microtasks, timers
7. Promise chaining, and errors from un-awaited promises
8. `for...in` vs `for...of`
9. Object and array reference semantics; spread copies are shallow
10. `Map` vs plain objects
11. ESM imports: live bindings, evaluation order, default vs named

**Week 0:** two questions per area, one each for areas 10 and 11.
**Short run:** five questions on weak JavaScript concepts in `log.md` not yet cleared (oldest first); the rest from areas the finished chapters' JS runtime pitfalls touched. With fewer than five open weak concepts, fill from the areas with the most misses so far.

## Write a batch

Ask four questions at a time, numbered across the run (`Q1`…`Q20`).

1. Write each question as its own file in `tmp=$(mktemp -d)` (keep the directory for the run): `"$tmp"/q<n>.mjs`, or for area 11 a small set of files, the entry one named `q<n>.mjs`. Each runs as an ES module in Node 22, so strict mode holds and top-level `this` is `undefined`.
2. Keep each snippet to 3–10 lines whose only output is `console.log`. Aim at the trap, not trivia: one behaviour a Python programmer would mispredict. Vary names, values and shape from anything earlier in the log.
3. Run each into a file, so the key stays off the terminal until marking: `node "$tmp"/q<n>.mjs > "$tmp"/q<n>.out 2>&1; echo "exit $?" >> "$tmp"/q<n>.out`. That output (stdout, the first line of any error, the exit status) is the answer key, never your own prediction. Run each twice and rewrite any snippet whose output differs.
4. Show the batch: each snippet and the question "What does this print, in order? If it throws, which error, and after which output?". Give no topic labels, and keep the key out of the chat until the user answers. Remind the user once per run to answer without running anything.

## Mark a batch

1. An answer is right when the printed lines and their order match; formatting of logged objects can differ. A throw counts only with the error type.
2. Read the `.out` files, then reveal the actual output for each question with a one-line reason.
3. For each miss, name the weak concept as the specific behaviour (e.g. "`this` in a method passed as a callback", not "this"), and give its *Exploring JavaScript* section (Lookup).
4. Update the open log entry's `Diagnostic` line (asked, right, misses so far), so an interrupted run resumes with fresh questions for the remaining count and areas.

## Lookup

*Exploring JavaScript* (ES2025 edition) is free at exploringjs.com/js/. First look for the topic in `book-index.md`'s Exploring JavaScript table. Otherwise fetch the table of contents (`https://exploringjs.com/js/book/index.html`), open the chapter that covers the behaviour, pick the section, and add a row with topic, chapter and section titles and the section's URL. When the site is unreachable, give the chapter title you expect, marked unverified, and leave the row out.

## Finish

1. Score: right / asked.
2. Complete the log entry ([`templates.md`](templates.md), diagnostic variant): every miss under weak JavaScript concepts with its section, and for a short run, under `Cleared`, each earlier weak concept answered right this time.
3. Set the run to done in `plan.md` with the date and score. `rm -rf "$tmp"`.

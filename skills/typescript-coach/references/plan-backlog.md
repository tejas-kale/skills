# Plan backlog

The source for `learning/plan.md` and the context for every spec.

## The monorepo

- pnpm workspace, Node 22, TypeScript strict, ESM (`NodeNext`), vitest. typescript-eslint in strict mode with `no-floating-promises`, `eqeqeq` and `strict-boolean-expressions`.
- One package per project under `packages/`, with a shared tsconfig and eslint config at the root.
- pi is Mario Zechner's minimal coding-agent harness. An extension exports a default function that receives pi's `ExtensionAPI`; through it, it registers tools (TypeBox parameter schemas), commands and providers, subscribes to events such as `session_start` and `tool_call`, and uses `ctx.ui` for user prompts. Names change between releases: check the installed docs (2a step 3) before a spec names any.
- Claude Code projects: hooks (a command reading the hook's JSON payload on stdin), MCP servers, and the status line.
- The model is Flint, a local model served by llama.cpp's `llama-server` through its OpenAI-compatible API, registered as a pi provider in project 4. Before project 4, specs depend on no model. From project 4, read the base URL from the user's provider package.
- Install: project 1's link script symlinks built pi extensions into `~/.pi/agent/extensions`, registers Claude Code hooks and MCP servers, and points `~/Code/config` at the Claude Code builds. The chapter 1 spec requires a target override (an environment variable for the base directory) so tests and verification run the script against a temp directory. Every later spec says what the link script must learn, if anything ("nothing: the extension is picked up by the existing glob" is an answer).

## Testing

- Logic lives in pure modules with unit tests; the extension's default function only wires them to pi.
- The user writes a `FakeExtensionAPI` in project 2 that records registrations and fires events. From project 3 on, specs for pi extensions test through it; the chapter 2 spec fixes where it lives.
- At most one smoke test per project, driving the pi SDK against Flint, and none before project 4.

## Feature gate

A spec uses a TypeScript feature no earlier than the chapter that teaches it: a feature named on a chapter's line below waits for that chapter. The commonest traps: unions, literal types and narrowing wait for 5; index signatures and `Record` for 6; `readonly` and `as const` for 7; classes for 8; enums and parameter properties for 9; `typeof`/`keyof`/indexed access and `Static<typeof schema>` for 10; type predicates, assertion functions and `satisfies` for 11; writing your own generics and overloads for 15 and 16. Generic types from libraries (`Promise<T>`, `Array<T>`) are fine earlier. Write specs that create refactoring opportunities for later chapters: chapter 6's hand-written parameter types beside a TypeBox schema are chapter 10's material, and each project's ad-hoc retry or event plumbing is chapter 16's.

## Dependencies

Later projects rely on these; a swap (2b) keeps them or moves them:

| Built in | What | Relied on by |
|---|---|---|
| 1 | monorepo scaffold, link script | every project |
| 2 | `FakeExtensionAPI` | every pi extension from 3 |
| 4 | Flint provider | smoke tests from 4, project 15 |
| 8 | MCP server over `learning/` | both coaches (optional) |
| 14 | `agent-utils` package | project 16 |

## Chapters

P = pi extension, CC = Claude Code project. Each line names the chapter, then the project and the concepts it practises. `est` is the starting session estimate; the spec replaces it with its task count.

### Part I: Setup

1. Kickstart Your TypeScript Setup (est 3): monorepo scaffold (pnpm workspace, shared tsconfig and eslint, vitest), the link script, and a hello-world P extension that shows a notification on `session_start`
2. IDE Superpowers (est 2): P session-timer footer for the 45/15 hour. Deliberately small, so the practice goes into editor navigation, hovers, rename and quick fixes. Also the `FakeExtensionAPI`.
3. TypeScript in the Development Pipeline (est 2): CC `PreToolUse` hook in TypeScript that blocks risky git commands, built with tsc, tested with vitest, run in CI (GitHub Actions)

### Part II: Fundamentals

4. Essential Types and Annotations (est 2): P Flint provider that registers llama-server, with typed fetching of `/v1/models`
5. Unions, Literals, and Narrowing (est 2): P permission gate on `tool_call`, using a discriminated union of tool events and an allow/deny/ask result type

### Part III: Objects, classes, mutability

6. Objects (est 2): P `todo` tool with TypeBox parameters and per-session state (`Record`s, index signatures, optional properties)
7. Mutability (est 2): P session-notes extension whose state survives pi's session branching (`readonly`, `as const`, immutable updates)
8. Classes (est 3): CC MCP server, class-based, exposing `learning/` (plan, log, weak concepts) to any agent; both coaches can use it
9. TypeScript-only Features (est 2): P `/mode` command (plan/build/review) that switches tool sets, comparing enums with literal unions, and parameter properties

### Part IV: Working with the compiler

10. Deriving Types (est 2): P `fetch_url` tool whose types come from its schema (`Static<typeof schema>`, `typeof`, `keyof`, indexed access, `ReturnType`)
11. Annotations and Assertions (est 2): CC hook-payload logger to JSONL, using type predicates, assertion functions, `satisfies`, and `as` only where justified
12. The Weird Parts (est 2): typed event bus between P extensions (structural typing, function assignability, excess property checks, the empty object type)

### Part V: Understanding the environment

13. Modules, Scripts, and Declaration Files (est 2): publish one P extension as a pi package, and hand-write `.d.ts` files for the llama-server API
14. Configuring TypeScript (est 2): shared `agent-utils` package used by both P and CC projects (project references, `NodeNext`, declaration output)

### Part VI: Advanced application development

15. Designing Your Types (est 3): P sub-agent extension that spawns pi in RPC mode, with a typed generic request/response protocol
16. The Utils Folder (est 3): capstone that pulls retry, `Result` and the typed event emitter out of every project into `agent-utils`, using generics and overloads

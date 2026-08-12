# Code Review — Workers

The review branch of [`workers-best-practices`](../SKILL.md): type correctness, API usage, config validity, and how to grade and report findings. Step 1 of the skill has already retrieved the types, the config schema, and the best practices page.

Search the retrieved `index.d.ts` for each type, class, or interface under review — look every name up rather than recalling it. Two further sources when you need them:

- `npx wrangler types` generates a typed `Env` interface from the local wrangler config.
- `node_modules/wrangler/config-schema.json` (JSON Schema draft-07) is authoritative for every config field name and shape.

---

## Type Validation

### Env interface

- Every binding must have a specific type. Flag `any`, `unknown`, `object`, or `Record<string, unknown>` on bindings.
- Binding types that accept generic parameters (Durable Object namespaces, Queues, Service bindings for RPC) must include them. Read the type definition to confirm which types are generic.
- Binding names must match the wrangler config exactly.
- Prefer generated types from `wrangler types` over hand-written interfaces.

### Handler and class signatures

Verify against current type definitions — do not assume signatures are stable.

- Correct import path (most Workers platform classes import from `"cloudflare:workers"`)
- Generic type parameter on base classes (e.g., `DurableObject<Env>`)
- Binding access pattern: `env.X` in module export handlers, `this.env.X` in classes extending platform base classes
- `ExecutionContext` as the third param in module export handlers (needed for `ctx.waitUntil()`)
- `fetch()` handlers must return `Promise<Response>`

### Binding access — the most common error

- **Module export handlers** (`fetch`, `scheduled`, `queue`, `email`): bindings via `env.X` parameter
- **Platform base classes** (`WorkerEntrypoint`, `DurableObject`, `Workflow`, `Agent`): bindings via `this.env.X`

Flag `env.X` inside a class extending a platform base class. Flag `this.env.X` inside a module export handler.

### Type integrity rules

| Rule | Detail |
|------|--------|
| No `any` | Never on binding types, handler params, or API responses |
| No double-casting | `as unknown as T` hides real incompatibilities — fix the underlying design |
| Justify suppressions | `@ts-ignore`/`@ts-expect-error` must include a comment explaining why |
| Prefer `satisfies` | Use `satisfies ExportedHandler<Env>` over `as` — validates without widening |
| Validate, do not assert | Schema or type guard for untyped data (JSON, parsed bodies), not `as` |

### Stale class patterns

Old patterns survive in codebases long after APIs change.

- **`extends` vs `implements`**: platform classes use `extends`, not `implements`. The `implements` pattern is legacy and loses `this.ctx`, `this.env`.
- **Import paths**: verify module specifiers match what types actually export. Common mistake: wrong path for `"cloudflare:workers"` vs `"cloudflare:workflows"`.
- **Renamed properties**: e.g., `this.state` to `this.ctx` in Durable Objects. Search types to confirm.
- **Constructor signatures**: base class constructors change. Verify expected parameters.

---

## Config Validation

### Required fields

For executable examples, verify: `name`, `compatibility_date`, `main`. Check the schema for current required fields.

### Config format

- **JSONC** (`wrangler.jsonc`) — preferred for new projects
- **JSON** (`wrangler.json`) — valid but no comments
- **TOML** (`wrangler.toml`) — legacy; acceptable in existing content, flag in new projects

### Binding-code consistency

1. Every `env.X` reference in code has a corresponding binding declaration in config
2. Every binding in config is referenced in code (warn on unused)
3. Names match exactly (case-sensitive)
4. For Durable Objects: `class_name` matches the exported class name

### Common config mistakes

| Check | What to look for |
|-------|-----------------|
| Stale `compatibility_date` | Should be recent; use `$today` placeholder in docs |
| Missing DO migrations | Every new DO class needs a migration entry |
| Binding name mismatch | Config `binding`/`name` must match `env.X` in code |
| Secrets in config | Never in `vars` — use `wrangler secret put` |
| Wrong binding key | Verify top-level key name against the schema |
| Missing entrypoint | `main` required for executable Workers |

---

## Type-specific anti-patterns

Beyond the scan list in `SKILL.md`, these only surface once you are reading types:

- **`@ts-ignore` / `@ts-expect-error` without explanation** — masks errors silently; require a justifying comment
- **`this.env.X` in a module export handler** — should be the `env` parameter
- **Non-serializable values across a boundary** — a `Response` or `Error` in a step or queue message compiles and fails at runtime

---

## Serialization Boundaries

Data crossing these boundaries must be structured-clone serializable:

- **Queue messages**: body passed to `.send()` or `.sendBatch()`
- **Workflow step return values**: persisted to durable storage
- **DO storage**: values in `storage.put()` or SQL
- **`postMessage()`**: WebSocket messages

Non-serializable types to flag: `Response`, `Request`, `Error`, functions, class instances with methods, `Map`/`Set`, `Symbol`.

Valid: plain objects, arrays, strings, numbers, booleans, null, `ArrayBuffer`, `Date`.

---

## Grading the code

How hard to press depends on what the code claims to be:

- **Illustrative** (concept demo, comments standing in for most logic) — verify the API names are real and the signatures plausible.
- **Demonstrative** (a functional snippet that would work in context) — verify syntax, APIs, and binding access.
- **Executable** (standalone, runs unmodified) — verify it compiles and runs, imports included, config included.

Risk level follows the blast radius: **HIGH** for auth, crypto, and bindings; **MEDIUM** for business logic and config; **LOW** for style and comments.

## Output format

```
**[SEVERITY]** Brief description
`file.ts:42` — explanation with evidence
Suggested fix: `code`
```

Severity: **CRITICAL** (security, data loss, crash) | **HIGH** (type error, wrong API, broken config) | **MEDIUM** (missing validation, edge case) | **LOW** (style, minor improvement)

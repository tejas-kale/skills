---
name: workers-best-practices
description: Author and review Cloudflare Workers code against production best practices. Use when writing a Worker, reviewing Worker code, configuring wrangler.jsonc, or checking for Workers anti-patterns — streaming, floating promises, global state, secrets, bindings, observability.
---

# Workers Best Practices

Your baked-in knowledge of Workers APIs, config fields, and binding shapes is stale. **Retrieve** first: every API signature, config field, and binding shape you assert comes from a source fetched this session, and a finding you cannot cite a source for does not get reported.

## 1. Retrieve

Fetch before writing or reviewing a single line. Prefer the latest published version over whatever `node_modules` pins.

```bash
# Latest workers types → /tmp/workers-types-latest/package/index.d.ts
mkdir -p /tmp/workers-types-latest && \
  npm pack @cloudflare/workers-types --pack-destination /tmp/workers-types-latest && \
  tar -xzf /tmp/workers-types-latest/cloudflare-workers-types-*.tgz -C /tmp/workers-types-latest
```

| Source | Where | Use for |
|---|---|---|
| Best practices page | `https://developers.cloudflare.com/workers/best-practices/workers-best-practices/` | Canonical rules and anti-patterns |
| Workers types | the `npm pack` above | API signatures, handler types, binding types |
| Wrangler config schema | `node_modules/wrangler/config-schema.json` | Config fields, binding shapes, allowed values |
| Cloudflare docs | search, or `https://developers.cloudflare.com/workers/` | API reference, compatibility dates and flags |

Done when the types, the config schema, and the best practices page are all in context.

## 2. Apply the rules

[`references/rules.md`](references/rules.md) is the single source of truth for every rule — configuration, request handling, architecture, observability, code patterns, security, testing — each with its correct pattern and the anti-pattern it replaces. Read it, then work the rule set:

- **Authoring** — every rule in the relevant sections holds in the code you write.
- **Reviewing** — read the full files rather than the diff, since binding access and global state only read correctly in context, then check every rule against them.

Done when every rule in `references/rules.md` has been applied or consciously judged inapplicable — not when the obvious ones pass.

## 3. Verify and report

Run `npx tsc --noEmit` and lint for `no-floating-promises`; a rule a tool can check is checked by the tool, not by eye.

For a review, [`references/review.md`](references/review.md) carries the review-specific reference: type and config validation, serialization boundaries, how to grade illustrative vs executable code, risk levels, and the finding format. Read it before writing up findings.

Done when every finding names a file and line, cites its evidence, and carries a severity.

## Anti-patterns to flag

The recurring ones, as a scan list — each is explained in full in `references/rules.md`.

| Anti-pattern | Why it matters |
|---|---|
| `await response.text()` on unbounded data | Memory exhaustion — 128 MB limit |
| Hardcoded secrets in source or config | Credential leak via version control |
| `Math.random()` for tokens or IDs | Predictable, not cryptographically secure |
| Bare `fetch()` without `await` or `waitUntil` | Floating promise — dropped result, swallowed error |
| Module-level mutable variables for request state | Cross-request data leaks, stale state, I/O errors |
| Cloudflare REST API from inside a Worker | Extra network hop, auth overhead, added latency |
| `ctx.passThroughOnException()` as error handling | Hides bugs and makes debugging impossible |
| Hand-written `Env` interface | Drifts from the actual wrangler config bindings |
| Direct string comparison of secrets | Timing side-channel — use `crypto.subtle.timingSafeEqual` |
| Destructuring `ctx` (`const { waitUntil } = ctx`) | Loses `this` binding — "Illegal invocation" at runtime |
| `any` on `Env` or handler params | Defeats type safety for every binding access |
| `as unknown as T` double-cast | Hides a real type incompatibility — fix the design |
| `implements` on a platform base class | Legacy — loses `this.ctx` and `this.env`; use `extends` on DurableObject, WorkerEntrypoint, Workflow |
| `env.X` inside a platform base class | Should be `this.env.X` |

## Scope

Workers themselves. For the wider platform — Durable Objects, Workflows, Wrangler commands, KV/D1/R2 — load the `cloudflare` umbrella skill, whose `references/` carries a file per product.

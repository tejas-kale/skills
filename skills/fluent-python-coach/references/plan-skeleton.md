# Plan skeleton

The source for `learning/plan.md` and the context for every spec.

## The agent being built

- A Python project managed with uv; tests with pytest, lint and format with ruff, and types with mypy from chapter 8.
- The LLM is a local model called Flint, served by llama.cpp's `llama-server` through its OpenAI-compatible `/v1/chat/completions` endpoint, with tool calls and `stream: true` server-sent events (SSE).
- The client is raw `httpx`, with no openai SDK: synchronous until chapter 21, asynchronous from then on.
- Specs keep network I/O behind an injectable `httpx.Client` (later the `LLMBackend` of chapter 13), so tests run against `httpx.MockTransport` or a fake and never need a running server.

## Feature gate

A spec uses a Python feature no earlier than the chapter that teaches it: a feature named on a chapter's line below waits for that chapter. The commonest traps: dataclasses wait for 5, type hints are optional until 8, decorator registration waits for 9, Protocols and ABCs for 13, generators for 17, context managers for 18, threads and processes for 19, async for 21. Write specs that create refactoring opportunities for later chapters: crude code now is next chapter's material.

## Chapters

Each line names the chapter, then the concepts to practise and where they land in the agent. `est` is the starting session estimate; the spec replaces it with its task count.

### Week 0 (before Part I)

0. Crude loop (est 2): a deliberately crude chat loop built from plain dicts and lists. Two tools: `run_python(code)` (subprocess with a timeout) and `get_exercise(chapter)`, which serves drills from `drills/chNN/`. Crude SSE handling (split lines, `json.loads` each `data:` payload, accumulate tool-call deltas in dicts). The drill format starts here; propose one JSON file per pack, `drills/chNN/pack.json`, holding a list of dicts with `id`, `kind`, `concept`, `prompt` and `check`, where `check` is Python run through `run_python` with the user's answer bound to `answer` and exit status 0 meaning correct.

### Part I: Data Structures

1. Data model (est 2): `Conversation` and `ToolRegistry` dunders (`__len__`, `__getitem__`, `__iter__`, `__contains__`, `__bool__`, `__repr__`)
2. Sequences (est 3): context window (slicing, `deque(maxlen=...)`, `bisect` on cumulative token counts), turns as tuples/`NamedTuple`, `match` sequence patterns for parsing model responses
3. Dicts and sets (est 3): tool dispatch, `__missing__` returning a tool-not-found error to the model, `ChainMap` config layers (defaults < project < CLI), `MappingProxyType` read-only registry, `Counter`/`defaultdict` mastery tracking, set difference for undrilled concepts, `match` mapping patterns on tool-call JSON
4. Unicode and bytes (est 2): explicit decoding of sandbox stdout/stderr with an `errors=` policy, SSE stream decoding with `codecs.getincrementaldecoder` (chunks can split multibyte characters), NFC normalisation of answers, explicit `encoding=` on all file I/O
5. Data class builders (est 3): `Message`/`ToolCall`/`Drill`/`Attempt` as `@dataclass(frozen=True, slots=True)`, `field(default_factory=...)`, `__post_init__` validation, tool JSON Schemas built from `dataclasses.fields()`, `asdict` persistence of session state
6. References and mutability (est 2): conversation snapshot/undo (`copy` vs `deepcopy`), aliasing and mutable-default bugs, `is` vs `==`, `WeakValueDictionary` cache of drill packs

### Part II: Functions as Objects

7. First-class functions (est 2): tool handlers as callables, `functools.partial` to bind config, `__call__` for stateful tools, key functions for ordering drills
8. Type hints in functions (est 2): annotate everything, switch on mypy, tool schemas built from `inspect.signature` and annotations
9. Decorators and closures (est 3): `@tool` registration, `@retry`/`@timed` on LLM calls, `functools.cache` for drill loading, `singledispatch` for rendering results
10. Design patterns with functions (est 2): drill-selection strategies (random, weakest-first, spaced repetition) as functions, command pattern for REPL commands

### Part III: Classes and Protocols

11. A Pythonic object (est 2): `Mastery` value object (`__format__`, `__hash__`, `__eq__`, `from_json` alternate constructor, `__slots__`)
12. Sequence special methods (est 2): `Transcript` whose slicing returns a `Transcript`, `__eq__`/hash via `functools.reduce`
13. Interfaces, protocols, ABCs (est 3): `LLMBackend` Protocol (llama-server implementation plus a `FakeLLM` for tests), `Tool` ABC, `runtime_checkable`
14. Inheritance (est 2): tool mixins (logging, timeout), cooperative `super()`, the MRO, then a refactor towards composition
15. More about type hints (est 3): `TypedDict` for raw API payloads, `@overload`, a generic `Result[T]`, bounded `TypeVar`, `mypy --strict`
16. Operator overloading (est 2): `Mastery` arithmetic, `|` to merge registries and config, rich comparisons for drill priority, `__iadd__`

### Part IV: Control Flow

17. Iterators and generators (est 3): SSE lines → events → tokens pipeline with `yield from`, lazy drill feed, `itertools` (`islice`, `groupby` by concept)
18. with, match, else (est 2): sandbox temp-dir context manager (`contextlib.contextmanager`), `ExitStack`, `match`-based command parser, `for/else` and `try/else`
19. Concurrency models (est 2): sandbox in its own process with a timeout, spinner thread while waiting for the model, the GIL in practice
20. Concurrent executors (est 2): `ThreadPoolExecutor` for running drill test suites in parallel, `as_completed` progress
21. Asynchronous programming (est 3): async httpx streaming, async subprocess sandbox, `asyncio.TaskGroup`, timeouts

### Part V: Metaprogramming

22. Dynamic attributes (est 2): `FrozenJSON`-style wrapper for responses, properties for derived stats, `__dir__`
23. Attribute descriptors (est 2): validated config fields (e.g. positive int, existing path), descriptor-declared tool parameters
24. Class metaprogramming (est 2): `__init_subclass__` auto-registers `Tool` subclasses (replacing `@tool`), class decorators, final refactor

---
name: design-patterns-pythonic
description: This skill should be used when the user asks to implement a design pattern in Python (builder, singleton, strategy, factory, observer, state, adapter, facade, decorator, composite, command, specification, null object, registry, event bus), asks "which pattern fits this", wants a dispatch `if/elif` chain replaced, wants a fluent/chainable API, or asks how to do a GoF pattern "the Pythonic way" instead of a Java-style class hierarchy. Distilled from ArjanCodes' example repo.
---

# Pythonic Design Patterns

GoF patterns re-expressed with closures, dataclasses, `Protocol`, and dict-dispatch instead of deep class hierarchies. Core bias: **a pattern is a shape, not a mandate for subclassing** — Python's first-class functions and structural typing usually give a lighter implementation than the textbook one.

## Before reaching for a pattern

1. Is this solving a real duplication/branching problem right now, or a hypothetical future one? If hypothetical, don't. (See `dry` example below — over-abstracting two coincidentally-similar functions is its own anti-pattern.)
2. Can a plain function or closure do it? Check the "Pythonic alternative" column before the "Classic OOP" column.
3. Only reach for an ABC/Protocol hierarchy when there are genuinely multiple interchangeable implementations behind one call site.

## Decision table

| Situation | Pattern | Pythonic technique | Example |
|---|---|---|---|
| `if/elif` chain picking behavior by type/string | Strategy | dict-of-callables or closures, not subclasses | [2022/strategy_pythonic](https://github.com/ArjanCodes/examples/tree/main/2022/strategy_pythonic) |
| Strategy needs config, not just behavior | Strategy w/ params | pass params via `__init__`/`functools.partial`, not extra methods | [2022/strategy_parameters](https://github.com/ArjanCodes/examples/tree/main/2022/strategy_parameters) |
| Need interchangeable object creators | Factory | dict-of-constructors or `Protocol` factory over ABC factory | [2022/factory_pythonic](https://github.com/ArjanCodes/examples/tree/main/2022/factory_pythonic) |
| Wrapping a 3rd-party client whose full API you don't want to expose | Adapter | composition + `functools.partial`, not subclassing the client | [2022/adapter](https://github.com/ArjanCodes/examples/tree/main/2022/adapter) |
| Multi-step subsystem calls need one entry point | Facade | one class/function hiding the steps | [2022/facade](https://github.com/ArjanCodes/examples/tree/main/2022/facade) |
| Need undoable/loggable actions | Command | callable objects with `execute`/`undo`; compare to a state-log alternative | [2022/command_with_undo](https://github.com/ArjanCodes/examples/tree/main/2022/command_with_undo), [2022/command_transaction_vs_state](https://github.com/ArjanCodes/examples/tree/main/2022/command_transaction_vs_state) |
| Dispatch chain is really a value match | Structural pattern matching | Python 3.10+ `match`, not `if/elif` | [2022/structural_pattern_matching](https://github.com/ArjanCodes/examples/tree/main/2022/structural_pattern_matching) |
| Runtime-discoverable plugins | Plugin system | shared base/`Protocol` + registration hook | [2022/plugin_system](https://github.com/ArjanCodes/examples/tree/main/2022/plugin_system) |
| Function needs cross-cutting behavior (logging, caching, auth) | Decorator | `functools.wraps`, stack multiple decorators deliberately (order matters) | [2023/decorator](https://github.com/ArjanCodes/examples/tree/main/2023/decorator), [2025/decorators](https://github.com/ArjanCodes/examples/tree/main/2025/decorators) |
| Observer/Strategy/Template Method without class ceremony | Function-based patterns | plain functions as callbacks instead of classes | [2023/funcpatterns](https://github.com/ArjanCodes/examples/tree/main/2023/funcpatterns) |
| Object behavior changes by internal state (draft/review/final) | State | `Protocol`-typed state classes, or a dict-based state table for simpler cases | [2023/state](https://github.com/ArjanCodes/examples/tree/main/2023/state), [2026/state](https://github.com/ArjanCodes/examples/tree/main/2026/state) (formalized into a reusable `StateMachine`) |
| Chained optional/error-prone computations | Maybe/railroad monad | build from scratch only to understand it — not a production dependency | [2023/monad](https://github.com/ArjanCodes/examples/tree/main/2023/monad) |
| Registering handlers by key without a growing `if/elif` | Registry | `@register_exporter("csv")` decorator populating a dict | [2025/registry](https://github.com/ArjanCodes/examples/tree/main/2025/registry) |
| Need exactly-one shared instance | Singleton | prefer module-level instance; if a class is required, compare `__new__`, metaclass, thread-safe variants and pick the simplest that's safe for your concurrency model | [2025/singleton](https://github.com/ArjanCodes/examples/tree/main/2025/singleton) |
| Multiple listeners react to one event | Observer / event bus | simple pub-sub, v1 vs a refined v2 | [2025/event](https://github.com/ArjanCodes/examples/tree/main/2025/event) |
| Chaining LLM agent steps (routing, fallback, tool selection) | Chain of Responsibility / Strategy on an agent | applied directly to a `pydantic_ai.Agent` pipeline | [2025/aidesign](https://github.com/ArjanCodes/examples/tree/main/2025/aidesign) |
| Fluent/chainable construction of an immutable object | Builder | frozen `@dataclass` + `Self`-typed chained methods | [2025/builder](https://github.com/ArjanCodes/examples/tree/main/2025/builder) |
| Tree/group structure where leaves and groups share an interface | Composite | shared `render()`/`total()` across leaf and container | [2026/composite](https://github.com/ArjanCodes/examples/tree/main/2026/composite) |
| Chainable API reading like a sentence (`.move().rotate().fade()`) | Fluent interface | methods return `Self` | [2026/fluent](https://github.com/ArjanCodes/examples/tree/main/2026/fluent) |
| Lazy/computed/validated attribute access | Descriptor | `__get__`/`__set__` from minimal example up to a cached-property | [2026/descriptors](https://github.com/ArjanCodes/examples/tree/main/2026/descriptors) |
| Composable filter/business rules (`rule_a & rule_b`) | Specification | `Rule` objects overloading `&`/`|`, optionally loaded from JSON/config | [2026/spec](https://github.com/ArjanCodes/examples/tree/main/2026/spec) |
| Type wraps a primitive but must enforce invariants (price can't be negative) | Value Object | subclass a primitive (or wrap in frozen dataclass) validating at construction, not at every use site | [2026/value](https://github.com/ArjanCodes/examples/tree/main/2026/value) |
| Replacing `Optional` + `if x is None:` scattered everywhere | Null Object | a no-op implementation of the same interface | [2026/none](https://github.com/ArjanCodes/examples/tree/main/2026/none) |
| Same pattern reimplemented across syntaxes (ABC vs function vs Protocol) to compare cost | Bridge (syntax-agnostic) | proves the pattern is independent of the syntax used to express it | [2022/bridge_pattern](https://github.com/ArjanCodes/examples/tree/main/2022/bridge_pattern) |

## Anti-pattern warning: don't force it

- An LLM-response wrapper built as ABC+Factory, simplified back down to plain functions once the "flexibility" turned out to be unused — the natural pattern was no pattern. [2026/pattern](https://github.com/ArjanCodes/examples/tree/main/2026/pattern)
- DRY-ing two functions that only *coincidentally* look similar produces a worse abstraction than the duplication it removed. Check whether the two things change for the same reason before merging them. [2026/dry](https://github.com/ArjanCodes/examples/tree/main/2026/dry)

## Deeper reference

For full before/after code shape per pattern and additional evolution examples (`badoo`, `funky`, `gui_architecture`'s MVC/MVP/MVVM comparison), see [references/catalog.md](references/catalog.md).

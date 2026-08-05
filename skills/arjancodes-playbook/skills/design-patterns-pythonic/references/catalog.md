# Pattern Catalog — Extended Notes

Deeper detail for entries in the main [SKILL.md](../SKILL.md) decision table, plus folders that didn't fit the table.

## Null Object — `2026/none`

Before: `location`, `battery_level`, `max_wind_speed` are all `Optional`, and `assign_delivery` is a pyramid of `if x is not None: ... else: return None` checks repeated for every field, plus an optional `diagnostics: RouteDiagnostics | None` checked at every call site.

After: a `prepare_drone(telemetry) -> ReadyDrone` step front-loads all the null checks once (raises `ValueError` early), so the body of `assign_delivery` operates on non-optional fields with zero `is None` branching. Diagnostics gets a `NullDiagnostics` implementing the same `Protocol` as `ConsoleDiagnostics`, defaulted as `diagnostics: RouteDiagnostics = NullDiagnostics()` — the call site never checks `if diagnostics is not None`.

```python
class RouteDiagnostics(Protocol):
    def record(self, message: str) -> None: ...

class NullDiagnostics:
    def record(self, message: str) -> None:
        pass  # no-op, satisfies the interface, no branching at call sites
```

**Lesson**: Null Object isn't "make a class called Null" — it's push the nullability check to one boundary (a validating constructor/factory) so the rest of the code can assume presence.

## Registry — `2025/registry`

```python
_registry: list[tuple[str, str, Callable[..., None]]] = []

def register_command(group: str, name: str):
    def decorator(func: Callable[..., None]):
        _registry.append((group, name, func))
        return func
    return decorator
```

Usage is `@register_command("export", "csv")` above a plain function — no base class, no `if format == "csv": ... elif format == "json":`. `get_registry()` returns the accumulated list for whatever dispatches on it (a CLI, a plugin loader). See `commands/` and `plugins/` subfolders in the same example for the dispatch side.

**Lesson**: when the set of "things by name" grows over time (formats, commands, exporters), a decorator-populated registry beats a manually maintained `if/elif` or `match` — new cases don't require touching the dispatcher.

## OOP-abuse ladder — `2024/badoo`

Same feature implemented 7 ways in sequence, each `_before`/`_after` pair showing the next refactor: `1_func` → `2_module` → `3_inheritance` → `4_abstractions` → `5_encapsulation` → `6_get_set` → `7_mixins`. The point isn't "the last one wins" — it's that each step is the *right* answer only once the previous one's limitation is actually hit. Jumping straight to mixins/abstractions for a two-function problem is over-engineering; staying at step 1 once you have five interchangeable variants is under-engineering.

**Lesson**: use this as a checklist when reviewing "is this abstraction justified yet" — name which step the current code is at and whether the next trigger condition has actually occurred.

## OO vs functional, three ways — `2024/funky`

Same problem solved once with classes, then three escalating functional versions (`2_functional`, `3_functional`, `4_functional`) — each adding a bit more functional-style composition. Useful for showing a Python dev coming from OOP-only backgrounds what the functional alternative actually looks like at increasing levels of commitment, not just "use functions."

## MVC vs MVP vs MVVM — `2022/gui_architecture`

Same Tkinter to-do app rebuilt three times (`mvc/`, `mvp/`, `mvvm/`), plus a `simple.py` baseline with no separation at all. All three patterns solve "keep UI code out of business logic" but move the state-sync responsibility to a different place:

- **MVC**: Controller mediates; View can still read Model directly.
- **MVP**: Presenter owns all View updates; View has no Model reference at all (more testable, more boilerplate).
- **MVVM**: ViewModel exposes observable state; View binds to it (less manual sync code, needs a binding mechanism).

**Lesson**: don't default to MVC out of habit — if the framework has data binding, MVVM removes more boilerplate; if you need the View to be a dumb, fully-mockable shell for testing, MVP is stricter than MVC.

## Bridge across syntaxes — `2022/bridge_pattern`

The same "bridge" abstraction (decouple an abstraction from its implementation so both vary independently) implemented three times: as ABC inheritance, as a plain function taking a callable, and as a `Protocol`. Confirms the *pattern* (decoupling two axes of variation) is separate from the *syntax* chosen to express it — don't assume "pattern X requires class hierarchy Y."

## Command with undo vs transaction log — `2022/command_with_undo`, `2022/command_transaction_vs_state`

Command pattern gives each action an `execute`/`undo` pair — good when undo logic is action-specific. The transaction/state-log alternative instead snapshots state before each action and restores wholesale on undo — simpler when actions are hard to invert individually (e.g., non-deterministic operations) but costs more memory per snapshot.

**Lesson**: pick Command when undo is cheap to express per-action; pick a state snapshot when it isn't.

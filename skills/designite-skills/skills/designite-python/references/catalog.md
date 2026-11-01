# DPy smell catalog

Every smell DPy (Designite for Python) reports, its rule, and how this skill finds it.

**Source** column:
- `DPy-paper` = "DPy: Code Smells Detection Tool for Python" (Boloori & Sharma, MSR 2025), Tables I and II. Exact rule.
- `DPy-docs` = designite-tools.com DPy feature pages (definition only, no threshold).
- `D-blog` = Designite architecture-smell blog posts (thresholds written for Java/C#; DPy's values are unpublished).
- `approx` = rule chosen for this skill.

**How** column: tool name = read its output (tools.md); `judge` = decide by reading code, report as "Claude-judged".

DPy treats both **classes and modules** as abstractions: a module's top-level functions are its
methods and its top-level variables its fields. A **component** is a Python package (folder).
DPy's size thresholds are Java's times 0.67 (Python is less verbose), which is why they differ from DesigniteJava.

## Architecture smells

| Smell | Rule | How | Source |
|---|---|---|---|
| Unstable Dependency | Package A depends on B and I(B) > I(A); I = Ce/(Ca+Ce). | pydeps + arch.sql | DPy-docs, formula D-blog |
| God Component | Package has > 30 modules or > 27,000 LOC. | radon raw + design.sql | D-blog values (DPy unpublished) |
| Feature Concentration | Modules of a package form unconnected groups in the import graph. LCC = groups / modules. Flag LCC >= 0.3 with >= 2 groups (the blog's scikit-learn example is flagged at 0.35). | judge from pydeps edges | D-blog, cutoff approx |
| Dense Structure | Average degree 2·E/V of the package graph >= 5. | graph.sql | D-blog |

DPy does not report Cyclic Dependency; pylint `cyclic-import` shows module cycles. List them under caveats, not as a DPy smell.

## Design smells

| Smell | Scope | Rule | How | Source |
|---|---|---|---|---|
| Multifaceted Abstraction | class, module | NOM > 3 and LCOM >= 0.8: methods split into groups that share no attributes. | design.sql lists NOM > 3 candidates; judge cohesion by reading which `self.x` each method uses | DPy-paper |
| Feature Envy | method | Uses another object's attributes/methods more than its own. | judge | DPy-docs |
| Deficient Encapsulation | class, module | Accesses non-public (`_name`) members of another class or module. | ruff `SLF001` (+ `from m import _x`) | DPy-docs (scikit-learn example) |
| Insufficient Modularization | class, module | NOPM > 20 or NOM > 30 or WMC > 100. | design.sql (radon) | DPy-paper |
| Hub-like Modularization | class, module | FAN-IN > 7 and FAN-OUT > 7. | graph.sql (module level); classes judge | DPy-paper |
| Broken Modularization | class, module | NOF > 4 and NOM = 0 (data-only class/module). | judge (`rg` classes with no `def`) | DPy-paper |
| Deep Hierarchy | class | DIT > 6. | pylint `too-many-ancestors` (`--max-parents=6`; counts library ancestors too, so confirm) | DPy-paper |
| Wide Hierarchy | class | NC > 5 direct subclasses. | `rg` base-class count | DPy-paper |
| Broken Hierarchy | class | Class and its supertype share no method names, and the supertype has no abstract method the class overrides. Skip classes with no methods (e.g. empty exception subclasses). | judge | DPy-paper |
| Rebellious Hierarchy | class | An overriding method contains only `pass`, `return` or `raise`. | `rg` candidates + confirm the method overrides one | DPy-paper |

## Implementation smells

| Smell | Rule | How | Source |
|---|---|---|---|
| Long Statement | > 80 characters. | ruff `E501` with `--line-length 80` (per physical line) | DPy-paper |
| Long Parameter List | > 4 parameters (`self`/`cls` not counted here). | lizard (design.sql subtracts self/cls) | DPy-paper |
| Long Method | > 67 lines. | lizard `length` | DPy-paper |
| Long Identifier | Function, class, field or local variable name > 20 chars. | `rg` | DPy-paper |
| Empty Catch Clause | `except` block containing only `pass` or a `return`. | ruff `S110` (pass) + `rg` (return) | DPy-paper |
| Complex Method | McCabe CC > 7. | lizard `ccn` | DPy-paper |
| Complex Conditional | > 2 logical operators (`and`/`or`) in one condition. | pylint `too-many-boolean-expressions` with `--max-bool-expr=3` | DPy-paper |
| Missing Default | `match` statement without `case _:`. | `rg` + read | DPy-paper |
| Long Lambda Function | Lambda > 80 characters. | `rg` | DPy-paper |
| Long Message Chain | More than 2 methods chained (`a.b().c().d()`). | `rg` (fluent pandas chains are idiomatic; say so) | DPy-paper |
| Magic Number | Numeric literal other than 0, 1, -1 without a name. | ruff `PLR2004` (comparisons only) + judge others | DPy-paper |

## ML smells

| Smell | Rule | How |
|---|---|---|
| Ambiguous Merge Key | `merge()` without `on=` (pandas joins on all shared columns). | dslinter `merge-parameter-pandas` + `rg` |
| Broken NaN Check | Comparing with `np.nan` (`==` is always False); use `np.isnan`/`isna`. | ruff `PLW0177`, dslinter `nan-numpy` |
| Chain Indexing | `df["x"]["y"]`; use `df.loc[...]`. | dslinter `chain-indexing-pandas` + `rg` |
| Forward Bypass | Calling `model.forward(x)` directly skips hooks; call `model(x)`. | dslinter `forward-pytorch` |
| Type Blind Conversion | `.values` on a DataFrame; use `.to_numpy()`. | ruff `PD011` |
| Unnecessary Iteration | Looping over a DataFrame (`iterrows`, `itertuples`, index loops) where vectorized ops work. | dslinter `unnecessary-iteration-pandas` + `rg iterrows` |

Check ML smells only in modules that import pandas, numpy or torch. dslinter misses many cases; always run the `rg` fallbacks too.

## Refactoring hints

| Smell | Usual fix |
|---|---|
| Multifaceted / Insufficient Modularization | Split the class or module by responsibility (field groups) |
| Broken Modularization | Move behavior next to the data, or use a dataclass with methods |
| Deficient Encapsulation | Add a public API on the owner instead of reaching into `_private` |
| Hub-like | Split the module; depend on smaller interfaces |
| Deep / Wide / Broken / Rebellious Hierarchy | Prefer composition; add intermediate base classes; drop inheritance that is not IS-A |
| Feature Envy | Move the function to the module/class whose data it uses |
| Complex / Long Method, Complex Conditional | Extract function; guard clauses; lookup tables |
| Long Parameter List | Dataclass parameter object, or keyword-only grouping |
| Long Message Chain | Introduce an intermediate variable or a method on the first object |
| Magic Number | Module-level UPPER_CASE constant |
| Empty Catch | Handle, log or re-raise; catch narrower exceptions |
| ML smells | Use the replacement named in the rule |
| Unstable Dependency / Dense Structure | Depend on stable abstractions; cut cross-package imports |
| God Component / Feature Concentration | Split the package along its groups |

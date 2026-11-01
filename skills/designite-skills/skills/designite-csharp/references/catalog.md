# Designite (C#) smell catalog

Every smell Designite for C# reports, its rule, and how this skill finds it.

Designite C# publishes its smell list but not its thresholds. Its catalog is DesigniteJava's plus
Duplicate Abstraction, Unfactored Hierarchy and Duplicate Code, so the thresholds here are
DesigniteJava's defaults (`ThresholdsDTO.java`) unless marked otherwise.

**Source** column:
- `DJ-code` = DesigniteJava community source; same rule assumed for C#.
- `D-blog` = Designite blog "Does your architecture smell?" (written with a C# case study).
- `approx` = rule not published; chosen for this skill.

**How** column: tool name = read its output (tools.md); `judge` = decide by reading code, report as "Claude-judged".
A **component** is a namespace. Metrics: NOF fields, NOPF public fields, NOM methods, NOPM public
methods, WMC sum of method CC, NC children, DIT depth of inheritance.

## Architecture smells

| Smell | Rule | How | Source |
|---|---|---|---|
| Cyclic Dependency | Namespaces depend on each other directly or indirectly. One finding per cycle. | graph.sql + arch.sql | D-blog |
| Unstable Dependency | A depends on B and I(B) > I(A); I = Ce/(Ca+Ce). | arch.sql | D-blog |
| Ambiguous Interface | A namespace that is not small (>= 5 types) offers only one public/internal non-static method. | judge | D-blog, size approx |
| God Component | > 30 types or > 27,000 LOC in a namespace. | design.sql | D-blog |
| Feature Concentration | Types in the namespace form unrelated groups (association/inheritance). LCC = groups / types; flag LCC >= 0.3 with >= 2 groups (blog example flagged at 0.5). | judge | D-blog, cutoff approx |
| Scattered Functionality | Many methods (>= 5) in one namespace use the same two other namespaces together. | judge | D-blog, cutoff approx |
| Dense Structure | Average degree 2·E/V of the namespace graph >= 5. | graph.sql | D-blog |

## Design smells

| Smell | Rule | How | Source |
|---|---|---|---|
| Imperative Abstraction | Exactly one public method, and it is > 50 lines. | judge (lizard `length` per method) | DJ-code |
| Unnecessary Abstraction | No methods and <= 5 fields. Ignore enums, marker interfaces, records used as DTOs if that is the design. | judge (`rg` types with no methods) | DJ-code |
| Multifaceted Abstraction | LCOM >= 0.8 and NOF >= 7 and NOM >= 7: methods split into groups that share no fields. | judge on NOM >= 7 classes | DJ-code |
| Unutilized Abstraction | No other project type references it. Skip entry points, controllers, DI-registered types, tests. | judge (`rg -w TypeName`) | DJ-code |
| Duplicate Abstraction | Two types with the same name, or the same members/implementation, in different places. | design.sql (same name) + judge | approx |
| Feature Envy | A method uses another type's members more than its own type's. | judge | approx |
| Deficient Encapsulation | NOPF > 0 (public fields). Auto-properties are encapsulated and do not count. | .NET analyzer `CA1051` (instance fields) + `CA2211` (static) | DJ-code |
| Unexploited Encapsulation | One method type-checks (`is`, `as`, type `switch`) 2+ types of the same hierarchy. | judge (`rg '\bis [A-Z]'`) | DJ-code |
| Broken Modularization | No methods and >= 5 fields/auto-properties (data class). | judge | DJ-code |
| Insufficient Modularization | NOPM >= 20, or NOM >= 30, or WMC >= 100. | design.sql (NOM, WMC from lizard) | DJ-code |
| Hub-like Modularization | Fan-in >= 20 and fan-out >= 20 project types. | judge for large classes | DJ-code |
| Cyclically-dependent Modularization | The type is in a dependency cycle with other types. | judge | DJ-code |
| Wide Hierarchy | > 10 direct subtypes. | `rg` base-type count | DJ-code |
| Deep Hierarchy | DIT > 6 (project types). | judge | DJ-code |
| Multipath Hierarchy | One direct supertype is also an ancestor of another direct supertype (interfaces count). | judge | DJ-code |
| Cyclic Hierarchy | A type is its own ancestor. | judge (compiler rejects most cases) | DJ-code |
| Unfactored Hierarchy | Sibling subtypes repeat the same members; they belong in the parent. | CPD duplicates between siblings + judge | approx |
| Rebellious Hierarchy | An override has an empty body or only `throw` (e.g. `throw new NotSupportedException()`). | `rg` + confirm it overrides | DJ-code |
| Missing Hierarchy | One method type-checks 2+ types that are not its own ancestors. | judge | DJ-code |
| Broken Hierarchy | Has a base type and public methods, but overrides/implements none of the base's members. | judge | DJ-code |

## Implementation smells

| Smell | Rule | How | Source |
|---|---|---|---|
| Abstract Function Call From Constructor | A constructor calls an abstract method. | `CA2214` (any virtual/abstract), confirm abstract | DJ-code |
| Complex Conditional | An `if` condition with >= 2 `&&`/`||`. | `rg` | DJ-code |
| Complex Method | CC >= 8 (Designite does not count `&&`/`||`). | lizard `ccn` (does count them; recount borderline) | DJ-code |
| Empty Catch Clause | A catch block with no statements. | `rg` (CA1031 only flags catching `Exception`, empty or not) | DJ-code |
| Long Identifier | A parameter, local or field name >= 30 chars. | `rg` | DJ-code |
| Long Method | >= 100 lines. | lizard `length` | DJ-code |
| Long Parameter List | >= 5 parameters. | lizard `params` | DJ-code |
| Long Statement | A line > 120 chars after trimming. | `rg` | DJ-code |
| Magic Number | A number literal other than 0 or 1 in a method, not in an array initializer or const. | `rg` + judge | DJ-code |
| Missing Default | A `switch` statement without `default`. | `rg` + read | DJ-code |
| Duplicate Code | Repeated code blocks. | PMD CPD (`--language cs`) | approx (>= 70 tokens) |

## Testability smells (rules not published)

| Smell | Rule used here | How |
|---|---|---|
| Hard-wired Dependency | Creates concrete project collaborators with `new` instead of receiving them (constructor injection). Ignore DTOs, exceptions, collections, `Options`. | judge (`rg 'new [A-Z]\w+\('`) |
| Global State | Mutable static fields or properties. | `CA2211` (public ones) + `rg 'static (?!readonly|class|void)'` |
| Excessive Dependency | Fan-out >= 20, or a constructor with many injected dependencies (>= 7 parameters is a strong hint). | judge + lizard `params` on constructors |
| Law of Demeter Violation | Reaching through objects: `a.B.C.Do()`. Ignore LINQ, fluent builders, `options.Value`. | judge |

## Test smells (no maintained C# tool; judge from test code)

Find test methods by attribute: xUnit `[Fact]`/`[Theory]`, NUnit `[Test]`/`[TestCase]`, MSTest `[TestMethod]`.

| Smell | Rule |
|---|---|
| Assertion Roulette | >= 2 assertions without a message (xUnit asserts have no message parameter; use FluentAssertions `because` or split the test). |
| Conditional Test Logic | if/loop/switch inside a test. |
| Constructor Initialization | NUnit/MSTest test class sets up state in a constructor instead of `[SetUp]`/`[TestInitialize]`. Not a smell in xUnit (constructors are its setup). |
| Eager Test | One test calls several different production methods. |
| Empty Test | Test method with no statements. |
| Exception Handling | try/catch or throw in a test instead of `Assert.Throws`. |
| Ignored Test | `[Fact(Skip = ...)]`, `[Ignore]`. |
| Unknown Test | Test with no assertion (no `Assert.`, `Should`, `Verify`). |

## Refactoring hints

| Smell | Usual fix |
|---|---|
| Multifaceted / Insufficient Modularization | Extract Class along field groups; partial classes do not fix it |
| Imperative Abstraction | Fold the operation into the type that owns its data |
| Unnecessary / Broken Modularization | Move behavior next to the data |
| Deficient Encapsulation | Fields to private + properties or intention-revealing methods |
| Unexploited / Missing Hierarchy | Polymorphism instead of type checks |
| Hub-like / Excessive Dependency | Split the class; depend on interfaces |
| Cyclic Dependency | Move the shared abstraction to its own namespace/project; dependency inversion |
| Unstable Dependency | Depend on abstractions in stable namespaces |
| Deep / Wide / Broken / Rebellious Hierarchy | Composition over inheritance; intermediate base types; implement only interfaces you honor |
| Unfactored Hierarchy / Duplicate Code | Pull Up Method; extract shared helper |
| Duplicate Abstraction | Merge or rename types |
| Feature Envy | Move Method |
| Complex / Long Method, Complex Conditional | Extract Method, guard clauses, pattern matching |
| Long Parameter List | Parameter object / options record |
| Magic Number | `const` or `static readonly` with a name |
| Empty Catch | Handle, log or rethrow; catch narrower types |
| Hard-wired Dependency | Constructor injection |
| Global State | Instance state passed explicitly; `static readonly` immutables |

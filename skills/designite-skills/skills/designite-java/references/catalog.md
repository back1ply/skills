# DesigniteJava smell catalog

Every smell DesigniteJava reports, its rule, and how this skill finds it.

**Source** column:
- `DJ-code` = DesigniteJava community source (`ThresholdsDTO.java` and the detectors). Exact rule.
- `DJ-blog` = Designite docs and blog ("Does your architecture smell?").
- `approx` = Designite does not publish the rule (Professional-only feature). The rule here is this skill's choice.

**How** column:
- `CK`/`PMD`/`TSD` = read it from that tool's output (see tools.md, queries.md).
- `judge` = no tool covers it. Apply the rule by reading the code. Report it as "Claude-judged".

Metric names (Designite): NOF fields, NOPF public fields, NOM methods (constructors included),
NOPM public methods, WMC sum of method CC, NC children, DIT inheritance depth, LCOM, FANIN, FANOUT.

## Architecture smells (component = Java package)

| Smell | Rule | How | Source |
|---|---|---|---|
| Cyclic Dependency | Two or more packages depend on each other directly or indirectly. Report each cycle once. | package graph query | DJ-blog |
| Unstable Dependency | Package A depends on B and I(B) > I(A), where I = Ce/(Ca+Ce) (Ce outgoing, Ca incoming package deps). | package graph query | DJ-blog |
| Ambiguous Interface | A package that is not small (>= 5 classes) offers a single public non-static method in total. | CK query + judge | DJ-blog, size approx |
| God Component | Package has > 30 classes or > 27,000 LOC. | CK query | DJ-blog |
| Feature Concentration | Classes in the package form unrelated groups (no association or inheritance between groups). LCC = groups / classes. Flag when LCC >= 0.3 and there are >= 2 groups. | judge | DJ-blog, cutoff approx |
| Scattered Functionality | Many methods (>= 5) in one package use the same two other packages together; those two may share one responsibility. | judge | DJ-blog, cutoff approx |
| Dense Structure | Average degree of the package graph, 2·E/V, >= 5. At most one per project. | package graph query | DJ-blog |

## Design smells (per class)

| Smell | Rule | How | Source |
|---|---|---|---|
| Imperative Abstraction | NOPM = 1 and that method's LOC > 50. | CK class+method | DJ-code |
| Unnecessary Abstraction | NOM = 0 and NOF <= 5. | CK | DJ-code |
| Multifaceted Abstraction | LCOM >= 0.8 and NOF >= 7 and NOM >= 7. | CK (`lcom*` stands in for LCOM) | DJ-code, metric approx |
| Unutilized Abstraction | No project class references it (FANIN = 0), or it has supertypes none of which is referenced. Skip tests, `main` classes, framework entry points. | CK `fanin` + judge | DJ-code |
| Feature Envy | A method uses another class's members more than its own class's. | judge | approx |
| Deficient Encapsulation | NOPF > 0. Public `static final` constants trigger it too; mention when that is the only cause. | CK `publicFieldsQty` | DJ-code |
| Unexploited Encapsulation | One method has `instanceof` checks on 2+ types of the same hierarchy. | judge (`rg instanceof`) | DJ-code |
| Broken Modularization | NOM = 0 and NOF >= 5 (data class). | CK | DJ-code |
| Insufficient Modularization | NOPM >= 20, or NOM >= 30, or WMC >= 100. | CK | DJ-code |
| Hub-like Modularization | FANIN >= 20 and FANOUT >= 20. | CK | DJ-code |
| Cyclically-dependent Modularization | The class is in a dependency cycle with other classes. | judge | DJ-code |
| Wide Hierarchy | NC > 10. | CK `noc` | DJ-code |
| Deep Hierarchy | DIT > 6. CK's `dit` counts `Object`, so use CK `dit > 7`. | CK | DJ-code |
| Multipath Hierarchy | One direct supertype is also an ancestor of another direct supertype. | judge | DJ-code |
| Cyclic Hierarchy | A type is its own ancestor. | judge | DJ-code |
| Rebellious Hierarchy | A method overrides an inherited method (same name and parameter types) with an empty body or only a `throw`. | judge | DJ-code |
| Missing Hierarchy | One method has `instanceof` checks on 2+ types that are not its own ancestors. | judge | DJ-code |
| Broken Hierarchy | Has a supertype and public methods, but overrides none of a supertype's public/abstract/interface methods. | judge | DJ-code |

## Implementation smells (per method)

| Smell | Rule | How | Source |
|---|---|---|---|
| Abstract Function Call From Constructor | A constructor calls an abstract method. | PMD `ConstructorCallsOverridableMethod` (broader: any overridable), then confirm it is abstract | DJ-code |
| Complex Conditional | An `if` condition with >= 3 sub-expressions (>= 2 `&&`/`||`). | `rg` query | DJ-code |
| Complex Method | CC >= 8. Designite counts if, case (not default), for, foreach, while, do; not `&&`/`||`/ternary/catch. | PMD `CyclomaticComplexity` (also counts `&&`/`||`, so it reports more); confirm borderline cases | DJ-code |
| Empty Catch Clause | A catch block with no statements (comment-only counts as empty). | PMD `EmptyCatchBlock` | DJ-code |
| Long Identifier | A parameter, local variable or used field name >= 30 chars. | PMD `LongVariable` | DJ-code |
| Long Method | Method body >= 100 lines. | CK method `loc` (source lines only, so it reports less) | DJ-code |
| Long Parameter List | >= 5 parameters. | PMD `ExcessiveParameterList` / CK `parametersQty` | DJ-code |
| Long Statement | A line of a method body > 120 chars after trimming and collapsing spaces. | `rg` query | DJ-code |
| Magic Number | A number literal other than 0 or 1 in a method body, not inside an array initializer. | `rg` query + judge (PMD `AvoidLiteralsInIfCondition` catches the ones in conditions) | DJ-code |
| Missing Default | A `switch` statement without `default`. | PMD `NonExhaustiveSwitch` (does not flag exhaustive enum switches) | DJ-code |

## Testability smells (Designite Professional; rules not published)

| Smell | Rule used here | How | Source |
|---|---|---|---|
| Hard-wired Dependency | A class creates concrete project collaborators with `new` instead of receiving them. Ignore value objects, DTOs, exceptions, collections. | judge (`rg "new [A-Z]"`) | approx |
| Global State | Mutable static fields. | PMD `MutableStaticState`, `AssignmentToNonFinalStatic` | approx |
| Excessive Dependency | FANOUT >= 20. | CK `fanout` / PMD `CouplingBetweenObjects` | approx |
| Law of Demeter Violation | Reaching through objects: `a.getB().getC().do()`. Ignore fluent builders and streams. | PMD `LawOfDemeter` (very noisy; filter) | approx |

## Test smells

| Smell | Rule | How |
|---|---|---|
| Assertion Roulette | Several assertions without messages. | TSD `Assertion Roulette` / PMD `UnitTestAssertionsShouldIncludeMessage` |
| Conditional Test Logic | if/loop/switch inside a test. | TSD |
| Constructor Initialization | Test class sets up state in a constructor. | TSD |
| Eager Test | One test calls many production methods. Needs the production file in TSD's input. | TSD |
| Empty Test | Test method with no statements. | TSD `EmptyTest` |
| Exception Handling | try/catch or throw inside a test. | TSD `Exception Catching Throwing` |
| Ignored Test | `@Ignore` / `@Disabled`. | TSD `IgnoredTest` |
| Unknown Test | Test with no assertion. | TSD / PMD `UnitTestShouldIncludeAssert` |

TSDetect reports more columns (General Fixture, Mystery Guest, Sleepy Test, ...). They are not Designite smells; leave them out of the main tables.

## Refactoring hints

| Smell | Usual fix |
|---|---|
| Multifaceted / Insufficient Modularization | Extract Class along the field groups; split by responsibility |
| Imperative Abstraction | Fold the operation into the class that owns its data |
| Unnecessary / Broken Modularization | Move behavior into the data class, or merge into its user |
| Deficient Encapsulation | Make fields private, add intention-revealing methods |
| Unexploited / Missing Hierarchy | Replace type checks with polymorphism (Replace Conditional with Polymorphism) |
| Hub-like / Excessive Dependency | Split the class; introduce interfaces; apply dependency inversion |
| Cyclic Dependency / Cyclically-dependent Modularization | Break the cycle with an interface in the depended-on package, or move the shared type |
| Unstable Dependency | Depend on an abstraction in a stable package |
| Deep / Wide Hierarchy | Collapse levels; prefer composition; add intermediate types for wide ones |
| Rebellious / Broken Hierarchy | Replace inheritance with delegation |
| Feature Envy | Move Method to the class it uses |
| Complex Method / Conditional, Long Method | Extract Method; decompose conditional; guard clauses |
| Long Parameter List | Introduce Parameter Object |
| Magic Number | Named constant |
| Empty Catch | Handle, log, or rethrow |
| Hard-wired Dependency | Constructor injection |
| Global State | Pass state explicitly; make it final/immutable |
| God Component / Feature Concentration | Split the package along its groups |

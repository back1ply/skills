---
name: designite-java
description: Reproduces DesigniteJava's code quality analysis for Java without Designite, using open-source tools (CK metrics, PMD, TSDetect) plus Claude's judgment for the smells no tool covers. Reports architecture, design, implementation, testability and test smells with causes and refactoring suggestions, using Designite's own thresholds. Use when the user asks for a Designite-style or design-smell analysis, code smells, technical debt, architecture smells, god classes, or OO metrics (WMC, LCOM, DIT, fan-in/out) on Java code (.java, Maven, Gradle).
---

# Designite-style analysis for Java

Goal: the same findings DesigniteJava would report, from free tools plus reading code.

- [references/catalog.md](references/catalog.md): every smell, Designite's rule and threshold, which tool covers it, refactoring hints.
- [references/tools.md](references/tools.md): setup, exact commands, output formats, where tools differ from Designite.
- [references/report-template.md](references/report-template.md): report layout.
- `assets/`: PMD ruleset and DuckDB queries that apply Designite's thresholds.

## Workflow

Copy this checklist and tick it off:

```
- [ ] 1. Scope: SRC = source root; skip generated code. OUT = $SRC/.designite
- [ ] 2. Tools present (tools.md setup); java -version >= 17; duckdb, rg, jq available
- [ ] 3. Run CK, PMD, import scan, TSDetect (tools.md "Run")
- [ ] 4. Query: design.sql, graph.sql + arch.sql, PMD counts, TSDetect columns, rg line checks
- [ ] 5. Judge the uncovered smells on hotspot classes (below)
- [ ] 6. Verify a sample of tool hits by reading code; drop false positives
- [ ] 7. Write $OUT/report.md (report-template.md)
```

Step 3 commands are in tools.md. Run each tool separately so one failure does not hide the others;
if a tool fails, keep going and list it under "Not checked".

## Step 5: smells Claude decides

No tool covers these; apply the catalog rule by reading code. Limit to hotspots (top 15 classes by
findings + WMC, and every class the queries flagged) unless the user asks for everything:

- Feature Envy, Multipath / Cyclic / Rebellious / Missing / Broken Hierarchy, Unexploited Encapsulation
- Cyclically-dependent Modularization (class-level cycles among flagged classes)
- Feature Concentration and Scattered Functionality (per package, from the import graph)
- Hard-wired Dependency; filter PMD LawOfDemeter hits down to real reach-throughs
- Magic Number candidates from the rg check (ignore 0, 1, array initializers, constant definitions)

Mark these findings *judged* in the report.

## Step 6: verification

Tool output is a proxy, not Designite itself. Before reporting:
- Read the code for every design smell you list as a top priority.
- `Unnecessary Abstraction` hits on enums/marker interfaces, and `Unutilized Abstraction` hits on entry
  points, tests or framework classes are usually not worth reporting. Note them as dropped.
- `Deficient Encapsulation` caused only by `public static final` constants: mention, low priority.
- PMD `CyclomaticComplexity` counts `&&`/`||`; Designite does not. Recount borderline (CC 8-10) methods.

## Output

`$OUT/report.md` following the template, plus a short chat summary: counts by category, the top 5
priorities with file:line and fix, and caveats. Suggest refactorings; do not change code unless asked.

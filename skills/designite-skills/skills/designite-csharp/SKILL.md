---
name: designite-csharp
description: Reproduces Designite for C# code quality analysis without Designite, using open-source tools (lizard, .NET analyzers via an injected MSBuild config, PMD CPD, ripgrep + DuckDB) plus Claude's judgment for the smells no tool covers. Reports architecture, design, implementation, testability and test smells with Designite's thresholds, causes and refactoring suggestions. Use when the user asks for a Designite-style or design-smell analysis, code smells, technical debt, architecture smells, god classes, duplicate code, or OO metrics on C#/.NET code (.cs, .csproj, .sln, .slnx).
---

# Designite-style analysis for C#

Goal: the same findings Designite for C# would report, from free tools plus reading code.

- [references/catalog.md](references/catalog.md): every smell, its rule and threshold, which tool covers it, refactoring hints.
- [references/tools.md](references/tools.md): exact commands, output formats, where tools differ from Designite.
- [references/report-template.md](references/report-template.md): report layout.
- `assets/`: MSBuild injection files (`designite.targets`, `designite.globalconfig`) and DuckDB queries.

## Workflow

Copy this checklist and tick it off:

```
- [ ] 1. Scope: SRC = repo root; CODE = production source folder(s); find the .sln/.slnx. OUT = $SRC/.designite
- [ ] 2. uv, duckdb, jq, rg; dotnet SDK (step 2); Java 17+ and PMD (step 4)
- [ ] 3. Run lizard, dotnet build with analyzers, rg scans, CPD (tools.md "Run")
- [ ] 4. Query: design.sql, graph.sql + arch.sql, SARIF filter, CPD rows, rg pattern checks
- [ ] 5. Judge the uncovered smells on hotspot types (below)
- [ ] 6. Verify a sample of tool hits by reading code; drop false positives
- [ ] 7. Write $OUT/report.md (report-template.md)
```

Ask before running `dotnet build` if the user has not asked for a build: it runs the repo's own
build logic and writes bin/obj. Without it, the analysis still works (lizard, rg, CPD, judgment);
note the gap. Run each tool separately; if one fails, keep going and list it under "Not checked".

## Step 5: smells Claude decides

C# has the most judged smells, because no working metrics tool covers NOPM, NOF, fan-in/out, DIT
or LCOM. Limit to hotspots (top 15 types by WMC and findings, every type the queries flagged) unless
the user asks for everything. For each hotspot type, read it and record NOF, NOPF, NOPM, base types
and the project types it uses, then apply the catalog rules:

- Imperative / Unnecessary / Multifaceted / Unutilized Abstraction, Broken Modularization, Hub-like
- Hierarchy smells (Deep, Multipath, Missing, Broken, Unfactored), Unexploited Encapsulation, Feature Envy
- Ambiguous Interface, Feature Concentration, Scattered Functionality (per namespace)
- Testability smells and test smells (catalog has the rules and how to find test methods)
- Missing Default in each `switch`, Magic Number candidates, Long Identifier candidates

Mark these findings *judged* in the report.

## Step 6: verification

- Read the code for every design smell listed as a top priority.
- lizard counts `&&`/`||` in CC; Designite does not. Recount methods with CC 8-10.
- Partial classes: add up all parts before judging size.
- DI-registered, reflection-loaded and framework types (controllers, handlers, `Program`) are not
  Unutilized Abstraction.
- CPD hits in generated files (`*.g.cs`, `*.Designer.cs`, migrations) are not Duplicate Code.

## Output

`$OUT/report.md` following the template, plus a short chat summary: counts by category, top 5
priorities with file:line and fix, and caveats (which steps ran). Suggest refactorings; do not
change code unless asked.

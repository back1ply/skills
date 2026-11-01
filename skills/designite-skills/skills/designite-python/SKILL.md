---
name: designite-python
description: Reproduces DPy (Designite for Python) code quality analysis without Designite, using open-source tools (radon, lizard, pydeps, ruff, pylint, dslinter) plus Claude's judgment for the smells no tool covers. Reports architecture, design (class and module level), implementation and ML-specific smells (pandas, NumPy, PyTorch) with DPy's published thresholds, causes and refactoring suggestions. Use when the user asks for a Designite/DPy-style or design-smell analysis, code smells, technical debt, god classes/modules, OO metrics (WMC, LCOM, fan-in/out), or pandas/ML code smells on Python code (.py, pyproject.toml).
---

# DPy-style analysis for Python

Goal: the same findings DPy would report, from free tools plus reading code.

- [references/catalog.md](references/catalog.md): every DPy smell, its rule and threshold, which tool covers it, refactoring hints.
- [references/tools.md](references/tools.md): exact commands, output formats, where tools differ from DPy.
- [references/report-template.md](references/report-template.md): report layout.
- `assets/`: DuckDB queries that apply DPy's thresholds to the tool output.

## Workflow

Copy this checklist and tick it off:

```
- [ ] 1. Scope: SRC = repo root; PKG = package folder(s) (not venvs, build, vendored code). OUT = $SRC/.designite
- [ ] 2. uv, ruff, duckdb, jq, rg available
- [ ] 3. Run radon, lizard, pydeps, ruff, pylint; dslinter only if pandas/numpy/torch are imported (tools.md "Run")
- [ ] 4. Query: design.sql, graph.sql + arch.sql, ruff/pylint/dslinter counts, rg pattern checks
- [ ] 5. Judge the uncovered smells on hotspots (below)
- [ ] 6. Verify a sample of tool hits by reading code; drop false positives
- [ ] 7. Write $OUT/report.md (report-template.md)
```

Run each tool separately; if one fails, keep going and list it under "Not checked". Tests usually
dominate long-method and magic-number counts: report test code in its own group, or exclude it if the
user only cares about production code.

## Step 5: smells Claude decides

Apply the catalog rule by reading code, limited to hotspots (the top 15 modules/classes by findings
and WMC, plus every candidate a query listed) unless the user asks for everything:

- Multifaceted Abstraction: for each NOM > 3 candidate, map which `self.` attributes (or module
  globals) each method uses; flag when the methods split into groups sharing none (LCOM >= 0.8).
- Feature Envy, Broken Hierarchy, Broken Modularization (NOF > 4, NOM = 0), class-level Hub-like.
- Rebellious Hierarchy: confirm each rg candidate really overrides a parent method.
- Feature Concentration: per package, check whether its modules form unconnected import groups.
- Magic Numbers outside comparisons, Missing Default in `match`, Long Lambda over 80 chars.

Mark these findings *judged* in the report.

## Step 6: verification

- Read the code for every design smell listed as a top priority.
- Fluent pandas chains (`df.groupby().agg().reset_index()`) trip Long Message Chain; report them
  but say they are idiomatic.
- `too-many-ancestors` counts library base classes (e.g. Django, unittest); check the project depth.
- ML smells need a real DataFrame/tensor; confirm the receiver type before reporting.

## Output

`$OUT/report.md` following the template (use an "ML" section instead of "Testability / Test"),
plus a short chat summary: counts by category, top 5 priorities with file:line and fix, and caveats.
Suggest refactorings; do not change code unless asked.

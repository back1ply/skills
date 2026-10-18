---
name: quality-pass
description: This skill should be used after writing or changing code, before committing, or when the user asks to "run a quality pass", "review my changes", "clean this up", "check code quality", or wants test-first work, an architecture scan, a duplicate-function hunt, or a performance pass. Routes each changed file to the best installed review skill (test-guard, clean-code-guard, docs-guard, writing-dax-measures and others) and falls back to built-in checks when a skill is missing.
argument-hint: "[tdd | deep | dupes | perf | re | <path>...]  (default: review the current changes)"
---

# Quality pass

One pass over the code that changed, using whichever review skills are installed. Arguments: `$ARGUMENTS`

This pass checks quality: clarity, tests, docs and design. It does not hunt for correctness bugs; for
that, suggest a bug-focused review (such as `/code-review`) at the end.

## How skills are found

A skill counts as **installed** when a skill with that name appears in your available-skills list, with
or without a plugin prefix (`tdd` and `mattpocock-skills:tdd` both count as `tdd`). Never read a skill
from a hard-coded path. When a skill named below is missing, use the fallback given for it and list it
under "not installed" in the final summary, with its install hint from the table at the end.

## 1. Pick the mode from the arguments

| Argument | Mode | Uses (if installed) |
|---|---|---|
| (none) or paths | **review**: review what changed | test-guard, clean-code-guard, docs-guard, file-type skills (section 3) |
| `tdd` | **build**: new feature or bug fix, test first | tdd, then review |
| `deep` | **architecture**: find deepening opportunities | improve-codebase-architecture, codebase-design |
| `dupes` | **duplicates**: functions that do the same thing under different names | finding-duplicate-functions |
| `perf` | **performance**: profile, then speed up the hot path | python-performance-optimization |
| `re` | **reverse engineering**: read a binary, format or live process | reverse-engineering, reverse-engineer-anything |

Several arguments combine (e.g. `tdd deep`). Unknown words are treated as paths.

## 2. Design lens (modes that edit code: review, tdd, deep, perf)

Apply briefly before changing anything. `dupes` and `re` only read, so they skip it.

- **Remove before you add.** First delete what the change makes unnecessary: dead code, unused
  parameters, guards for cases that cannot happen, stub files and duplicate helpers. Then build on the
  smaller base. Prefer leaving the code simpler than you found it over adding a new layer.
- **Deep modules.** When the change touches a module's interface or adds a seam, use `codebase-design`
  if installed. Fallback: keep interfaces small and push complexity behind them; a module whose interface
  is as complex as its body should probably be merged into its caller.
- **Python design.** For Python changes that add classes, patterns or layers, use `arjancodes-playbook`
  skills if installed (prefer functions, dataclasses and `Protocol` over class hierarchies).

## 3. Review mode (default)

1. **Scope.** The files named in the arguments; otherwise the changed files:
   `git diff --name-only HEAD` plus untracked files from `git status --porcelain`. In a repo with no
   commits yet, use `git status --porcelain` alone. Outside a git repo, ask which files to review.
   Skip generated, vendored, lock and data files (json/csv/yaml config).
2. **Route each file to its primary reviewer:**

   | Files | Skill | Fallback when not installed |
   |---|---|---|
   | Tests: `test_*.py`, `*_test.py`, `*.test.*`, `*.spec.*`, `*Test.php`, `*_test.go`, `tests/`, `__tests__/`, `spec/` | `test-guard` | Each test checks behaviour through a public interface, can fail, asserts something specific, and has no copy-pasted setup that a fixture would remove |
   | DAX: `*.dax`, measures in `*.tmdl` / `*.bim` | `writing-dax-measures` | Variables over repeated expressions, `DIVIDE` over `/`, no `FILTER` on whole tables where a column filter works |
   | GSC: `*.gsc` | `gsc-writer` | Review as code (next row) |
   | Docs: `*.md`, `*.mdx`, `*.rst`, READMEs | `docs-guard` | Every function, flag, path and example named in the doc exists in the code; no filler |
   | All other code | `clean-code-guard` | Names say what things do, functions do one thing, no dead code, no speculative options, no copy-paste |

   Then add the secondary checks:
   - `.py` files with long or tangled functions: also `python-refactor` if installed.
   - Code files whose docstrings or doc comments changed: also `docs-guard` on those comments.
   - Any other installed skill made for that file type or framework (for example a Power Query or
     Terraform skill): use it alongside the primary reviewer.
3. **Report** findings grouped by reviewer, most severe first, then fix the ones that are clearly right
   and in scope. Keep behaviour unchanged unless a finding is a real bug. Run the project's own checks
   (`just check`, `npm test`, `pytest`, …) after fixing.
4. Respect the project's rules (AGENTS.md / CLAUDE.md): review gates, commit rules, code-health tools.

## 4. Other modes

- **tdd**: use `tdd` and follow its red, green loop for the requested change. Fallback: one failing test,
  the least code to pass it, repeat; never write all the tests first. Then run review mode on what changed.
- **deep**: if `improve-codebase-architecture` is installed, it may be user-only (not invocable by you);
  in that case tell the user to run `/improve-codebase-architecture` themselves and stop. Otherwise use it,
  or fall back to `codebase-design`: list the 3 to 5 shallowest modules in the recently changed areas, say
  what merging or deepening each would buy, and let the user pick. Change nothing until they do.
- **dupes**: if `finding-duplicate-functions` is installed, warn that it starts several subagents (it
  costs more than other modes), then use it. Fallback: list functions by name and signature, group the
  ones that do the same job, and report the groups without changing code.
- **perf**: use `python-performance-optimization` for Python; for other languages use that language's
  profiler. Always measure before and after; change only the measured hot path.
- **re**: use `reverse-engineering` or `reverse-engineer-anything`, whichever is installed. Stay
  read-only on anything live. If neither is installed, say so and stop.

## 5. Finish

End with one short list: what each skill found, what was fixed, what was left and why, and which skills
were not installed (with install hints). If code changed, suggest a bug-focused review.

## Install hints

| Skill | Install |
|---|---|
| test-guard, clean-code-guard, docs-guard | `npx skills add amElnagdy/guard-skills -g` |
| tdd, codebase-design, improve-codebase-architecture | Claude Code: `/plugin install mattpocock-skills@claude-plugins-official`; other agents: `npx skills add mattpocock/skills -g` |
| python-refactor | `npx skills add acaprino/alfio-claude-plugins -g -s python-refactor` |
| python-performance-optimization | `npx skills add wshobson/agents -g -s python-performance-optimization` |
| finding-duplicate-functions | `npx skills add obra/superpowers-lab -g -s finding-duplicate-functions` |
| writing-dax-measures, arjancodes-playbook | `npx skills add back1ply/skills -g` |

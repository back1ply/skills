# Guardrail tools

IMP's rule 19 says standards are enforced by machines. The site keeps a directory of over 500 guardrail tools, sorted by what they check and by stack. This file is a map to that directory, written for this skill. **For tool picks in a specific language, fetch the live category page.** The directory changes often and its curation belongs to the site.

Directory home: <https://impatientprogramming.org/tools/>

## Tools built by the IMP authors

| Tool | Stack | What it gates | Rule | Repo |
|---|---|---|---|---|
| `exhale` | Ruby / Rails | Duplicated code and methods that got more complex; kept duplication must be declared in the Contract | 12 | <https://github.com/tools4imps/exhale-ruby> |
| `flinch` | Go | Mutation testing on Contract-covered code; each kill credited to an obligation | 20, 26 | <https://github.com/tools4imps/flinch> |
| `covenant` | Elixir | Every Contract obligation needs a passing test; publishes contract coverage | 29 | <https://github.com/tools4imps/covenant> |
| `praxis` | Any | LLM reviewers check files against conventions written in a README spec | 19 | <https://github.com/zarpay/praxis-cli> |
| `qualm` | Any | Asks a decision model whether a reviewer would push back on each changed file | 27 | <https://github.com/tools4imps/qualm> |

Suggested order inside a PR: the agent builds (inhale), then covenant checks the Contract, exhale checks duplication and complexity, flinch runs mutations, praxis checks house rules, qualm asks for a second opinion, and green merges itself.

## Directory categories

| Category | What it covers | Rules | Live page |
|---|---|---|---|
| The Contract | Executable specs, spec-driven agent tools, API contract tests, traceability | 13, 20, 29 | <https://impatientprogramming.org/tools/contract/> |
| Generated inputs | Property-based testing, fuzzing, deterministic simulation | 20, 28 | <https://impatientprogramming.org/tools/generated-inputs/> |
| Proof | Model checkers, spec languages, verifiers, design-by-contract libraries | 13, 16 | <https://impatientprogramming.org/tools/proof/> |
| Tests that bite | Mutation testing, approval/snapshot testing, test-suite health | 20, 26 | <https://impatientprogramming.org/tools/tests-that-bite/> |
| Breathing out | Duplication finders, dead code, unused dependencies, complexity limits | 12 | <https://impatientprogramming.org/tools/breathing-out/> |
| Structure | Architecture and import-boundary checks (e.g. ArchUnit, dependency-cruiser, Packwerk, import-linter) | 19 | <https://impatientprogramming.org/tools/structure/> |
| Standards | Default linters, formatters, type checkers; custom-rule engines (Semgrep, ast-grep); hook runners | 19 | <https://impatientprogramming.org/tools/standards/> |
| Safety | Secrets, vulnerable dependencies, infrastructure and CI-workflow scanning | 24 | <https://impatientprogramming.org/tools/safety/> |
| What users see | End-to-end/UI testing, AI test agents, accessibility, visual regression, performance budgets | 18, 24 | <https://impatientprogramming.org/tools/what-users-see/> |
| The agent itself | Agent hooks, sandboxes, parallel-agent managers, LLM eval gates | 6, 15, 21 | <https://impatientprogramming.org/tools/the-agent/> |
| Review and merge | AI code review, merge queues, auto-merge, feature flags | 3, 23, 27 | <https://impatientprogramming.org/tools/review-and-merge/> |
| Measurement | Delivery metrics, recording which code agents wrote | 9 | <https://impatientprogramming.org/tools/measurement/> |

## How to use this when setting up a repo

1. Detect the stack from manifest files (`package.json`, `pyproject.toml`, `Gemfile`, `go.mod`, `Cargo.toml`, `mix.exs`, and so on).
2. Check what's already wired in (CI config, pre-commit hooks, lint configs) before suggesting anything new.
3. For each missing gate, fetch the relevant category page above and pick the tool it recommends for that stack. Prefer the stack's default tool over a niche one.
4. Start with the cheapest high-value gates: standards (lint, format, types), then safety (secrets, dependencies), then breathing out (duplication, complexity), then tests that bite (mutation testing).
5. Add each gate to CI so it fires on every change (rule 24), not only locally.

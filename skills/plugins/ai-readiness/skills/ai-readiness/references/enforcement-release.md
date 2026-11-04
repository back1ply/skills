# Enforcement & Release: the four dimensions

Source: "AI Readiness for Engineering Organizations" (Jurgen De Smet, 2026), pp. 76-93, the
online assessment (howreadyfor.ai/assess), and per dimension the author's Substack essay and the
site's long-form page (URLs in each `Read:` line). Level wording follows the online version.

Ladder: 1 Blind, 2 Tacit, 3 Visible but inert, 4 Acted on, 5 Durable. Levels 1-3 need a human to
choose; 4-5 the system acts. Score the worst case in scope, not the typical one. If nothing can
be produced as evidence, that is a 1. Part theme: "Is the rule a wall or a wish?" An agent obeys
what it meets while it runs (a failing check), not what sits on a page it never opens.

## Contents
- 17 · Hard guardrails vs cultural agreements
- 18 · Architecture enforcement in CI
- 19 · Dependency hygiene
- 20 · Release discipline

## 17 · Hard guardrails vs cultural agreements
Read: field guide pp. 78-81; essay https://jurgendesmet.substack.com/p/ai-readiness-hard-guardrails-vs-cultural (2026-06-09); page https://howreadyfor.ai/d/hard-guardrails-vs-cultural-agreements
**Question:** Take the standards your teams rely on anywhere in this scope and sort them into two columns: the ones a machine refuses to allow through, and the ones people have agreed to. Do you know how long the second column is?
**Why agents care:** An agent never sat in the standup or read the wiki, so every standard that is only agreed is invisible to it; it runs through open space and stops only at walls. Rules files (CLAUDE.md, .cursorrules) are still advisory: read, followed some of the time. Per the guide (2026), Google's advisory-mode static analysis left 84% of filed bugs unfixed until findings became compiler errors and review-time gates; 66% of projects define static analysis but 37% enforce it for new contributions. What changed Google's result was the mechanism: findings shown inside review with no separate dashboard (Tricorder) and specific checks as compile errors (Error Prone). Per the essay (2026-06-09): across 246 Java projects only 8.76% of flagged SonarQube issues were fixed in advisory mode (median 19 days for those that were); a GPT-4o best case with governance rules literally in the prompt caught 73% of violations (27% slipped through), while a CI gate has a zero miss rate for the check it runs; and half of 2,443 instrumented engineers did not test, so "we agree to test" is only an agreement unless a gate forces test execution.
**Signals you are low:**
- Standards live in a document and nobody can say which a machine would stop.
- "Someone would catch that in review" is said about real standards.
- The AI guidance is a rules file, and reading it is treated as the same as obeying it.
- Nobody owns the job of moving costly agreements from the agreed column to the enforced one.

| Level | What it means here | Tell (what settles it) |
|---|---|---|
| 1 Blind | No list; nobody has asked which standards a machine would refuse. | Ask three engineers to name the coding standards: three different lists, none marking what the build refuses. |
| 2 Tacit | Experienced people know which rules are real; nothing is written. | A newcomer and a five-year veteran give different answers on what the pipeline enforces; the sort lives inside the veteran. |
| 3 Visible but inert | Both columns exist on a page; nothing has moved from one to the other. | Find the page and its date; if nothing moved from agreed to enforced since, it is a record of the problem, not a practice that shrinks it. |
| 4 Acted on | New standards arrive with an enforcement decision; old agreements get converted. | The last standard added is mechanically refused today, and the gate arrived with the standard, not a year later after a bad breach. |
| 5 Durable | Enforcement survives new languages, new teams and the release that wants an exception. | Count pipelines where the gate is disabled or warn-only: zero, or each with an owner and an expiry date. Anything else is enforcement in name only. |

**Score 4 when:** the enforced/agreed sort is a maintained practice that routes costly agreed standards toward enforcement, not a one-off workshop.
**Evidence to collect:**
- Run the sort per standard: if it is violated, does something mechanical stop it reaching production? Enforced: compiler errors, blocking lint, CI gates, pre-commit hooks, type constraints, failing scans. Agreed: wiki, onboarding docs, "someone would catch it in review", boundaries in heads. The shorter the agreed column, the higher the score.
- Open the CI config(s) and list which jobs can fail the merge; check branch-protection or required-status settings if visible. Standards named in docs with no matching job, lint rule or hook are in the agreed column.
- Grep lint, type-check and test configs for `warn`, `continue-on-error`, `allow_failure`, `|| true`, `--exit-zero`, `noqa`/`eslint-disable` volume (the essay cites a study of 7,357 Python suppressions where half hid no active warning and some hid later ones: a growing suppression count means the agreed column is growing by stealth). Warn-only gates cap the score at 3; any with owner and expiry comment supports 5. Results that only live on a separate dashboard are advisory mode: 3 at most.
- For 5, check new repos, languages and acquired teams arrive inside the same gates (org template, reusable workflow, repo-creation template); a repo outside the template is in the agreed column.
- Open hook config (`.pre-commit-config.yaml`, `.husky/`, `lefthook.yml`) and check CI repeats the hooks, since hooks can be skipped locally.
- Find the standards doc or rules file (`CONTRIBUTING.md`, `CLAUDE.md`, wiki export) and run `git log --format=%ad -1 -- <file>`; compare to the dates of newest CI checks (`git log --diff-filter=A -- .github/workflows`). Docs updated without matching gates means 3.
- Take the last 2-3 standards added in history and find the check that enforces each, and whether it landed in the same change.
**Small-team note:** the "newcomer vs veteran" tell has no second person; instead, ask whether the owner could list from memory which rules the build refuses, and check that list against CI. Solo repos can reach 4 with a pre-commit plus CI gate per standard.
**Cheapest moves up:**
- 1 to 2/3: write the two-column sort once, with the owner of each agreed item.
- 3 to 4: pick the review comment you keep retyping, name the earliest stage that would stop it (type, lint, hook, CI gate) and build that one gate this week.
- 4 to 5: turn every warn-only gate to fail, or give it an owner and expiry date.
- Any step: move findings from a dashboard into the review or build, and promote specific high-cost checks to errors.

## 18 · Architecture enforcement in CI
Read: field guide pp. 82-85; essay https://jurgendesmet.substack.com/p/ai-readiness-architecture-enforcement (2026-08-11); page https://howreadyfor.ai/d/architecture-enforcement-in-ci
**Question:** Does the build fail on an architectural violation anywhere in your scope, or do you rely on a reviewer noticing the one line that inverted a dependency?
**Why agents care:** "Dependency" here means internal module boundaries, not third-party packages. Architecture used to be held by a reviewer who could read what one human could write; that ratio is gone. A change can be clean, tested and green while inverting a layer, and the agent obeys only what fails at execution time. The guide cites a preprint ("constraint decay") that stacking architecture rules in prose degrades agent correctness, so words are the wrong instrument. Per the essay (2026-08-11): the May 2026 preprint (eight web frameworks) put the cost of imposing Clean Architecture at 9.1 points (+/-1.6) and of fully stacked constraints at about 30 points of assertion pass rate; hold the figures lightly. A December 2025 study (3 models, 5 runs each) had one model break a stated hexagonal architecture in 4 of 5 runs with functionally correct code: tests stay green, and the failure is model-dependent, not a rate to quote. Apiiro (vendor research, Sept 2025, not peer-reviewed): syntax errors down 76%, logic bugs down over 60%, architectural design flaws up 153%, privilege-escalation paths up 322%. A fitness function is model-independent and yours to maintain; it is an established technique (Thoughtworks radar since 2018).
**Signals you are low:**
- If an agent inverted a layer dependency today, nothing in CI would go red before a human looked.
- Load-bearing boundaries live in a diagram, a decision record or one senior's head.
- No one owns the architecture ruleset by name.
- Review is the boundary control while reviewers are already buried (Faros telemetry, ~22,000 developers: per the guide, 2026, median review time up roughly fivefold and a third more PRs merged with no review; per the essay, 2026-08-11, the figure is 31.3%. A velocity and oversight measure, not an architecture-drift one).

| Level | What it means here | Tell (what settles it) |
|---|---|---|
| 1 Blind | No stated rules; what may depend on what is taste. | Try to write the diagram as a list of forbidden dependencies; you cannot, or two people write different lists. |
| 2 Tacit | Senior reviewers hold the boundaries and catch breaches by eye. | Ask what share of merges a boundary-aware reviewer reads now vs two years ago; if it fell and nothing replaced them, protection fell too. |
| 3 Visible but inert | A scan reports violations; the build goes green anyway. | The violation list is longer than last quarter and every one of those changes merged: the scan only counts. |
| 4 Acted on | A scoped fitness function fails the build on a boundary breach. | The last rule-breaking change was refused by the build, which named the rule; the rule was chosen, not a tool default. |
| 5 Durable | Rules evolve with the architecture; exceptions are dated, not permanent. | Every entry in the check's exception list has a name and a date, and the rules changed the last time the architecture did. |

**Score 4 when:** a scoped fitness function (ArchUnit, dependency-cruiser, import-linter, NetArchTest or similar) fails the build on a breach of the one or two boundaries that would hurt most, with a named owner for the ruleset. It catches structural rules only, not design judgment.
**Evidence to collect:**
- Search for boundary tooling: `.dependency-cruiser.js`, `.importlinter`, `pyproject.toml [tool.importlinter]`, ArchUnit/NetArchTest test classes, `eslint-plugin-boundaries`, `no-restricted-imports`, Bazel visibility, Go `internal/` plus depguard. None found means 1-2 (unless rules are written down, then 2).
- Prose is not a gate: an ADR, diagram or layering rules in CLAUDE.md are intent. Boundaries held only there score 2-3, never 4.
- Boundaries need not be textbook layers: any rule the owner would defend in review counts (this module owns the payments table, billing must not reach into auth internals, no cycles between two packages). With no defended boundary at all, score 1.
- Confirm the check runs in the CI file as a required step that exits non-zero, not report-only or `allow_failure`. Report-only (or a periodic cycle report) is 3. Scope matters: one or two boundaries, failing rarely and rightly; a noisy gate that flags legitimate refactors, or one often bypassed, trains people to ignore it.
- Read its exception/baseline list (`ignore`, `forbidden` allowances, baseline file); `git blame` it. Entries with no name or date cap at 4; dated, owned entries support 5.
- Check `git log` on the rule file vs recent structural commits (new modules, moved packages): rules untouched while structure changed suggests inherited, not maintained.
- Find a commit that tripped the rule in CI history and see whether the message names the rule. Planting a deliberate violation is not read-only: do it only with the owner's permission, in a temporary worktree that is discarded after.
**Small-team note:** "reviewer" tells do not apply to a solo codebase; score on whether a machine check exists, since no reviewer is the real situation. One import-linter or dependency-cruiser contract in CI is a legitimate 4.
**Cheapest moves up:**
- 1 to 2: write the forbidden-dependency list from the diagram and give the ruleset a named owner.
- 2 or 3 to 4: encode one or two load-bearing rules as a CI gate that fails; keep it tight, since a noisy gate trains people to ignore it.
- 4 to 5: date and own every exception, and review the rules whenever the architecture changes.
- Any step: demote ADRs, diagrams and review to "why", and let the build hold the boundary. A fitness function catches structural rules only (who may depend on whom, no cycles), not design judgment such as a swelling god-object.

## 19 · Dependency hygiene
Read: field guide pp. 86-89; essay https://jurgendesmet.substack.com/p/ai-readiness-dependency-hygiene-and (2026-07-28); page https://howreadyfor.ai/d/dependency-hygiene
**Question:** Of the dependencies running in production anywhere in your scope, how many did a human actually choose?
**Why agents care:** A model writes the import line from a frozen snapshot of the world and does not check the live registry, so it can name a package that does not exist. Hallucinated names repeat and converge across models, which makes them an attacker's shortlist (slopsquatting). Per the guide (2026): commercial models hallucinated package names at least 5.2% of the time and open models 21.7%, and 43% of invented names recurred across all 10 reruns. Review habits read the import line as plumbing, so the decision slips past everyone. Per the essay (2026-07-28): Endor Labs found only 1 in 5 agent-recommended versions safe (exists, no known vulnerability), up to 49% known-vulnerable and about a third nonexistent; a 2026 re-run on frontier models (199,845 prompts) narrowed hallucination to 4.62-6.10%, better but not gone, and 127 invented names recurred across five models from different labs, so waiting for newer models does not close it. Upgrades fail the same way: Sonatype found 27.76% of 36,870 AI upgrade recommendations named versions that do not exist (the everyday cost is a wedged pipeline, not a breach), against 454,600 new malicious packages in 2025. Gates built for a human chooser still pass whatever the model chose. Patch lag is also real: per the page, months pass between a fix being published and projects running it.
**Signals you are low:**
- Nobody can say what share of this quarter's new dependencies a human chose vs an agent added.
- Update bots auto-merge dependency changes with no cooldown and no existence check.
- Agents recommend packages from training data, not the live registry.
- The new import is the one line in every diff that review treats as plumbing.
- Nobody can say what share of imports a human chose; making import origin visible comes first, since you cannot gate a decision you cannot see.

| Level | What it means here | Tell (what settles it) |
|---|---|---|
| 1 Blind | No inventory; nobody could list what runs in production or who chose it. | Count the packages in the main service's lockfile and find who accepted the last one added: the count surprises you and nobody signed. |
| 2 Tacit | Careful engineers vet their own imports; nothing covers the rest. | Ask the authors of the last ten additions why they chose that package: some answer in detail, others do not recall deciding. |
| 3 Visible but inert | Scanners list vulnerable and outdated packages; nothing stops a new one arriving. | A dependency added in the last month was examined only by a scan that ran after merge: the gate is downstream of the decision. |
| 4 Acted on | New imports are gated: the package exists, is not brand new, and a person approved it. | The last new dependency was blocked until checks passed and a person accepted it, rather than arriving inside an unrelated change. |
| 5 Durable | The gate holds across every repository and updates land fast enough to matter. | Gate-enabled repos vs total is broad, and the last critical upgrade reached production quickly. |

**Score 4 when:** imports are grounded in the live registry and gated by an existence and cooldown check, with a human on the import line (manifest reviewed as seriously as the function).
**Evidence to collect:**
- Read-only spot check on the last merged AI-assisted PR with a dependency change: does each package exist and for over a week; does the claimed version exist; did anyone decide to add it, or did it ride in under a reviewed function; would a freshly registered package at that exact name have been caught by anything that runs? "No" to the last is the essay's readiness ceiling: 3 at most.
- Count lockfile entries (`package-lock.json`, `poetry.lock`, `go.sum`, `Cargo.lock`) and compare direct vs transitive; note whether lockfiles are committed at all (not committed is 1-2).
- Run `git log -p --since=90.days -- <manifest or lockfile>` (or `git log --follow --format='%h %an %s' -- requirements.txt`) and judge for the last ten additions whether a PR description, linked ticket or approval explains the choice.
- Open CI and bot config (`dependabot.yml`, `renovate.json`, workflows): look for auto-merge, a minimum release age/cooldown (`minimumReleaseAge`, `cooldown`), required review on manifest paths (CODEOWNERS entry for manifests), and a pre-merge step that checks a new package exists and is not brand new. Scan-only after merge is 3; pre-merge existence, provenance and age check plus a named approver is 4. Bots may notice and propose freely; the gate sits between proposal and merge. Look for bot PRs that failed on unpublished versions (the upgrade trap) and for agent tooling with a live-registry lookup step.
- Check whether the gate config is shared (org-level template, reusable workflow) or per repo; count repos covered vs total for 5; automated update PRs must go through the gate, not around it, and new repos must inherit it.
- Measure upgrade lag: date a critical advisory fix vs the commit bumping it (`git log -S'<package>@<version>'`).
**Small-team note:** "a person approved it" in a solo repo means a deliberate manifest-only commit or PR that you review separately from feature code, plus the automated existence and age check. Do not score 4 on self-approval inside a mixed change.
**Cheapest moves up:**
- 1 to 2/3: generate the dependency inventory and commit the lockfile; add a scanner.
- 3 to 4: add a required pre-merge check on manifest changes (existence plus minimum age) and require a human approval on that path via CODEOWNERS.
- 1 to 3: make import origin visible (who or what added each new dependency) before gating anything.
- 3 to 4: turn off bot auto-merge or add a cooldown (even a few days turns "installed before anyone noticed" into "caught before it shipped"); give agents a tool to check the live registry (the guide, 2026, cites safe-version share rising from about 1 in 5 to about 57% with registry lookup, still not trust-blind).

## 20 · Release discipline
Read: field guide pp. 90-93; essay https://jurgendesmet.substack.com/p/ai-readiness-release-discipline-and (2026-07-14); page https://howreadyfor.ai/d/release-discipline
**Question:** When something you released last month changed behaviour, how did the people depending on it find out? And would that still work at the rate your scope now ships?
**Why agents care:** Consumers depend on what they observe, not what is documented (Hyrum's Law), and AI multiplies observable behaviours faster than commits. Producers can now ship faster than consumers absorb, and consumer-side agents write against stale contracts: per the guide (2026), models complete deprecated API use from a quarter to over a third of the time, and 70-90% with outdated context. Release notes and version numbers are narrative channels that cannot keep pace; the guide cites 44% of manifesting npm breaking changes arriving in minor and patch releases. Per the essay (2026-07-14): that is the Venturini et al. npm study (TOSEM 2023), where about 12% of dependent packages hit breaking changes in non-major updates; the Deprecated Usage Rate study (ICSE 2025, 7 LLMs) found 25-38% overall, 70-90% with outdated context and still 9-18% with the current API in context, so consumer-side agents cannot be fixed by showing them the new contract. Lehman's Law V (release content statistically invariant) is the consumer absorption ceiling that generation breaks. The essay's own test: count how many people inside the org detected the last downstream break before the ticket; zero is a debugging cadence shared with customers.
**Signals you are low:**
- A consumer who wanted to know what changed would have to ask you.
- The version number is the breaking-change defense, never checked against what AI actually shipped.
- "They'll find out when something breaks" would be said out loud.
- The last downstream break was detected by the customer, with zero people inside the org knowing first.

| Level | What it means here | Tell (what settles it) |
|---|---|---|
| 1 Blind | Consumers find out by breaking; nothing announces what changed. | Take the last downstream breakage and count who inside the org knew before the customer: zero. |
| 2 Tacit | Certain teams warn consumers personally because they know them. | The list of who was told before the last interface change matches who knows your team socially. |
| 3 Visible but inert | Release notes and versions are published; nothing verifies they match what shipped. | Compare last release notes to the actual diff: a behaviour changed that the notes do not mention. |
| 4 Acted on | The runtime signals the change: deprecation headers, alerts on a changed signature. | The last deprecation shipped was announced by the runtime to callers, and you can see who was still calling it. |
| 5 Durable | Visibility keeps pace with release tempo; consumer impact is known before shipping. | The system can answer "who calls the interface I am about to change" before shipping, including for a service launched last month. |

**Score 4 when:** change visibility is engineered into the runtime (deprecation/sunset headers, schema-version tags, signature-change alerts, deprecation-usage metrics) at code-generation tempo. Scale the mechanism to the situation; the principle is visibility at the pace of change.
**Evidence to collect:**
- Look for contract checks in CI: OpenAPI/proto/GraphQL diff tools (`buf breaking`, `oasdiff`, `graphql-inspector`), API snapshot or public-signature tests, contract tests (Pact). Absent is 1-3; present and failing the build on breaking diffs is toward 4.
- Grep the code for deprecation signalling: `Deprecation`/`Sunset` response headers, `@deprecated` with runtime warnings, a metric labelled by deprecated endpoint, schema-version headers. Docs-only deprecation is 3.
- Check the team's definition of "breaking" (the essay's Hyrum's-Law reading): does it cover observable behaviour (field order, enum coercion, error formats, defaults) or only the documented contract? Contract-only is 3 at best.
- Compare the last two or three release notes or CHANGELOG entries to `git diff <tag1> <tag2>` for public surfaces; unreported behaviour changes mean 3 at best. Check whether the changelog is generated from the diff (higher) or hand-written.
- Check if versions are enforced against the diff (semver bump tooling that blocks a patch release containing a breaking contract diff).
- Look for consumer discovery: API gateway or access logs by client, usage metrics, a consumer registry, a code-search or dependents list. If answering "who calls this" needs a manual hunt, it is under 5. For 5, check coverage on a service launched recently, not only the interface that once caused an incident.
- Reference shapes (mechanisms differ, the principle is visibility in the data path): Kubernetes returns a `Warning` header (RFC 7234) on deprecated calls and increments `apiserver_requested_deprecated_apis`, labelled by group, version, resource and removal release, with beta APIs kept nine months or three minor releases; Stripe pins each account to the API version of its first call, walks responses back through version-change modules, and publishes a short explicit list of non-breaking changes. Few teams can build either, so score the principle, not the scale.
**Small-team note:** with no external consumers, score on the interfaces others rely on (CLI flags, file formats, DB schema, internal services, scheduled jobs); the instrument has no "not applicable", so if nobody is downstream say so beside the score rather than inflating it. For a one-person codebase with a few known consumers, a manual notice step is 3 (a person chooses); a contract-diff check that fails the build plus a runtime deprecation signal is a real 4.
**Cheapest moves up:**
- 1 to 2/3: keep a list of consumers per interface and publish release notes generated from the diff.
- 3 to 4: add a breaking-change diff to CI for the main contract (schema/proto/OpenAPI) and a deprecation header or log line on retired endpoints; cheap forms are a Slack alert on public signature changes and a schema-version header on responses.
- 4 to 5: add a usage metric per deprecated endpoint or client so impact is queryable before a change ships.

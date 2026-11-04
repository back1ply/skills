# Truth Signals: the four dimensions

Source: "AI Readiness for Engineering Organizations" (Jurgen De Smet, 2026), pp. 27-43, and the
online assessment (howreadyfor.ai/assess). Level wording follows the online version. The levels are
observed from client engagements; the cited research only explains why each dimension is worth scoring.

Part premise: every later control assumes honest signals. An AI author acts on a false green,
a hollow test or an unwatched revert rate faster and more confidently than a human would. Score the
worst case in scope, not the typical one. If nobody can produce the evidence, that is a 1.

## Contents
- 5 · CI Reliability: does red mean broken and green mean safe?
- 6 · Test Meaningfulness: would the suite notice a behaviour change?
- 7 · Change Absorption: how much merged work comes back out?
- 8 · Technical Debt: is the debt priced and inside the AI plan?

## 5 · CI Reliability
Read: field guide pp. 29-31; https://jurgendesmet.substack.com/p/ai-readiness-ci-reliability; https://howreadyfor.ai/d/ci-reliability
**Question:** Somewhere in your scope a pipeline went red this week. Did anybody investigate it, or did they press rerun, and would you defend that choice?
**Why agents care:** AI does not slow down when the signal is unreliable; it floods the signal with more code (per the guide (2026)). CI is the last mechanical gate once human review stops scaling, so a gate that lies in either direction lets defects through at volume. Slow feedback also means an agent pushes several changes before it learns whether the first one worked (the guide's figure: three pushes per one answer). Our inference, not the sources': an agent cannot tell a real failure from noise, so it either "fixes" code that was never broken or retries until green.
**Signals you are low:**
- The standard reply to red is "rerun it", not "what failed?"
- Developers rerun green builds because they do not quite trust the pass (silent failures: ignored exit codes, cache bugs, artifact errors). Per the guide (2026), in a 142,387-job industrial study 11% of successful builds were rerun and 51% of reruns started from an already-passed job. Per the essay (2026-04-14), the silent failures were artifact errors (28%), caching bugs (23%) and ignored exit codes (18%).
- Nobody can state the flake rate; nobody tracks it.
- Getting back to green takes hours, not minutes.
- Failures increasingly surface after merge, where they are costlier to diagnose.
Calibration, per the essay (2026-04-14) unless noted: a 4,000-test suite with 0.01% flakiness per test fails about 33% of runs on noise (0.03% gives about 70%; the guide has the same arithmetic). CircleCI's 2026 data puts the main-branch success rate at 70.8% against a 90% benchmark, and median time to recover a green build at 72 minutes. Use these as reference points for "minutes, not hours", not as pass marks.

| Level | What it means here | Tell (what settles it) |
|---|---|---|
| 1 Blind | Nobody knows the flake rate. Rerunning is the reflex and nothing counts it. | Count failed runs in last month's pipeline history followed by a rerun with no code change. If nothing records that and nobody can give the share, nothing is counting. |
| 2 Tacit | A few people know which tests cannot be trusted; everyone else asks them. | Who decides whether a red build is worth investigating? A person rather than a rule means the signal is interpreted, not trusted. |
| 3 Visible but inert | Flake rate is measured and reported. Nothing quarantines or blocks anything. | Find the flakiest test and what happened to it. Still in the blocking suite, last action a rerun: the measurement connects to nothing. |
| 4 Acted on | A flaky test is quarantined automatically; reruns are budgeted, not unlimited (counted and capped, and the flake rate has an accountable owner). | Last test that started flaking was quarantined or failed the build automatically because a rate crossed a threshold, not because someone got annoyed. |
| 5 Durable | The signal holds as the suite grows; new repositories inherit the same guarantees (feedback stays fast enough that people wait for it; the flake budget holds in a late-release week). | Flake rate and time-to-first-signal over the last year: flat or falling while the suite grew, new repos starting inside the same limits. |

**Score 4 when:** red deterministically means broken (flake rate tracked and driven down), so the team's instinct on red is to investigate, and feedback arrives in minutes. Zero flakiness is not required; trust is.
**Evidence to collect:**
- Open the CI config (`.github/workflows/`, `.gitlab-ci.yml`, `Jenkinsfile`, `.circleci/`, `azure-pipelines.yml`). Grep for `retry`, `rerun`, `flaky`, `quarantine`, `continue-on-error`, `allow_failure`, `|| true`. Blanket retries with no budget or counter = level 2-3; failures swallowed by `|| true` or ignored exit codes = a silent-failure path (green can lie).
- Test-runner config: look for a rerun plugin (e.g. pytest-rerunfailures, jest retryTimes, `retries` in Playwright/Cypress) and whether anything records which tests needed a retry. Retry with no record = level 1-2; record that auto-quarantines or fails past a threshold = level 4.
- Read CI run history via the platform CLI or API if available (e.g. `gh run list --json conclusion,headSha,attempt`): runs with attempt > 1 on the same SHA are reruns. Report the share of failed-then-rerun-then-green runs; no history access means say "unmeasured", not a guess. Also count reruns whose first attempt passed: they show distrust of green, the half of the problem teams miss.
- Search for a quarantine list or tag (`grep -ri "quarantine\|@flaky\|skip.*flak" tests/ ci/`) and check its age with `git log -1 --format=%cd -- <file>`. A list that has grown for months with no owner = level 3.
- Check for required status checks / branch protection config in the repo (rulesets, `CODEOWNERS`-adjacent settings) to see whether CI actually blocks merge.
- Time the pipeline from the last runs' start-to-finish; hours rather than minutes caps the score at 3.
**Cheapest moves up:**
- 1 to 2/3: count reruns-without-change from run history and publish the share weekly.
- 3 to 4: add an automatic quarantine rule keyed on a flake threshold and put a budget on reruns.
- Close silent-failure paths (ignored exit codes, unverified caches) before chasing flaky tests.

## 6 · Test Meaningfulness
Read: field guide pp. 32-34; https://jurgendesmet.substack.com/p/ai-readiness-test-meaningfulness; https://howreadyfor.ai/d/test-meaningfulness
**Question:** Take a function anywhere in your scope, move a boundary by one or flip a comparison, and run the suite. Would anything fail, or would it stay green?
**Why agents care:** A test does two things: it runs code (execution) and it states what the answer should be (the oracle). A model supplies execution cheaply but can only infer the oracle from the implementation, so tests it writes after the code mirror the code and confirm a bug as readily as a fix. Coverage targets then reward exactly this, and an agent will hit the number without protecting anything.
**Signals you are low:**
- Tests are generated from the implementation after the code is written.
- Coverage is high and rising, yet real regressions still reach production.
- A passing suite is treated as proof of correctness.
- Assertions are dense and opaque; a failure does not say what broke.
- Nobody can say which tests would survive a deliberate behaviour change.
Named patterns: "Fake Test Coverage" (tests that hit the numbers without testing behaviour; per the guide (2026), an analysis of 300+ repositories found it in 40-50% of AI-generated code) and "Assertion Roulette" (many assertions per test method, so a failure does not say which one fired). Anti-pattern: answering shallow tests by generating more of them, which adds assertions, not oracles. Per the guide (2026), coverage is a weak predictor of fault detection (ICSE 2014), and Google found raw coverage "not reliably actionable".

| Level | What it means here | Tell (what settles it) |
|---|---|---|
| 1 Blind | No account of what the suite protects, and no coverage figure either. | Ask what would break if someone changed a boundary condition in the most important function. A guess, and nobody offers to try it, is level 1. |
| 2 Tacit | Certain people write tests that would catch a regression; others produce coverage. | Read assertions in two recent test files by different authors. One specifies behaviour, one restates the implementation, and the pipeline treats them the same. |
| 3 Visible but inert | Coverage is measured and gated. Nothing measures whether a test would catch a fault. | Change a comparison operator in a covered function and run the suite. Still green while the report calls the line covered: the gate measures execution, not protection. |
| 4 Acted on | Introduced faults are caught mechanically, and a suite that misses them fails (mutation testing, or property tests over stated invariants, run in the pipeline). | Find the last change the mutation or property gate refused: it failed on its own because the suite missed an introduced fault, not because a reviewer thought the tests looked thin. |
| 5 Durable | Protection holds as the system grows, and somebody still states what must be true (new modules arrive inside the same thresholds; generated tests are held to them like any other). | Fault-detection score over a year, and what happened when a generated suite arrived. Same or better is durable; quietly excluded is the practice ending. |

**Score 4 when:** mutation or property testing gates the suite, so a behavioural change actually fails something. Coverage stays as a diagnostic for untested code only.
**Evidence to collect:**
- Look for mutation tooling config (Stryker `stryker.conf.*`, `mutmut`, PIT `pom.xml` plugin, `cargo-mutants`, `mutatest`) and property-test libraries in dependency files (Hypothesis, fast-check, jqwik, proptest, QuickCheck). None present = at most level 3.
- Check whether that tooling is wired into CI as a failing gate (a minimum mutation score or a required job) rather than an optional or `continue-on-error` report. Present but non-blocking = level 3.
- The guide's own probe (only if the owner allows running tests; it is not read-only): in a temporary worktree, flip a comparison or shift a boundary by one in a covered function, run the suite, then discard the worktree. Per the essay (2026-06-02), pick a function recently modified by an AI assistant, not a convenient old one. Green = level 3 or below for that area. Without permission, mark it `NEEDS OWNER` and score from config and assertions.
- Read the assertions of 2-3 recently added test files (`git log --diff-filter=A --name-only -- '*test*'`). Expected values copied from the function's output, or snapshot-style asserts with no stated rule, indicate mirror tests (level 2).
- Look at the coverage gate in config (`--cov-fail-under`, `coverageThreshold`, `jacoco` rules). A bare percentage gate with no fault-detection check = level 3 at best.
- Check for specs, acceptance criteria or invariants the tests cite; where "correct" is written down, tests can anchor to it.
**Small-team note:** the level 2 tell compares authors. In a one- or two-person codebase compare older hand-written tests with recent AI-generated ones, or test files written before versus after the code. Do not score the human-vs-human split as absent; score the oracle quality you can see.
**Cheapest moves up:**
- 3 to 4: run mutation testing on the one highest-value module and gate that module only, then widen.
- Add property tests for stated invariants (for example, price never above base after discount) where a spec exists. Per the guide (2026), each property-based test finds roughly 50 times as many faults as the average unit test, and both it and mutation testing force a human to define "correct" before the test exists. The essay (2026-06-02) also names approval testing, where a person signs off the expected output, as a practitioner response. Our reading: a snapshot nobody reviewed is still a mirror.
- Keep coverage only as a diagnostic for code with no tests at all.
- Have a human write the expected behaviour before the implementation or its tests are generated.

## 7 · Change Absorption
Read: field guide pp. 35-37; https://jurgendesmet.substack.com/p/ai-readiness-measuring-change-absorption; https://howreadyfor.ai/d/change-absorption
**Question:** Of everything merged anywhere in your scope last month, how much was reverted or rewritten within two weeks, and is that share rising?
**Why agents care:** AI raises how much change arrives and leaves the capacity to absorb it (pipeline plus human reviewers, maintainers, support, sales) unchanged. Agent-sized batches push reviewers past the size where review still works, so code clears CI but never clears a human mind; the first visible symptom is rework. An agent has no sense of this unless the revert and churn rate is measured and can stop it.
**Signals you are low:**
- Churn relative to module size is climbing and nobody watches it.
- Median pull request size is past about 400 lines (per the guide (2026), review effectiveness drops below 70% past 400 lines and below 50% past 1,000).
- Review time rises nearly one-to-one with PR volume, so reviews become rubber stamps.
- Feature-branch activity grows while main-branch throughput is flat or falling.
- People outside engineering learn of changes through breakage rather than communication (support tickets about behaviour nobody briefed them on; a customer describing a feature that changed since the demo).
- A low change failure rate sits next to rising rework. Per the essay (2026-07-07, citing DX and DORA), read change failure rate together with rework rate (deployments made to fix something that just shipped); a low failure rate can hide high rework.
- Maintainers take longer and longer to make a first meaningful fix in code they did not write (no dashboard tracks this; ask).
Calibration for churn (a line authored, pushed, then reverted or substantially revised within two weeks; GitClear, 211 million lines): per the guide (2026), 3.05% in 2020, 3.27% in 2021 (pre-AI baseline), 4.50% in 2023, 5.67% in 2024. The essay (2026-07-07) adds GitClear's 2025 projection of 6.87% and that refactoring (moved code) fell from 24.8% to 9.5% of changed lines over 2021-2024. These are reference points; your own file-level proxy will not match the definition, so compare your trend, not the absolute figure. The essay's opening asks about a week; the live question and the guide say two weeks, which this file follows.
Where the cliff shows: per the guide (2026), among median teams feature-branch activity rose 15% while main-branch throughput fell 7%, whereas the top 5% saw +85% and +26% in step. Batch growth is the mechanism (PR size +154%, review time +91%, merge rate per developer +98%). Failures also shift in kind: surface errors fall while structural problems rise, so a falling bug count does not prove absorption.

| Level | What it means here | Tell (what settles it) |
|---|---|---|
| 1 Blind | Nothing measures what comes back. Rework disappears into the next estimate. | Search last month's merge history for reverts and for files rewritten within two weeks of landing. If getting the count is a project rather than a query, nothing is watching. |
| 2 Tacit | Individual teams feel the rework. Nobody adds it up. | Ask two teams if rework is up. Both say yes with conviction, neither has a figure. |
| 3 Visible but inert | Churn and revert rates sit on a dashboard. No decision waits for them. | Find the number, then the last decision that changed because of it. If rising churn never slowed a rollout or reopened a plan, it is reporting. |
| 4 Acted on | Rising churn gates a decision on its own, rather than after somebody argues for it (a rollout stops, batch size tightens or a review triggers). | Last time churn or revert rate crossed its threshold, something stopped or slowed because of the number, not because a person noticed and argued. |
| 5 Durable | The rate holds as volume grows, because absorption gets funded before it breaks (batch size, review load and change reaching people outside engineering are watched together). | Churn against merge volume over a year: volume rose, rate stayed flat, and you can name what was funded to keep it there. |

**Score 4 when:** revert and churn rate is tracked on a cadence and the number gates a decision. Relative churn (against module size) is the leading indicator, not absolute churn.
**Evidence to collect:**
- Revert count: `git log --since="30 days ago" --no-merges -i --grep='^revert' --format=%h` against total non-merge commits (`git rev-list --count --no-merges --since="30 days ago" HEAD`). This is a floor, since squash-merges and manual undo hide reverts. If the repo squash-merges, also grep PR titles for "revert".
- Two-week rewrite proxy: list files touched by commits in the last 30 days, then for each file count commits touching it in a following 14-day window (`git log --since=... --format= --name-only | sort | uniq -c | sort -rn | head -20`). Hot files touched many times in short windows are the churn candidates; compare against file size for relative churn. If this takes a custom script rather than a query, that is level 1 evidence.
- PR size: median changed lines of recently merged PRs (`git log --shortstat --merges` or squash commits via `git log --shortstat --since=...`, or the platform API). Past 400 lines is a flag.
- Search the repo for a dashboard, scheduled job or CI step that reports churn/revert rate (`grep -ri "churn\|revert rate\|change failure" .github ci docs scripts`), then check for a threshold or a required check that acts on it. A report with no threshold = level 3; a threshold wired to a gate or release hold = level 4.
- Look in release or rollout docs for a rule that names a rework number as a stop condition.
**Small-team note:** the tells ask what teams say and what decisions changed. For a one- or two-person codebase, the git history is the whole measurement: score the revert and rewrite count from git. A written threshold you choose to stop on is still 3 (a person chooses); 4 needs something that stops on its own, such as a check that blocks agent-generated changes while the rework share is past the threshold. Absence of a second team is not an excuse for level 1 if you can run the query.
**Cheapest moves up:**
- 1 to 3: compute reverts plus two-week rewrites per month from git and plot it.
- 3 to 4: attach a threshold to the number and a named consequence (hold the rollout, cap PR size, reopen the plan).
- Cap batch size for generated changes so review stays under the effectiveness cliff.
- Brief support, sales and documentation owners on what shipped, and track how often people outside engineering find out through breakage (per the essay, absorption fails at the organisational boundary too).

## 8 · Technical Debt
Read: field guide pp. 38-41; https://jurgendesmet.substack.com/p/ai-readiness-technical-debt; https://howreadyfor.ai/d/technical-debt
**Question:** Somewhere in your scope is a system everybody agrees needs fixing. Does your AI plan carry a line item for fixing it, or an assumption that the acceleration will pay for it later?
**Why agents care:** Generated code lands in the same tangles and reproduces whatever inconsistent patterns it finds (three patterns for one operation get copied three times). It cannot infer context, undocumented business trade-offs, or principles never written down, and it tends to avoid the refactors that keep code clean. Unpriced debt turns into "unexpected complexity" that eats the plan, and developers feel faster while measured delivery slips (per the guide (2026), the METR study found experienced developers 19% slower while believing themselves 20% faster; per the essay (2026-04-07) that was 16 developers in mature repositories averaging ten years and over a million lines, so the finding is about experienced people in code they know). Debt also compounds rather than accumulates: each unrefactored component adds a dependency that makes the next restructuring harder.
**Signals you are low:**
- "AI will clean it up" is an actual sentence in planning conversations.
- The AI business case has no explicit, money-denominated remediation budget.
- Stabilisation work keeps appearing as "unexpected complexity" instead of planned paydown.
- No shared definition of technical debt and no consistent way to measure it.
- Developers report feeling faster, but delivery dates keep slipping.
- Near-duplicate helpers pile up (the essay's example: three pricing calculators and two validation layers, none authoritative) while refactoring shrinks. Per the essay (2026-04-07), GitClear saw refactored lines fall from roughly 25% to under 10% of changes (2020 to 2024), and Ox Security found refactor avoidance in 80-90% of AI-generated code across 300+ repositories.
Sizing reference, per the guide (2026) citing IBM: 86% of executives say debt constrains AI success; remediation can take up to 29% of AI implementation budgets; skipping foundational work brings 15-22% longer timelines; enterprises that account for debt in the business case project 29% higher ROI. Treat these as order-of-magnitude checks on a remediation line, not targets. A "classic catch-22" applies: the same tools create debt and are sold as its cure. AI-assisted migration has halved an application's debt (CGI case, per the essay) only with clear architectural intent and humans making every keep-or-kill decision; "AI can help with debt" is a tool choice, "AI will clean it up" is an excuse.

| Level | What it means here | Tell (what settles it) |
|---|---|---|
| 1 Blind | Nobody has counted it. Debt is a word used in estimates, not a quantity. | Ask what debt costs in a year. A story about a system rather than a quantity, and no two people tell the same one. |
| 2 Tacit | Some teams keep their own list. It stops at the team boundary. | Ask two teams for their debt list. Both have one, nobody above has seen either. |
| 3 Visible but inert | The debt is quantified and reported (a register, quality-gate score or remediation backlog). No decision waits on the number. | Find where the figure is reported, then a decision that changed because of it. If it never moved a date, budget or scope, it is reporting, not governance. |
| 4 Acted on | The debt carries a money figure, and that figure gates the AI business case. | The last acceleration or AI program approved carries an explicit remediation line, and the approval refused to proceed without one, not because a reviewer happened to ask. |
| 5 Durable | The figure is maintained and remediation is funded continuously, not campaigned for (new debt is taken deliberately and carries a date). | Debt figure over two years and who owns it: recomputed on a cadence, remediation funded in a year with no transformation program running. |

**Score 4 when:** debt is quantified financially and the number gates the AI business case; it is not buried in story points. Per the guide (2026), the claim is that accounting for debt openly produces realistic budgets and timelines.
**Evidence to collect:**
- Search docs for a debt register or ADRs (`grep -ril "tech.*debt\|debt register\|remediation" docs/ README* ADR* adr/`), and check authorship and last-modified dates with `git log -1 --format='%an %cd' -- <file>`. Scattered per-team lists with no shared owner = level 2.
- Look for a monetary or effort-in-money figure for debt anywhere in plans, roadmaps or business-case docs available in the repo or provided by the user. Story points or a TODO count alone is not a money figure.
- Check whether the debt figure is wired to a gate: a business-case template, approval checklist or planning doc that requires a remediation line. No such requirement = at most level 3.
- Measure the in-repo symptoms as support, not as the score: duplication tooling output (jscpd or similar), age and count of `TODO|FIXME|HACK` (`git grep -c`), long-lived workaround files, modules with high churn and low test coverage. These show debt exists; they do not move the level past what the money and gating evidence shows.
- Check the git log for refactor-only commits in recent months (`git log --since="90 days ago" -i --grep='refactor\|cleanup\|debt' --oneline | wc -l`). A thin or falling count while feature volume rises indicates refactoring is in retreat.
- Where tracker or planning data is available, compare planned and delivered dates for AI-assisted work and count "stabilisation" or "unexpected complexity" items: slipping dates beside reports of feeling faster is the METR pattern. Do not accept "developers feel faster" as evidence.
- Look for dated, deliberate debt entries (an owner, a date, a reason) as evidence of level 5 practice; undated entries do not count.
- This dimension is largely organisational: if the repo cannot answer, record "needs a conversation with whoever owns the plan" and score 1 until someone produces the figure.
**Small-team note:** "teams" and "the organisation" may not exist. Score on whether the debt is written down, priced in time or money, and whether the plan for AI use names it. A solo owner who keeps a dated, priced debt list and chooses to defer new work until a named item is paid is level 3, because a person chooses; it is 4 only when a plan template or check refuses the work without the remediation line. Do not require a board.
**Cheapest moves up:**
- 1 to 2/3: collect one shared list, and attach a cost (money, or engineer-weeks times a rate) to the top few items.
- 3 to 4: make an explicit remediation line mandatory in the AI business case or plan template, and let its absence block approval.
- Stop the bleeding before accelerating on the worst system: per the guide (2026), going slower first is the fastest path to sustainable returns (the essay's example pauses net-new features for one cycle to stabilise CI and remove coupling).
- Direct AI at work humans avoid (migration, duplicate removal, test scaffolding) while a human defines the invariants first (for example one promotion calculator, one eligibility source of truth, explicit boundaries).

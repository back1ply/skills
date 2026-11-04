# Foundation & Structure: the four dimensions

Source: "AI Readiness for Engineering Organizations" (Jurgen De Smet, 2026), pp. 10-26, and the
online assessment (howreadyfor.ai/assess). Level wording follows the online version.

Part premise: AI reasons only from what it can read, takes everything literally and has no memory of
past decisions. If structure hides intent, splits meaning across names or needs five files to explain
one, every later safeguard inherits that confusion. Score the worst case in scope, not the typical one.
"Nobody can produce it" is a 1. Levels 1-3 need a human to choose; 4-5 the system acts.

## Contents
- 1 · Repository structure
- 2 · Cognitive load per module
- 3 · Domain language consistency
- 4 · Semantic drift

## 1 · Repository structure
Read: field guide pp. 12-15; essay https://jurgendesmet.substack.com/p/ai-readiness-repository-structure (2026-03-31); https://howreadyfor.ai/d/repository-structure
**Question:** Across everything in your scope, does your repository setup help an agent reason about the system, or force it to guess?
**Why agents care:** The repo layout sets the agent's field of view. It only reasons reliably about boundaries it can reach in one workspace; across unstitched repos it makes confident claims about code it never saw (missing interface, stale README, version mismatch each manufacture a hallucination). Mono vs multi is not the verdict: the unmanaged version of either is the problem. Mono needs scoped builds and enforced boundaries; multi needs versioned contracts and retrieval. Per the /d/ page: half of repository-level tasks need code from other files, and performance roughly doubles when that cross-file context is available (RepoCod); a large share of real-repo hallucinations are project-context errors, such as calling functions that do not exist here or inventing dependencies across a boundary it could not see (Zhang et al.). Per the essay (2026-03-31): a multi-repo change can pass locally while silently breaking a sibling repo, so integration feedback arrives late.
**Signals you are low:**
- Every commit rebuilds and retests everything; no scoped or affected-graph logic.
- Module boundaries are social agreements that break under deadline pressure.
- Multi-repo with no retrieval layer across repos, and cross-repo contracts that are tribal, not versioned.
- A cross-service rename (e.g. `userId` to `accountId`) is a release-coordination ceremony, not one change.
- The AI reports "everything is aligned" and production regularly disagrees.

| Level | What it means here | Tell (what settles it) |
|---|---|---|
| 1 Blind | No agreed model; nobody can list what is in scope or who owns it | List the repos in scope and count how many have a named current owner. A real share with nobody, or someone who left, is a 1 |
| 2 Tacit | The model lives in the heads of the longest-serving people | Ask two engineers who joined this year where a new service goes and what it may call. Two confident, different answers |
| 3 Visible but inert | Written down and diagrammed (diagram, schema files, ownership file); nothing fails when it is crossed, and an agent that never opens the wiki behaves as if none of it existed | Find the last crossing of a boundary your own docs forbid. If a reviewer noticed it rather than the build, you are here |
| 4 Acted on | The build fails on a boundary crossing, with no reviewer involved; across repos, a consumer that breaks a versioned contract goes red before it ships | Find the last accidental crossing in history; the build caught it and went red before a person read the change |
| 5 Durable | New modules inherit the rules; exceptions carry a date and expire; a rule that fires on fine things is tuned, not switched off | Open the exception/allowlist file and read the dates. Expiring entries on a list shorter than last year is durable; a list that only grows is enforcement rotting |

**Score 4 when:** whichever model runs, structure is enforced by machine, not convention: scoped builds and enforced module boundaries in a monorepo, versioned and enforced contracts across a multi-repo, so AI cannot drift across a boundary unnoticed.
**Evidence to collect:**
- Count repos in scope and map each to an owner: CODEOWNERS, a catalog file, or repo admins/README. Many with none or departed owners points to 1.
- Open the CI config: is there path filtering, an affected-graph or build-cache tool (nx, bazel, turborepo, pants, or paths-filter rules)? Whole-repo builds on every commit caps a monorepo at 3.
- Look for boundary-enforcement config: import-linter, dependency-cruiser, ArchUnit, eslint boundaries, Bazel visibility, Go `internal/`. Present and run in CI points to 4; documented only points to 3.
- Multi-repo: check cross-repo contracts are versioned artifacts (OpenAPI/proto/schema package with semver, consumer contract tests) and whether any retrieval/index spans repos. Neither means 2-3.
- Search for an exception list (allowlist, baseline, ignore file) and run `git log --format=%ad -p -- <file>` to see if entries are dated, expire, and shrink over time (5) or only grow (4 at best).
- `git log --diff-filter=A --name-only` for new top-level modules: do they get boundary rules by default (template, generator, glob) or by hand?
- Per the essay (2026-03-31), also check: architecture docs, ADRs and agent instructions (CLAUDE.md/AGENTS.md) live next to the code and change in the same PR (else AI summaries diverge from reality); and whether dependency versions and lint/policy config are single-sourced (mono) or reinvented and several minor versions apart per repo (multi).
- Do not mark down multi-repo as such. The guide and essay name legitimate cases (regulated data isolation, acquired incompatible stacks, least-privilege access) where the coordination tax is deliberate; score on enforcement, not on repo count.
**Small-team note:** A single deliberately chosen repo with one owner can still reach 3-4: owner is you, and the check is whether a lint/build rule (not memory) stops a layer violation. Do not invent a "second reviewer"; judge the tell by what the build does when you cross a line yourself.
**Cheapest moves up:**
- 2 to 3: write the topology and the allowed-call rules down once (one diagram or ADR page per repo/area, with owners).
- 3 to 4: turn the one rule that keeps being broken into a failing CI check (import/boundary lint or scoped-build gate).
- 4 to 5: put every exception in a dated allowlist that fails the build once the date passes.

## 2 · Cognitive load per module
Read: field guide pp. 16-19; essay https://jurgendesmet.substack.com/p/ai-readiness-cognitive-load-per-module (2026-06-16); https://howreadyfor.ai/d/cognitive-load-per-module
**Question:** Does anything in your scope know how tangled its worst module is, or only your people?
**Why agents care:** The module boundary is the context boundary. A well-bounded module gives the agent a small, self-contained prompt; an entangled one forces it to ingest every dependency, and quality drops as context grows (per the guide (2026): one model fell from 29% to 3% accuracy from 32K to 256K tokens; cross-file dependency info lifted pass rate from 20.3% to 41.1%). Humans offset tangles with remembered familiarity; the agent has none, so entropy hits it first. Under AI, complexity ratchets up and velocity falls (per the guide (2026): +41.6% cognitive complexity after adoption, and a doubling of complexity linked to -64.5% velocity; 806 adopting repos vs 1,380 controls, with the +281% lines-added burst in month one back to baseline by month three while the complexity stayed). Per the essay (2026-06-16): more context hurts even with perfect retrieval (13.9% to 85% degradation from input length alone), so "we have RAG" does not lift this score; look-alike code from coupled modules degrades output by up to 15%; about a quarter of hallucinations were project-context conflicts and the best retrieval mitigation added only 3%; well-modularized systems show 6-8x lower change-propagation cost.
**Signals you are low:**
- Understanding or changing one module means opening about five others.
- AI output compiles and passes tests but quietly leans on deprecated or wrong cross-module behavior.
- Cognitive complexity in the busiest modules is rising and nobody tracks the number.
- Module APIs leak internals; "shared types" drag half the system into each change.
- Only people who memorized the hidden dependencies move fast there.

| Level | What it means here | Tell (what settles it) |
|---|---|---|
| 1 Blind | No measurement; the only signal is which modules people avoid | Ask for a coupling or complexity number for any module in scope, not the worst one. If nobody can produce one for any of them, the worst module is unidentified, not just unmeasured |
| 2 Tacit | A few people hold the map and compensate with familiarity | Who gets a change in the worst module? If it is two long-tenured people and nothing in the module says why, it is tacit |
| 3 Visible but inert | The number is computed and shown; the pipeline ignores it | Take the worst-scoring module and read its last ten changes. If no review mentions the score and none was sent back for it, it is decoration |
| 4 Acted on | A threshold flags or fails the build on its own, before review; the budget is argued about in the open | Find the last change that crossed the threshold: something automatic refused it because of the number, not a reviewer's mood |
| 5 Durable | Budget holds as the system grows; new modules arrive inside it; thresholds tighten rather than slip; bringing a module back under budget is planned, owned work | Look at threshold history over a year. Tightened, or held with dated exceptions, is 5; raised each time it blocked a release is not |

**Score 4 when:** coupling and complexity carry a tracked budget that fails or flags the build, not just a code-review habit.
**Evidence to collect:**
- Find complexity/coupling tooling in config: sonar quality gate, radon/xenon, eslint `complexity`/`max-lines`, ruff `C901`, CodeScene or similar, dependency-cruiser. None anywhere is 1-2.
- Check whether the tool runs in CI and whether it can fail the job (exit code/gate on) or only reports. Report-only or dashboard-only is 3; failing or flagging is 4.
- `git log -p -- <threshold config>` over 12 months: counts of thresholds raised vs lowered, and dated exceptions. Raised-on-block is the anti-5 pattern.
- Run the tool on the largest/most-changed files (`git log --since=1.year --name-only | sort | uniq -c | sort -rn | head`) and check whether those files are the worst scorers and whether anyone knows.
- For one chosen module, count imports and cross-module references: the guide's test is whether ~5 other modules are needed to understand 1.
- Prefer cognitive complexity as the metric: per the essay (2026-06-16) it correlates at r = 0.654 with measured human comprehension time and is the metric the adoption study used. Look for look-alike types or logic in neighbouring modules (payment and order modules that implement discounts slightly differently); that is what misleads an agent.
**Small-team note:** Two people can both hold the map, so the "two people" tell fires by default; score 2 only if the structure itself is opaque to a fresh reader. A pre-commit or CI complexity gate you run solo is a legitimate 4.
**Cheapest moves up:**
- 1 to 3: compute a complexity/coupling number per module and show it; name the worst module.
- 3 to 4: make the worst module's score non-regressing in CI (fail or flag when a change raises it past the current value).
- 4 to 5: ratchet the threshold down on a schedule and require dated exceptions instead of raising the limit.

## 3 · Domain language consistency
Read: field guide pp. 20-22; essay https://jurgendesmet.substack.com/p/ai-readiness-domain-language-consistency (2026-04-21); https://howreadyfor.ai/d/domain-language-consistency
**Question:** If you asked three teams anywhere in your scope to define your most contested domain word, would you get the same answer?
**Why agents care:** An agent learns your vocabulary from the code alone. When one concept wears four names (customer/client/user/account) all four look equally right, so it picks one and the other teams reject it, or it averages them into a fifth. It also ignores bounded-context lines, cloning a name that fit billing into the order service where it misleads. The guide ties misleading API names to more bugs (per the guide (2026): +29% bug likelihood) and AI code to roughly twice the naming inconsistencies of human code (per the guide (2026): 470 PRs, 320 AI-co-authored vs 150 human, with readability issues above 3x). Per the essay (2026-04-21): misleading names also slow bug localization and lower the chance of finding the bug, and the effort spreads past the bad identifier to the whole snippet (Fakhoury et al.); among developers who blame AI for lower quality, 44% cite missing context (Qodo 2025). Bounded contexts only help an agent if the boundary is explicit in the code.
**Signals you are low:**
- Three teams give three names for the core entity and all three are in production.
- AI-generated PRs spark review threads about vocabulary instead of logic.
- A method name that fits one service keeps being cloned into another, where it misleads.
- Services share terms but nothing marks where a term changes meaning (no explicit contexts).
- A glossary exists, if at all, as a document, not in lint or review gates.

| Level | What it means here | Tell (what settles it) |
|---|---|---|
| 1 Blind | No shared vocabulary and nobody owns one | Ask three people in different teams to define the central domain word in one sentence, without talking to each other, and collect the answers before anyone compares. Different answers, all confident |
| 2 Tacit | The vocabulary lives with the people who modelled the domain | Search the code for the two rival names of one concept and count each. If both are still growing, a person and their calendar is the correction mechanism |
| 3 Visible but inert | An accurate glossary that nothing reads or enforces | Note the glossary's last edit date, then find a name added since that contradicts it. Nothing stopped it landing |
| 4 Acted on | A rival term for an existing concept fails a check before merge; new public names are checked against the glossary | Find the last time a rival term reached a public name: it did not merge; the check fired and named the expected term |
| 5 Durable | The vocabulary keeps up with the business, in code and in the rule; retired terms leave the code, not only the glossary | Take the latest business rename and check glossary, rule and code. If one of the three did not move, enforcement is drifting from the domain |

**Score 4 when:** the glossary is enforced in naming, lint and review gates, not parked on a wiki page.
**Evidence to collect:**
- Locate the glossary (GLOSSARY.md, docs/domain, a wiki export, a terms YAML) and `git log -1 --format=%ad -- <file>` for its last edit; none found is 1-2.
- Pick the most contested concept and `git grep -ciw` each rival name (customer, client, user, account) by directory; note which counts are rising via `git log -S"<name>" --since=1.year --oneline | wc -l`.
- Search lint/CI config for banned-name or synonym rules: eslint `id-denylist`, custom regex lint, `semgrep` patterns, vale, a pre-commit grep, schema-name checks. Rule present and in CI is 4; glossary only is 3.
- Check for explicit bounded-context markers (per-context folders or packages, context map doc, translation layers) where a term changes meaning.
- Compare the glossary's term list to current public API/schema names to find contradictions added after its last edit.
- Per the essay (2026-04-21) and /d/ page: check the glossary is expressed in the code itself (naming conventions, module boundaries, review standards), that new terms enter by a route people use, and that after the last business rename the rule moved within about a week (a retired word still flagged, or still present in code, means 5 is not met).
**Small-team note:** The "three teams" tell becomes: would you and the code (and any docs) give one definition? Score 1-2 if your own code uses rival names for one concept; the lint-gate tell at 4 still applies unchanged.
**Cheapest moves up:**
- 1 to 2/3: pick the single most contested word, define it in one sentence, and record it (glossary entry or `GLOSSARY.md`) with an owner.
- 3 to 4: turn the top two or three banned synonyms into a lint or CI grep rule that names the preferred term in its message.
- 4 to 5: make glossary, rule and code change together (a rename updates all three in one PR).

## 4 · Semantic drift
Read: field guide pp. 23-26; essay https://jurgendesmet.substack.com/p/ai-readiness-semantic-drift-in-codebases (2026-06-30); https://howreadyfor.ai/d/semantic-drift
**Question:** Does the same concept have one name across your scope or several, and do you know whether it is worse than a year ago?
**Why agents care:** This dimension is the trend, not the snapshot. Names decay under change (Lehman's Second Law) and refactoring was the brake; AI generates fast, rarely consolidates, and learns from context already carrying drift, so each suggestion reads a more fragmented vocabulary than the last. Per the guide (2026): moved code fell from 24.8% to 9.5% of changed lines (2021-2024) while copy-paste rose from 8.4% to 12.3%; only about 1 in 10 notified naming inconsistencies were fixed. In 2024 copy-pasted code exceeded moved code for the first time on record. Per-change drift is invisible, so it must be watched as a trend. Per the essay (2026-06-30): names drift in three ways (Wang et al.): narrowing 52.7% (`process()` becomes `processPayment()` in one module and stays `process()` in three others), change 24.9% (the name now lies) and generalization 22.4% (the name loses precision); the ratio is 1 inconsistent method name per 531 consistent ones, too rare for any reviewer to reject a PR over. Naming-inconsistency detectors reach only 55-60% accuracy on realistic data, so a detector alone is weak evidence of tracking. Drift is directional: feature scattering in JFreeChart rose monotonically (73 to 87 classes over 14 versions) and does not reverse unless someone consolidates.
**Signals you are low:**
- A correct rename once broke something downstream and the team quietly stopped renaming.
- The key concept has more name variants this year than last (`git log` per variant shows the slope).
- Copy-pasted code is outpacing moved or consolidated code in change history.
- Refactoring is the first thing cut when a sprint tightens.
- Fixes everyone agrees are correct never happen because fixing always costs more than it seems to gain.

| Level | What it means here | Tell (what settles it) |
|---|---|---|
| 1 Blind | Nobody is watching; no way to say whether it is worse | Ask who would notice a second name for an existing concept entering the code this month. Nobody, or whoever reviews it, is a 1 |
| 2 Tacit | Repair happens when someone finds time; unbudgeted, invisible | Scan last quarter's delivered work for consolidation or renaming. None planned (only carried inside feature tickets) means 2 |
| 3 Visible but inert | The trend is measured and shown; no budget follows it | Find the duplication trend for the scope, then name the last three decisions it changed. None means the number is a report |
| 4 Acted on | Crossing a threshold puts consolidation into the plan as delivery, not a favour asked for | Point at the current plan: it contains consolidation work and you can name the number that put it there |
| 5 Durable | The budget survives a bad quarter; the measurement is maintained when tooling changes; retired names stay retired | Take a consolidation from a year ago and check the retired name is still absent. Names creeping back means it was repaired once, not held |

**Score 4 when:** naming and duplication drift is measured over time and refactoring time is budgeted against it.
**Evidence to collect:**
- Run a duplicate detector (jscpd or similar) at two points a year apart (check out an old commit in a temporary worktree) and compare. Only one data point, or none, means 1-2; a stored trend means 3+.
- For the key concept, `git log -S"<variant>" --since=1.year --oneline | wc -l` per variant: new variants appearing or counts rising versus last year shows drift direction.
- Estimate moved vs added code: `git log --since=1.year --numstat` and rename detection (`git log -M --diff-filter=R --name-status | wc -l` per quarter); falling renames with rising adds echoes the guide's pattern.
- Look in the backlog/plan/roadmap for items labelled refactor, consolidate or rename and check whether they link to a metric or threshold (4) or only appear as goodwill (2-3).
- Compare intended vocabulary (an agreed term list) to the actual terms in code; no intended vocabulary to compare against is 1-2. Where available, look at the share of moved vs added vs copy-pasted lines and commits carrying several duplicated blocks.
- Grep for a retired-name list or deprecation file and test whether any retired name reappears in code added since (`git grep` limited to recent commits): reappearance caps at 4.
**Small-team note:** "Plan" can be your own task list and "bad quarter" your busiest sprint. Score 4 only if a metric, not mood, put consolidation on the list; do not credit ad hoc cleanups.
**Cheapest moves up:**
- 1 to 3: compute duplication and rival-name counts once now and again each quarter, and store them.
- 3 to 4: set one threshold (e.g. rival-name count or duplication percent) and agree that crossing it adds a consolidation item to the next plan.
- 4 to 5: ring-fence the consolidation budget and add the retired names to a check so they fail if reintroduced.
- Per the essay (2026-06-30), teams that get value budget recurring counter-entropy work (vocabulary reviews, naming alignment, concept consolidation) and treat a rename that broke something downstream as a missing dependency map, not a reason to stop renaming.

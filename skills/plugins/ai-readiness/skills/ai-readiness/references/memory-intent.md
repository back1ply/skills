# Memory & Intent: the four dimensions

Source: "AI Readiness for Engineering Organizations" (Jurgen De Smet, 2026), pp. 59-75, and the
online assessment (howreadyfor.ai/assess). Level wording follows the online version.

Part question: does the system remember why, and know what it was asked? An agent works from the
code as it stands now; it does not know why a boundary exists, what a feature was for, or which
quiet assumption holds things up. It fills gaps with confident invention. Ladder: 1 Blind, 2 Tacit,
3 Visible but inert, 4 Acted on, 5 Durable. Levels 1-3 need a human to choose; 4-5 the system acts.
Score the worst case in scope, not the typical one. Not knowing is a 1.

## Contents
- 13 · Decision Memory (ADRs)
- 14 · Requirements Quality
- 15 · Security Assumptions
- 16 · Documentation Integrity

## 13 · Decision Memory (ADRs)
Read: field guide pp. 61-64; essay https://jurgendesmet.substack.com/p/ai-readiness-adr-discipline-and-decision ; page https://howreadyfor.ai/d/decision-memory
**Question:** Pick an architectural decision taken anywhere in your scope in the last two years. Can somebody find the reasoning in the repository, or only in the person who made it?
**Why agents care:** The code shows the shape of a boundary, not why it was drawn or what it cost. An agent takes the cheapest route, straight across the boundary, and a reviewer who sees only the patterns in the repo approves. Refactoring used to carry intent informally; per the guide (2026) it has fallen while copy-paste has risen, so intent no longer travels on its own. Per the essay (2026-05-19), citing GitClear: moved code fell from 24.1% to 9.5% of changes (2020-2024) while copy-paste rose from 8.3% to 12.3% (the field guide gives 24.8% and 8.4% for 2021-2024; the author's two figures differ). Per the guide, Ox Security found "avoidance of refactors" in 80-90% and "return of monoliths" in 40-50% of AI-generated code across 300+ repos. The guide calls the gap "intent debt" (Storey): an absence of artifacts, not a mess.
**Signals you are low:**
- The rationale for a major boundary lives in a whiteboard photo, a former employee's memory, or nowhere.
- The codebase teaches several ways to structure a boundary and the oldest is the most common.
- A reviewer questioning an AI change has no written decision to point at, only "this isn't how we do it".
- Decisions are recorded, if at all, in a wiki far from the code that the team has forgotten exists ("decision archaeology": pages nobody visits, chat threads lost in the scroll).

| Level | What it means here | Tell (what settles it) |
|---|---|---|
| 1 Blind | No record of why. The reasoning left when the meeting ended. | Search the repos for anything written about a boundary you know was argued over. Nothing found and the only source is a person who must be tracked down. |
| 2 Tacit | A few people carry the reasoning and get asked in review. | Ask two long-standing engineers why a major boundary exists. They agree in detail and neither can point to where it is written. |
| 3 Visible but inert | Decisions are written down (a log, records in the repo, a dated wiki); nothing checks the code still follows them. | Take a two-year-old record and check the code still obeys it. It does not, and nothing noticed: the record is history, not a constraint. |
| 4 Acted on | The decision lives in the repository beside the code, and a review or check can point at it. Reversing one is a deliberate, dated act. | Find the last change that went against a recorded decision. Something pointed at the record before merge; outcome was a refusal or a new record superseding the old. |
| 5 Durable | Decisions stay current as the system moves; stale ones are superseded, new ones arrive with the change that implements them, and the set is small enough that people read it instead of asking. | Look at record dates. Recent ones present and old ones carrying supersessions, not silence, means a living practice rather than a folder someone made once. |

**Score 4 when:** Decisions are version-controlled records (ADRs: title, status, context, decision, consequences) that a reviewer can point to, not whiteboard photos. The record states the trade-off and rejected alternatives, not just the fact ("we use separate services" is a fact; "separated because coupling froze deploys for 3 days, accepted latency, rejected a shared library" is memory). A wiki or chat log far from the code caps at 3: it is neither beside the code nor reachable by a check. The essay's three layers help place a repo: pattern (one dominant way to cross a boundary), decision (the record), constraint (a machine-enforceable rule; you cannot write the rule before the boundary and its reason are agreed).
**Evidence to collect:**
- List decision-record directories: `git ls-files | grep -iE '(adr|decisions?)/|0[0-9]{3}-.*\.md'`. None, or only a wiki link, means 1-2.
- Check status and dates: `git log --format='%ad %s' --date=short -- <adr dir>`. One burst years ago and nothing since means 3, not 5.
- Count records with a status of superseded/deprecated, and records that name rejected alternatives and costs. Supersessions present leans 5.
- Pick one record naming a boundary and grep the code for imports or queries that cross it. Live violations with no CI rule or review link means 3.
- Search PR/commit text for references to record IDs (`git log --grep='ADR'`). References made at merge time mean 4.
- Check whether agent context files (CLAUDE.md, AGENTS.md) point to the records; a pointer is evidence the machine will meet them.
- Check whether new records land in the same PR as the change that implements them (records added months later or in bulk suggest archaeology, not practice).
- Count competing implementations of one boundary pattern; the oldest being the most common means an agent will copy the pattern the decision retired.
**Small-team note:** The "two long-standing engineers" tell does not apply to a one-person repo; use "the author, asked six months later". Records in the repo count fully; a solo maintainer needs no ceremony: a short dated file per decision is level 3 and a check that cites it is level 4.
**Cheapest moves up:**
- 1 to 3: write the five-field record for the one boundary people argue about most, in the repo beside the code; the guide says over 15 minutes is over-engineering.
- 3 to 4: make review or CI cite the record (a boundary check, a PR template line asking which record applies).
- 4 to 5: add a status field and require a superseding record when a decision changes.

## 14 · Requirements Quality
Read: field guide pp. 65-68; essay https://jurgendesmet.substack.com/p/ai-readiness-requirements-quality ; page https://howreadyfor.ai/d/requirements-quality
**Question:** Could an agent pick up the top item of any backlog in your scope and build the right thing without guessing?
**Why agents care:** Agents do not ask; they pick one reading and build fluently, then write tests confirming it, so nothing downstream contradicts the mistake. Per the guide (2026): in HumanEvalComm, models wrote code in over 63% of ambiguous cases without asking; in ClarEval, GPT-4o fell from 89.02% to 8.94% passing when the same task lost its goal, premise or precise terms; and in an OpenAI screening of 1,699 SWE-bench issues, 38.3% were too underspecified to use (68.3% removed with other defects). Modern agents do ask (per the guide, Claude Code asks more than twice as often as humans interrupt it on complex tasks), but after about three questions developers type "use your best judgement", so the brief must already carry the answers.
**Signals you are low:**
- A typical ticket is a few lines assuming the reader knows the domain and can ask.
- Acceptance criteria, when present, cannot become a test without inventing a definition of success.
- The same action ("cancel", "deactivate", "suspend") means different things across tickets.
- Features pass review, then generate support tickets about behavior nobody specified.

| Level | What it means here | Tell (what settles it) |
|---|---|---|
| 1 Blind | A title and a sentence. Done is not written anywhere. | Read only what is written in the top item. If you cannot say what must be true for it to be done, neither can the next picker. |
| 2 Tacit | Quality depends on who wrote the item, not on the process. | Read the top five items by three authors. If you can tell who wrote which from the level of detail alone, the standard is a person. |
| 3 Visible but inert | A good definition of ready exists (a template); items are pulled without meeting it. | Count how many of the last ten pulled items met your own definition of ready at pull time. |
| 4 Acted on | An item cannot be pulled into work until it is a testable spec. | Take the last five pulled items and find the readiness check on each. Every check ran before the pull, and you can point at an item sent back. |
| 5 Durable | A changed requirement reaches whoever is building against it, an agent that read the item this morning included. | Find an item whose requirement changed mid-build. Was the item updated before the code, or only after the demo went wrong? |

**Score 4 when:** Backlog items are written as testable specs (goal, preconditions and out of scope, acceptance criteria that convert to tests, domain terms as the codebase uses them, edge cases enumerated), by standard and checked before pickup. The guide's test: the opposite of vague is testable, not long. Judge precision per slice, not per product: a small slice a user can try is right, so do not demand a whole-feature spec. Format (INVEST, EARS, Gherkin) is a tool, not the test; what counts is whether the top item answers what an agent would otherwise have to ask.
**Evidence to collect:**
- Find a definition-of-ready or ticket template in the repo (`.github/ISSUE_TEMPLATE`, `.github/pull_request_template.md`, `docs/` templates). None means 1-2.
- Sample the last ten closed items or PRs via the tracker CLI or `git log`; score each against the five-question test (goal, preconditions/out of scope, testable acceptance, domain terms, edge cases). Report the pass count.
- Look for automation enforcing readiness (a workflow, bot, or required fields blocking a status change). Present and has sent items back means 4.
- Check whether acceptance criteria appear as test names or in tests (`git log --grep` on ticket IDs, then read the diff). Direct mapping supports 4+.
- Compare ticket vocabulary with the codebase's type and glossary names; mixed terms for one concept signal a gap.
- Read the top item cold, as an agent. Goal check, from the essay: "improve the cancellation flow" fails; "cancel so no further charges issue, last paid period honoured, prorated amounts refunded" passes because a test can be written from it alone. A six-line story usually leaves half a dozen edge cases implicit.
- For level 5, find a mid-build change in ticket history and compare the ticket edit time with the commit time. Also ask whether the standard held in the last crunch quarter; one that lapses when everyone is behind is not durable.
**Small-team note:** With one or two people the backlog may be a notes file or issue list; score the same way against the top items, and count "author is the only reader" as tacit, not as a pass. A checklist the agent is asked to fill in is still 3 (it can skip it); required fields or a check that blocks starting until the spec is complete is a fair level 4 in a small team.
**Cheapest moves up:**
- 1 to 3: adopt a five-line item template (goal, preconditions, out of scope, acceptance, edge cases).
- 3 to 4: make the check a gate before pickup (a bot, an agent-run lint of the ticket, or a required field) and send one item back to prove it works.
- 4 to 5: require the item to be edited first whenever scope changes mid-build.

## 15 · Security Assumptions
Read: field guide pp. 69-71; essay https://jurgendesmet.substack.com/p/ai-readiness-security-assumptions ; page https://howreadyfor.ai/d/security-assumptions
**Question:** Pick a security assumption your teams hold anywhere in this scope. Where in the codebase would an agent learn it?
**Why agents care:** An agent replicates patterns in context, not a threat model. With three validation or auth approaches (one secure, one legacy, one half-migrated) it treats all three as equal examples. Internal conventions sit outside what a model was trained on, so it cannot infer yours. Per the guide (2026): Pearce et al. found roughly 40% of 1,689 Copilot programs (89 scenarios) had top-25 weaknesses; Fu et al. found 29.5% of Python and 24.2% of JavaScript Copilot code in real projects had weaknesses across 43 categories; Perry et al. found assistant users wrote insecure code on 4 of 5 tasks while feeling more confident. Per the guide (Snyk 2024), over 75% of developers think AI code is more secure, nearly 80% bypass policy for it and only 10% scan most of it: distrust is a belief, verification an action. Security that lived in people's heads is invisible to any tool.
**Signals you are low:**
- Ask three engineers for a service's threat model and get three answers or three blank looks.
- Several validation or auth patterns coexist, and the insecure legacy one remains a usable example.
- AI-generated code is exempted from scans and policies that human code must pass.
- The reason behind a security choice exists only in the memory of someone who was in the room.

| Level | What it means here | Tell (what settles it) |
|---|---|---|
| 1 Blind | Assumptions are unstated. Nobody could list them. | Search for how a request gets authenticated and count the distinct patterns. More than one, with nothing saying which is correct. |
| 2 Tacit | Security-minded people hold the rules and catch things in review. | Look at who reviewed the last changes to auth or data-access code. The same one or two names, and nothing routes work to them automatically. |
| 3 Visible but inert | Assumptions are documented; nothing fails when code contradicts them. | Search for the pattern your policy forbids. Live examples exist and no build has ever failed over one. |
| 4 Acted on | One canonical pattern, and a scan that fails the build on a deviation. | Find the last change violating a critical assumption. The build failed and the failure named the rule, instead of a reviewer catching it on a good day. |
| 5 Durable | Rules keep pace with the threat model; old patterns are removed, not deprecated. | Search for the pattern deprecated two years ago. No live examples left to copy, and new repos start inside the same scans. |

**Score 4 when:** Critical assumptions are machine-enforced: one canonical pattern and scans that fail the build. Articulation comes first (you cannot write a rule until you agree which pattern is secure), and the rationale is written so a reviewer can say a change violates the threat model.
**Evidence to collect:**
- Grep auth and validation entry points and count distinct patterns (middleware names, decorators, validator libraries). Several with no stated winner means 1-3; one pattern is necessary for 4 but not enough without a failing scan.
- Open CI config for SAST, secret and dependency scans (`.github/workflows`, `Jenkinsfile`, `.gitlab-ci.yml`, semgrep/CodeQL/bandit config). Check they are required and not `continue-on-error` or allow-failure.
- Open the scanner rule set for custom rules naming your own banned functions or required patterns; custom rules point to 4.
- Grep for a forbidden pattern (string-built SQL, the old hash, the old auth helper). Live hits mean 3 or lower; none plus a failing rule means 4-5.
- Check CODEOWNERS for auth and data-access paths: automatic routing beats the same two names recurring in `git log -- <path>`.
- Look for exemptions (path ignores, bot or AI-authored branches skipping scans).
- Check for a written threat model, security ADRs, or comments at the boundary where an assumption applies, and whether agent context files carry the rules. Written rationale is what lets a reviewer say "this violates our threat model", even if the agent never reads it.
**Small-team note:** Skip "who reviewed" for solo repos; the tacit tell becomes "the assumption exists only in my head". Use the scan config as the divider: documented only is 3, a required failing scan is 4.
**Cheapest moves up:**
- 1 to 3: pick the one secure pattern per concern and write it down with the reason (an ADR, threat model note, or comment at the boundary).
- 3 to 4: delete the legacy examples where feasible, then add a ban or required-pattern rule that fails the build.
- 4 to 5: remove, not just deprecate, old patterns, and put new repos under the same scans by default.

## 16 · Documentation Integrity
Read: field guide pp. 72-75; essay https://jurgendesmet.substack.com/p/ai-readiness-documentation-integrity ; page https://howreadyfor.ai/d/documentation-integrity
**Question:** If a new developer or an agent followed the README of any repository in your scope from a clean machine, would they get a running system, and would you bet on it?
**Why agents care:** Docs used to be repaired by the reader asking a colleague. An agent cannot ask; it treats README, comments and context files as ground truth and builds on a stale map. Per the guide (2026, Ashik et al.; 270 API updates, 8 libraries, 11 models): executable output rose from 42.55% to 66.36% with structured docs, and a third still broke because stale model memory often beats fresh docs, so feeding agents more docs is not the fix. Per the guide (DORA 2024), per 25% more AI adoption perceived documentation quality rose 7.5% while delivery stability fell 7.2% (an association, and "perceived", as the essay (2026-08-04) stresses). Fluent generated prose hides staleness: polish reads as currency, so a well-governed wiki or a technical-writing team does not raise the score, only executed verification does. Per the guide, Faros telemetry shows 31.3% more PRs merged with no review, so the human gate that might catch drift is thinner.
**Signals you are low:**
- Nobody can say a clean clone plus the README produces a running system, because nobody checked.
- Setup docs are found stale when onboarding breaks, not before.
- Agents are pointed at internal docs as ground truth and none of it is tested.
- The documentation metric trends up while incidents trace to instructions that no longer match reality.
- Docs are mostly AI-generated and no one can say which are checked against the running system.

| Level | What it means here | Tell (what settles it) |
|---|---|---|
| 1 Blind | Nobody knows whether the instructions work; nobody has tried recently. | Follow the first five README steps of a service you never set up, on a clean machine. You cannot finish without asking, and nothing in the pipeline would have caught it. |
| 2 Tacit | New joiners get set up by a person; docs are patched afterwards. | Ask the most recent joiner how many times they asked a person to get the system running. More than once means the docs are repaired in conversation. |
| 3 Visible but inert | Docs are hand-maintained and reviewed; nothing executes them. | Diff the setup instructions against the build configuration. They disagree anywhere, and both were considered current. |
| 4 Acted on | Instructions are executed in the pipeline from a clean checkout, so drift fails. | Find the last time documentation broke the build: something ran the instructions and failed, not a joiner discovering it in week two. |
| 5 Durable | Executable docs extend as the system grows; generated prose is verified too. | Count repos executing their instructions in the pipeline against the total. New repos join the set by default, not by volunteering. |

**Score 4 when:** The load-bearing setup and run docs are executed in CI from a clean checkout, so drift turns the build red. The guide's three moves: define the load-bearing doc surface (setup, run, operate) with an owner; make the runnable parts execute in CI; demote everything else to labeled, untrusted prose. Docs that cannot execute (rollback runbooks, diagrams) need a game-day or an owner on a cadence.
**Evidence to collect:**
- Find the CI job that runs the README or a setup script from a fresh checkout (`grep -ri 'readme\|make setup\|bootstrap\|quickstart' .github Jenkinsfile Makefile`). A job executing the documented commands means 4.
- Diff documented commands against Makefile / package scripts / Dockerfile / CI steps. Disagreement means 3 or lower.
- Compare doc age with code age: `git log -1 --format=%ad -- README.md` against `git log -1 --format=%ad -- <src dir>`. A README untouched through many merges signals drift.
- Check for doc tests (markdown code-block runners, doctest, link or command checkers) and whether they are required checks.
- Grep docs for env vars, endpoints or tools that no longer exist in the code.
- Run the essay's cold-read check on the top operational doc: follow it literally as an agent that cannot ask, count wrong or missing steps, then ask whether anything in CI would have caught one. Check whether agent context files and code comments are inside the checked surface.
- Check whether docs outside the executable surface are labelled untrusted prose, and whether non-executable ones (rollback runbooks, diagrams) have a game-day, synthetic run or cadence owner.
- For level 5, count repos with an executed-docs job against the total, and check whether the repo template includes it and how AI-generated docs are verified.
**Small-team note:** For one repo the "last joiner" tell becomes: when did you last bootstrap it from a fresh clone? A scripted clean-checkout CI step running the setup commands is a legitimate level 4; "I know it works" without a run is 2.
**Cheapest moves up:**
- 1 to 3: run the README once from a clean checkout and fix what breaks; name an owner for setup, run and operate docs.
- 3 to 4: add a CI step that executes the setup and run commands from a clean checkout and fails on error.
- 4 to 5: add that step to the repo template, and mark remaining prose as untrusted or verify it on a cadence.

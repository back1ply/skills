# Flow & Throughput: the four dimensions

Source: "AI Readiness for Engineering Organizations" (Jurgen De Smet, 2026), pp. 42-58, and the
online assessment (howreadyfor.ai/assess). Level wording follows the online version.

Part question: can the work move without queueing? AI raises how fast individuals produce change; it does
nothing for review, integration, testing and release. A stage near capacity does not slow gracefully when
load doubles; it seizes. Score the worst case in scope, not the typical one. Not knowing is a 1.

## Contents
- 9 · Trunk-Based Development
- 10 · Velocity and the Constraint
- 11 · Organizational Design
- 12 · Code Ownership and Review Routing

## 9 · Trunk-Based Development
Read: field guide pp. 44-47; essay https://jurgendesmet.substack.com/p/ai-readiness-trunk-based-development (2026-05-05); https://howreadyfor.ai/d/trunk-based-development
**Question:** How old is the oldest branch alive anywhere in your scope right now, and what would it cost to merge it today?
**Why agents care:** An agent generates change faster than people do, and so does everyone else on trunk, so a branch's delta from trunk grows faster and compounds ("merge debt"). Conflicts land in code the resolver did not write, often in files AI touched on both sides, so resolution needs program-logic judgment and bugs slip through. Short branches keep the diff small enough for an agent (and a reviewer) to hold in context. Per the guide (2026), citing Kasi and Sarma: about 1 in 5 merges needs human intervention, conflicted code is twice as likely to carry a bug, and 75% of conflicts need program-logic reasoning. Merge debt compounds (more files, more churn, more clones, each multiplying the others) and is invisible: no dashboard tracks it, so it surfaces on merge day. The guide's highest-value response is shortening lifetimes to hours, backed by flags, fast tests and small increments, not smarter conflict tooling.
**Signals you are low:**
- Branches routinely live days or weeks; end-of-sprint merges become multi-day resolution jobs.
- The person resolving conflicts rarely wrote the conflicting code.
- The team says "continuous integration" but integrates weekly (a CI server is not CI).
- Nobody can state the age of the oldest open branch; no alert fires on divergence.
- "We are too big for trunk-based" is not a reason to score higher: per the essay (2026-05-05), Google (about 25,000 developers, one trunk) and Microsoft (200+ PRs a day to trunk, flags decoupling deploy from exposure) do it at scale. Score what exists, not the size excuse.

| Level | What it means here | Tell (what settles it) |
|---|---|---|
| 1 Blind | No idea how old branches are. Integration is an event, not a habit. | Sort open branches in the busiest repo by last commit; oldest is months old and nothing reports it. |
| 2 Tacit | Some teams merge daily out of discipline. Nothing requires it. | Branch ages across the two busiest teams differ (hours vs weeks) and no rule explains it. |
| 3 Visible but inert | Branch age is reported. Nothing stops a branch getting older. | Oldest branch passed the target and only "appeared on a list and stayed there". |
| 4 Acted on | Branch lifetime is bounded in hours by tooling, not good intentions. | The last branch to cross the limit was blocked or flagged automatically; flags and fast tests already existed. |
| 5 Durable | Short branches survive pressure; new repos start inside the same limit. | During the last big release or migration lifetimes did not move, or exceptions have owners and dates. A code freeze means the practice was switched off when needed. |

**Score 4 when:** branch lifetime is bounded in hours by policy and tooling (feature flags, fast tests), not goodwill. Reference definition per the essay (2026-05-05), quoting DORA: three or fewer active branches, each lasting no more than a few hours, merging to trunk at least daily, no code freezes. Per the live page, level 4 includes builds that refuse stale branches and flags that make unfinished work safe to merge.
**Evidence to collect:**
- `git for-each-ref --sort=committerdate refs/remotes --format='%(committerdate:short) %(refname:short)'`: oldest entries; months old = 1-2 territory, nothing in CI or a bot acting on them caps it at 3.
- Merged-branch lifetime from history: `git log --merges --format='%h %ad' --date=short` and compare each merge to its branch's first commit (`git merge-base`); median in hours vs days.
- Open the CI/bot config for a branch-age or stale-branch check that fails or blocks (not just comments); also a merge queue or branch-protection rule. Present and blocking = 4.
- Look for a feature-flag mechanism (flag library, flag config) and test duration in CI logs; short branches without flags/fast tests are fragile.
- Search for freeze/exception files or release-branch policy; exceptions with owner and date point to 5.
- Count active branches per repo against DORA's three-or-fewer; a CI server alone is not evidence (periodic integration with automated builds is 3 at best).
**Small-team note:** For one or two people, branch age still scores: few branches and a trunk-only habit is real, but a habit with no hook or branch-protection rule is 2, not 4. Don't award 4 for "I always merge fast".
**Cheapest moves up:**
- 1 to 2/3: add a scheduled report of oldest open branches. Our addition: a report only makes merge debt visible; the guide's real fix is shorter lifetimes.
- 3 to 4: make the age limit a blocking check or auto-flag, and put feature flags plus fast tests in place so the limit is survivable (an organizational decision about work flow, not a git setting).

## 10 · Velocity and the Constraint
Read: field guide pp. 48-50; essay https://jurgendesmet.substack.com/p/ai-readiness-ai-velocity-simulation (2026-05-26); https://howreadyfor.ai/d/velocity-and-the-constraint
**Question:** If merge-request volume doubled tomorrow anywhere in your scope, which stage fills up first? And do you know that, or are you guessing?
**Why agents care:** Agents raise arrival rate (more and larger MRs) while lowering service rate (big PRs reviewed by fatigued people), so utilization climbs toward the cliff. Per the guide (2026), wait is roughly equal to service time at 50% utilization, 4x at 80%, 9x at 90%, 19x at 95%. Output beyond the constraint's capacity is just a longer queue; the hard discipline is throttling generation to what the constraint can absorb (subordination: if review absorbs 1.2x, do not generate 2x). Averages hide the worst cases: per the essay (2026-05-26) the p90 and p99 waits are far worse than the mean, so some MRs wait days. Per the guide (2026), Harness found faster shipping after AI in 55% of low-automation, 64% of moderate and 78% of fully automated organizations, and DORA 2024 found delivery throughput down 1.5% per 25% more AI adoption while review and approval speed improved (the signature of optimizing a non-constraint). The constraint can also sit upstream of the pipeline (problem selection, requirements): unvalidated work in the queue is itself a cost.
**Signals you are low:**
- Doubled volume has never been walked against the real pipeline stages (review, CI, test, deploy, monitoring).
- Development metrics climb while delivery metrics flatten or fall.
- The last bottleneck was found in an incident, not on paper.
- No enforced WIP cap; new work starts whenever someone is free.
- Effort goes to stages that are easy to improve, not to the constraint.
- Stage tells (per the essay): review (PRs age, skim-approvals, AI PRs wait longer), CI (builds queue, "just rerun it" is the default, recovery over an hour), deployment (manual gates, approval queues, weekend releases), monitoring (rising MTTR, overtime absorbing incidents).

| Level | What it means here | Tell (what settles it) |
|---|---|---|
| 1 Blind | No idea where work queues. Every stage feels equally busy. | Ask which stage fills first if MRs double; several confident, disagreeing answers = nothing measures. |
| 2 Tacit | Experienced people know where it jams from living through it. | Three people agree where it jams but none can point to a number. |
| 3 Visible but inert | Queue and waiting times are measured. Nothing limits what enters. | Longest-queue stage is on your dashboard, but nothing limits work entering it. |
| 4 Acted on | A WIP cap is enforced by tooling that refuses work past the line. | When the constraint last hit its limit, something held or refused new work automatically, not a lead asking people to slow down. |
| 5 Durable | The cap moves when the constraint moves, and holds when delivery is behind. | Constraint a year ago vs now: it moved and limits moved with it. A cap still where first set = not revisited. |

**Score 4 when:** the constraint is identified and a WIP limit is enforced by tooling that blocks new work past the cap, not discovered in an outage. Per the live page the limit comes from measurement, not from what felt reasonable; level 5 means caps are still enforced in the quarter delivery is behind and are revised when the constraint moves.
**Evidence to collect:**
- Compute PR/MR time-to-first-review and open-to-merge from the platform API or `git log` merge dates, as median and p90/p99 (not the mean alone); a long, growing tail at one stage names the constraint (review aging with skim-approvals, CI "just rerun" habits, manual deploy waits).
- Open CI config for retry/rerun-on-red patterns and main-branch success rate; reruns as default = CI is the constraint.
- Look for an enforced cap: limit on open PRs per author, merge queue, board WIP limit tied to automation, or an agent concurrency limit. A dashboard or a convention alone = 3; refusal by tooling = 4.
- Search docs or retros for a written constraint analysis ("which stage fills first") and its date; stale date vs current stage layout is the 5 test.
- Compare throughput of feature branches vs main/delivery over time: dev activity up, delivery flat is the guide's signature gap.
**Small-team note:** With one or two people the pipeline stages are still real (CI time, deploy wait, your own review). Score from measured queue times for those; "I can feel it" is 2. A WIP cap can be an agent-concurrency or open-PR limit enforced by a script or branch rule.
**Cheapest moves up:**
- 1 to 2/3: do the paper simulation (double volume, walk each stage) and put the stage's wait time on a dashboard.
- 3 to 4: follow the guide's order: exploit (smaller PRs, cut low-value ceremony), subordinate (cap AI output to what the constraint absorbs), enforce the cap in tooling, then elevate capacity (add reviewers, automate deploys, observability) only after the first two are exhausted. Then repeat: the constraint moves.

## 11 · Organizational Design
Read: field guide pp. 51-54; essay https://jurgendesmet.substack.com/p/ai-readiness-organizational-design (2026-06-23); https://howreadyfor.ai/d/organizational-design
**Question:** Pick a recent feature that crossed team boundaries anywhere in your scope. If AI doubled what every one of those teams produced tomorrow, would it arrive sooner, or would the queues between them simply grow?
**Why agents care:** An agent works inside whatever boundary it can see, and each team's assistant is competent only within its component. Integration needs two domains understood at once, so the seams (handoffs, cross-team PRs) are where AI output queues and where bugs surface. Per the guide (2026), CircleCI measured median teams up 15.2% on feature branches and down 6.8% on main; the guide frames team design as the deciding variable (it gives the top 5% as +85.1% and +26.2%; the essay once says top 10%, prefer the guide). Also per the guide (2026), Faros AI found developers completing 21% more tasks and merging 98% more PRs with no measurable delivery improvement at organization level. Worked example (guide and essay): a 4-team, 3-handoff feature took 6 weeks (2 working, 4 waiting); after each team doubled output it took 8. In component-team structures cross-team review is the integration, so a review-time rise is an integration-capacity problem. Fixed ownership makes every cross-boundary change queue behind one team.
**Signals you are low:**
- A typical customer feature needs 3+ teams and several handoffs.
- Cross-team PRs got larger and slower after AI.
- Team boundaries are frozen to a fixed architecture (the Inverse Conway Maneuver as dogma) and cannot move.
- Teams own delivery only; requirements arrive via intermediaries instead of customer contact.
- Narrow-ownership teams duplicate code instead of reusing across components, because reaching into another team's code needs coordination nobody starts (per the essay).
- Nobody tracks handoff or cross-team queue metrics.

| Level | What it means here | Tell (what settles it) |
|---|---|---|
| 1 Blind | No view of where work waits between teams. Structure discussed only in reorganisations. | Last cross-team feature's ticket history: count teams, then idle days between; cannot produce the second number. |
| 2 Tacit | A few connectors move work across boundaries, by relationship not design. | Everyone names the same one or two people who get things across, and they hold no role that says so. |
| 3 Visible but inert | Flow and handoff numbers are on a dashboard. No boundary ever moves because of them. | Last boundary change came from a reorganisation, not the dashboard. |
| 4 Acted on | Breaching a queue target triggers a structural review on its own. | Last time a queue between two teams breached, a review was scheduled automatically, not because a senior person happened to look. |
| 5 Durable | Boundaries move with the architecture; shared ownership outlasts the people who arranged it. | When the architecture last changed shape, team boundaries moved with it without waiting for an annual reorg. |

**Score 4 when:** cross-team handoff and queue metrics are tracked on a cadence, and breaching the target automatically triggers a structural review.
**Evidence to collect:**
- Take the last cross-team feature: ticket links/epics and transition timestamps; count distinct teams and idle days between hand-offs (git history alone cannot give this; use the tracker export).
- Fraction of recent PRs touching paths owned by 2+ teams (map changed paths to CODEOWNERS entries) and their time-to-merge vs single-team PRs.
- Look for a handoff/queue dashboard and an alert or scheduled review rule tied to a threshold; a dashboard with no linked action = 3.
- Check commit/review history for who actually crosses boundaries; the same one or two names = 2.
- Look for written ownership/boundary change history (ADRs, team charter changes) dated against architecture changes.
- The essay's three checks: can any team member review any part of the team's domain; does the team talk to customers directly; when the architecture changes, must the team structure change too, or is scope broad enough to adapt?
**Small-team note:** A one- or two-person codebase has no team seams; score the seams you do have (a vendor or another team's API, a shared platform you wait on). If there are truly none, the instrument still requires a score: nothing records where work waits, so it is 1. Say the dimension is barely exercised, and report the floor with and without it; never award 4 or 5 by default.
**Cheapest moves up:**
- 1 to 3: count teams, handoffs and waiting vs working weeks on one recent feature; start tracking cross-team queue time.
- 3 to 4: attach a target and an automatic structural-review trigger to the metric.
- The guide's direction: widen each team's scope with strong CI and small changes, component mentors who teach rather than gate, and teams owning discovery as well as delivery. Not "let everyone touch everything".
- Staged sharing path (essay): read-only access, supervised pull requests, gated review, open contribution with mentor review, then full shared ownership where anyone can review. Use it to place a team and name the next step.
- Anti-patterns to flag: Conway's Law treated as fate; the Inverse Conway Maneuver freezing teams to a fixed architecture; autonomy without coordination mechanisms (Spotify's model, per the guide, was never fully implemented and was abandoned at 3,000 people).

## 12 · Code Ownership and Review Routing
Read: field guide pp. 55-58; essay https://jurgendesmet.substack.com/p/ai-readiness-code-ownership-and-review (2026-04-28); https://howreadyfor.ai/d/code-ownership-and-review-routing
**Question:** If the busiest team in your scope vanished tomorrow, how many open changes would have nobody left qualified to review them?
**Why agents care:** AI-generated code is a "minor contributor" in Bird's sense (zero history with the module), so it needs reviewers who know the area. If routing sends all of it to one team, tripled volume lengthens that queue and then lowers review quality into rubber-stamping; per-reviewer limits (per the guide, about 200-400 lines per session) do not scale by adding people to a silo. Review also transfers knowledge, so narrow routing narrows who can ever review: per the guide (2026), citing Rigby and Bird, reviewing raises the distinct files a developer knows by 66% to 150%, and 67-86% of contributors to Qt and OpenStack modules only reviewed. Per the guide (2026): LinearB found AI PRs wait 4.6x longer for review and AI code accepted about 33% against 84% for human code; Faros AI found PR size +154% and review time +91%. A system answers in one of three ways: rubber-stamp, accept the queue, or distribute the load; most pick the first two by accident. Caution (essay, 2026-04-28): Stack Overflow 2025 survey data suggests reviewers currently scrutinize AI code more, not less, so test for rubber-stamping instead of assuming it.
**Signals you are low:**
- One or two teams carry a review queue several times deeper than others.
- CODEOWNERS routes each path to a single team by default.
- Large AI PRs are approved faster than a human could read them.
- An entire service has exactly one team qualified to review it, and people know which.
- Nobody monitors review-queue depth, so concentration surfaces only when someone leaves.
- Review capacity is per reviewer: a fourth person added to a silo does not multiply it. Per the guide (2026), citing SmartBear/Cisco: effectiveness drops after about 60 minutes and above 450 lines per hour, so a 400-line PR at 300 lines per hour already passes the wall.

| Level | What it means here | Tell (what settles it) |
|---|---|---|
| 1 Blind | Nobody knows who could review what. Changes find a reviewer by habit. | Last twenty merged changes to the most critical service have one or two distinct reviewers, and nothing records who else could. |
| 2 Tacit | A few people review everything important, and everybody knows who. | Last month most changes to the critical area went to the same reviewer. |
| 3 Visible but inert | Ownership is written into a file. Nothing watches the queue behind it. | Busiest owner's review wait rose over the last quarter and routing did not change. |
| 4 Acted on | Routing spreads across qualified reviewers; queue depth triggers a change. | Last time one reviewer's queue passed its limit, something rerouted or escalated automatically, not a volunteer. |
| 5 Durable | Breadth is maintained deliberately, so a departure does not take an area with it. | Qualified reviewers per critical area now vs a year ago held or grew across joiners and leavers. |

**Score 4 when:** CODEOWNERS routes to breadth (people across teams) and review-queue depth is monitored with action, not concentrated in one silo by habit.
**Evidence to collect:**
- Distinct reviewers on the last 20 merged changes to the most critical path (platform API or `git log --merges` plus review data); 1-2 names = 1-2, several = 3+.
- Open CODEOWNERS (repo root, `.github/` or `docs/`): single-team entries per path = silo; entries listing people across teams or a rotating group = breadth. File present but no queue metric = 3.
- Reviewer concentration: share of reviews done by the top reviewer per area over the last month/quarter, and review wait trend.
- Look for automation that reroutes or escalates on queue depth (round-robin/load-balanced assignment, auto-reassign, depth alert). Absent = cannot be 4.
- Compare review wait for AI-assisted vs human PRs where the platform labels them; a large gap on a single-team path points to routing, not reviewer negligence.
- Reviewer counts per area by quarter (authors plus reviewers with merged-change history) to test 5; also look for approval times versus PR size (large PRs approved in minutes = rubber-stamping).
**Small-team note:** With one or two engineers, "distinct reviewers" cannot be several people. Score honestly: if the only reviewer is the author or one peer, that is 1-2 for the reviewer-breadth tell. Substitute checks that do real review work (required CI, agent review plus a human, a second reviewer for risky paths) and say that a bus-factor of one stays low regardless.
**Cheapest moves up:**
- 2 to 3: write CODEOWNERS and start tracking review-queue depth and wait per owner.
- 3 to 4: point CODEOWNERS at developers across teams, not one team, and add an automatic reroute or escalation when a queue passes its limit. Per the essay, CODEOWNERS adoption tends to reduce merge time and redistribute load (Palanisamy, 844,000+ PRs); the target list decides the outcome. The aim is enough qualified reviewers per area across teams, not every team knowing everything.
- The guide's conditions for broad ownership: reliable CI that catches mechanical defects before human review, automated architecture guardrails, and practices that build shared context (review itself).

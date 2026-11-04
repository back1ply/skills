# AI readiness: evidence protocol

Source: the instrument's own rule that every level has a tell, turned into a working protocol for evidence-based scoring. Use it as the brief for each scoring agent, and as the bar for accepting their scores.

## Contents
- Hard limits
- What counts as evidence
- Where to look
- Splitting the work across agents
- Calibration
- Spot-checks before reporting
- Owner questions
- Reliability and history
- Report format

## Hard limits
Copy these into every scoring agent's brief, word for word:
- Read-only. Do not edit, create, stage, commit, stash, check out, pull or fetch anything in the scored repos. Another session may be working there.
- Allowed: file reads and searches, `git log`, `git show`, `git grep`, `git ls-files`, `git blame`, `git for-each-ref`, `git shortlog`, listing commands, and read-only CI or ticket-tracker API calls.
- Do not run build recipes, tests, migrations, deploy tools, cloud CLIs or anything that calls a live system. Never trigger, rerun or reconfigure a CI job; never write to a tracker.
- Never print a secret value.

## What counts as evidence
- Every score cites at least one of: a `file:line` with a short quote, a commit hash, or the output of a command or API call run this session.
- Every "none", "missing" or "never" names the search behind it (pattern and paths). A negative from one search term is not an absence.
- A gate is proven by its config, not a doc that mentions it: open the hook config or CI file and quote the line. Check whether the stage is wrapped to warn (`catchError`, `continue-on-error`, `allow_failure`, `|| true`); a warning gate is level 3.
- A level 4-5 claim needs a run you can point to: the build that went red on a violation, or the exception list with dates.

## Where to look
| Dimension area | First places |
|---|---|
| Structure, boundaries, architecture (1, 18) | Import-boundary or layer tests, dependency-checker config, workspace or build graph config |
| Complexity, drift (2, 4) | Lint config thresholds, suppressions count (`git grep -c "noqa\|eslint-disable"`), duplication reports |
| Vocabulary (3) | Glossary files, generated docs, accepted-values or enum tests |
| CI, tests, churn (5-7) | CI file and recent build history (note the retention: keep-last-N limits what you can count), coverage or mutation config, `git log --grep` for reverts and fixes |
| Debt (8) | Backlog or register files, waiver and expiry lines, ADRs that record removed checks |
| Branches, flow (9-10) | `git for-each-ref --sort=committerdate refs/remotes`, `git rev-list --left-right --count main...<branch>`, CI concurrency and lock settings |
| Org, ownership (11-12) | CODEOWNERS, `git shortlog -sn`, review settings, the ticket tracker |
| Decisions, requirements (13-14) | ADR index and statuses, spec or backlog templates, tests that cite ADRs |
| Security, docs (15-16) | Secret scanning, SAST config and whether it blocks, setup docs and whether CI runs them from a clean checkout |
| Guardrails, deps, release (17, 19-20) | The coding-standards file (does each rule name its check?), lockfile checks, package age cooldowns, deprecation markers, consumer or exposure declarations, changelogs |

## Splitting the work across agents
- One agent per repo per half (dimensions 1-10, 11-20) keeps each context small. Give each the same brief and the live question text.
- Use a mid-tier model for evidence gathering; keep calibration and the final read with the parent.
- Agents return per dimension: score, tell checked, 1-3 evidence items, why not one higher, cheapest move up, and `NEEDS OWNER` where applicable. Cap reports at about 1,200 words.

## Calibration
Agents read the same ladder differently. Before reporting:
1. List every dimension where two repos or two agents differ by a level or more, and every score of 1.
2. Re-read that dimension's level text and tells, then apply one reading to all repos.
3. Common corrections: an owner who visibly acts (fixes red builds, merges daily) but nothing requires or measures it is 2, not 1. Nothing reported or measured cannot be 3, however good the habit. Something that warns but never blocks is 3, not 4.
4. Anti-patterns seen in agent output (reject them):
   - "Not applicable" or "skip": the instrument has no skip. Score by the rules and note the context beside the score.
   - Level 4 for a threshold, checklist or notice a person chooses to act on: anything needing a person to choose is 3 at most.
   - "Evidence" that mutates the repo (planting a violation, flipping an operator, running the suite): not read-only. Only with the owner's permission, in a discarded worktree.
4. Report each change with its one-line reason.

## Spot-checks before reporting
Open the files yourself for the claims a decision rests on: each "blocks the build", each absence that sets a 1, each date or age, and the evidence behind the floor. Report how many you checked and that the rest are agent-reported with references.

## Owner questions
Mark tells that only a person can answer `NEEDS OWNER: <exact question>`. Team-shaped tells (two recent joiners, the busiest team, cross-team waits) usually land here for small teams. Ask the owner at most three, each with the answer you would recommend and how it changes the score; fold the rest into "not checked".

## Reliability and history
- **Independent second scoring.** Give a fresh agent the same brief and scope, no access to the first run's notes or scores. Compare per dimension: exact matches, off-by-one, off-by-two or more. Report exact agreement per cluster. Treat any off-by-two as a broken tell or missing evidence, and resolve it by opening the evidence, not by averaging.
- **Machine-settled tells first.** Branch age, warn-only CI stages, CODEOWNERS presence, author spread, exception lists and their dates, build retention, revert counts: these should never disagree between runs. If they do, the evidence step was skipped.
- **Dated record.** Save each run as scope, date, the 20 scores, and one evidence line per score, next to the previous runs. Compare with the last record and explain every drop and every rise.
- **Predict, then re-score.** Before a fix, write down the dimension and level it should reach. After it lands, re-score that dimension and its cluster. Report predicted vs actual; an unpredicted move means the tell or the fix is wrong.
- **Validity check.** Collect where agents actually caused rework in scope (revert and fix commits, agent session logs, incident notes) and map each to a dimension. Low scores should sit where the rework is. When they do not, re-examine those scores before acting on them.

## Report format
1. Floor (and which dimensions hold it), sum and band, the scope.
2. If the floor comes only from team-shaped dimensions, also give the floor without them.
3. The pattern across clusters (for example: enforcement strong, measurement weak).
4. Up to three owner decisions with recommendations.
5. Calibration changes.
6. The scorecard HTML (copy `assets/scorecard-template.html` from this skill's folder and fill it in) and its path; offered next moves (cheapest move per low dimension), not done.
7. Verification: what you checked yourself, what is agent-reported, what was not checked.

# IMP workflows for a coding agent

Step-by-step playbooks this skill builds from the IMP rules. They are this skill's interpretation, not text from the site. Rule numbers point to `rules.md`.

## 1. Starting a feature

1. **Read the Contract** for the area you're touching (rule 13). If there isn't one, say so and offer to start one (see `contract.md`).
2. **Check the story** (rule 1). Is there a written success criterion the team can see? If not, ask the human for one before committing to the work.
3. **Ask the One Question** (rule 5): *what do we still need to learn before we can build this?* Write down the answer as a list of unknowns.
4. **Spike the unknowns** (rules 15, 16, 18). For each real unknown, propose two to four cheap throwaway spikes that can run in parallel (separate worktrees or branches). Name the hypothesis each spike tests. Put anything user-facing in front of the customer early.
5. **Design in an artifact** (rule 14). Before writing production code, talk through the design in an editable document or prototype with the human. Offer options and accept rejection. Keep the artifact as the design record.
6. **Pin existing behaviour** before changing old code (rule 20). Find out why each guard is there before you move it.

## 2. Inside one pull request: breathe in, breathe out (rule 12)

**Inhale:**
- Build until the feature shows its real shape. Sprawl is allowed here.
- Write each obligation into the Contract as it's agreed, both functional and non-functional (rule 20).
- Once the "what" is settled, build it complete rather than leaving shortcuts (rule 16).

**Exhale** (same PR, before asking to merge):
- Fold the new code back into what already exists. Remove duplicates, merge near-copies into the existing abstraction, delete dead code, and simplify anything that got harder to follow. Agents add complexity by default, so this step is your job.
- Check the Contract against what was agreed with the human, not against what you happened to build.
- Run the mutation gate. Delete tests that catch nothing no other test catches (rule 26).
- Run every guardrail (lint, types, structure, security, duplication, complexity) (rules 19, 24).
- No technical debt leaves the PR. If something is kept on purpose, record it in the Contract with its reason.

**Merge:**
- Keep branches short-lived and rebase or merge from main often (rule 23).
- Label honestly (rule 9): `fix:` only for a defect in code live in production; everything else is `refine:`.
- State the PR's **blast radius** (what could break, for whom, and how badly) so the team can decide whether green can merge itself or a human must review (rule 27).

## 3. Deciding how much review a change needs (rule 27)

Use blast radius, not habit:

| Blast radius | Typical examples | Gate |
|---|---|---|
| Low | Internal tools, copy, styling, behind a flag, easy rollback | Automated checks + adversarial model review; green merges itself |
| Medium | User-facing features with fast rollback, non-critical data paths | Above, plus canary or staged rollout |
| High / catastrophic | Money movement, auth, data deletion or migration, security boundaries, irreversible actions | Human review required, on top of everything above |

Treat this table as a starting point, not something the site prescribes. Sebastian Scholl's essay argues that a deliberate human gate on high-risk work is a control to keep, not a bottleneck to remove.

## 4. A bug report arrives (rules 9, 28)

1. Confirm it's live in production. If not, it's a refinement, not a bug.
2. Stabilise first: roll back or hotfix if users are affected.
3. Add the missing obligation to the Contract. Make it executable and show it fails against the current code.
4. Show the new test kills the mutant that matches the bug.
5. Fix the code. Label the PR `fix:`.

## 5. Daily brief (rule 8)

When asked for a daily or morning brief, cover the **whole team's** last 24 hours, people and agents: merged PRs, open PRs and their state, incidents, Contract changes, anything blocked. Post it somewhere public (rule 6). Keep it short.

## 6. Weekly rhythm (rules 2, 4)

- **Monday:** each person names one big focus and a demoable vertical slice for Friday ("call your shot").
- **During the week:** work flows PR by PR. There are no sprints.
- **Showcase:** only finished work counts, and product work is demoed in production. No criticising the team's decisions from above during the showcase.
- **Forecasts:** don't give dates while still turning unknowns into knowns. Once over the top of the hill, give a forecast you believe.

## 7. Building a guardrail (rules 19, 24)

When an agent makes the same mistake twice, turn the lesson into a machine check. Don't just add a prompt note. In rough order of preference:

1. An existing linter rule or config switch.
2. A custom rule (Semgrep, ast-grep, a lint plugin).
3. An architecture or boundary check (import rules, package boundaries).
4. A hook that runs on the agent's own actions (for example a Claude Code hook).
5. An LLM reviewer against a written convention, for things only a reader can judge.

A guardrail is software: give it tests and keep it in the repo.

## 8. Measuring (rule 9)

- Count production defects (`fix:`), not PR counts. Small PRs inflate PR counts but can't inflate the defect count.
- Track how close you run to plan or usage limits, since hitting one stops agents mid-task. Flat-rate dollars aren't worth tracking. Matthew Canham's essay disagrees about unmeasured spend, so mention that when cost matters to the team.

## 9. Pairing with people (rule 21)

Everyone pairs with an agent all day. Pair two humans when there's a decision neither should make alone. Mark Ryall's essay adds that human pairing still spreads knowledge, keeps people honest, and helps grow junior engineers, which an agent can't do.

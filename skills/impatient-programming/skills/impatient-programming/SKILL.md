---
name: impatient-programming
description: "Work the Impatient Programming (IMP) way: Obie Fernandez's rewrite of XP's 29 rules for teams that build with coding agents. Covers the Contract (executable obligations kept in the repo), breathe in / breathe out inside every PR, mutation-tested tests that must earn their place (the kill matrix), green merges itself by blast radius, fix: vs refine: labels, Contract-first bug fixes, regeneration drills, guardrails enforced by machines, daily agent briefs and the weekly showcase. Use when the user mentions IMP, Impatient Programming, imps, the Contract, contract coverage, breathe out / exhale, kill matrix, green merges itself, the One Question, or impatientprogramming.org; asks to apply IMP or XP-for-agents to a repo or PR; wants an IMP-style PR, bug fix, daily brief or guardrail setup; or asks what an IMP rule says."
---

# Impatient Programming (IMP)

IMP keeps XP's values (communication, simplicity, feedback, courage, respect) and rewrites each of Don Wells's 29 XP rules from 1999 for a world where typing is nearly free and agents do much of the coding. Its people are **imps**, and they keep their agents on a tight leash. When this skill is active, you are one of those agents.

Canonical source: <https://impatientprogramming.org/>. The rules and the agent primer are by Obie Fernandez, CC BY 4.0. The snapshot in this skill is from 2026-10-27. If the user needs the latest wording, fetch the live page.

## Core moves (always apply)

1. **Read the Contract first.** It's the team's written, versioned, ideally executable description of what the software must do, both functional and non-functional. If none exists for the area, say so and offer to start one. → `references/contract.md`
2. **Ask the One Question** before building: *what do we still need to learn before we can build this?* Spike the unknowns in parallel. Put prototypes in front of the customer.
3. **Pin existing behaviour** before changing old code, and find out why each guard is there before moving it.
4. **Breathe in, breathe out, in the same PR.** Sprawl until the feature takes shape. Then fold it back into what already exists: dedupe, simplify, delete dead code. No technical debt leaves the PR.
5. **Write obligations into the Contract as they're agreed.** On the exhale, check the Contract against what was *agreed*, not against what you built.
6. **Every test must earn its place.** Mutation-test. Drop any test that catches nothing another test doesn't already catch.
7. **Machines enforce standards.** When a mistake happens twice, build a guardrail, not a prompt note.
8. **Label honestly.** `fix:` means a defect in code live in production. Everything else is `refine:`.
9. **Bugs are Contract gaps.** Add the obligation first, see it fail, prove it kills the matching mutant, then fix.
10. **Green merges itself, scaled by blast radius.** State the blast radius on every PR. Save human review for changes that could cause catastrophic damage.
11. **Integrate continuously.** Keep branches short-lived. Work in the open so the whole team learns from each session.

## Load the reference you need

| Situation | Read |
|---|---|
| What exactly does rule N say, or what's its reasoning? | `references/rules.md` (all 29 rules, full text, CC BY) |
| Quick orientation or paste-in briefing for another agent | `references/primer.md` (the site's official agent primer) |
| Writing, reviewing or enforcing a Contract; regeneration drills; Contract-first bug fixes | `references/contract.md` |
| Running a feature, a PR, a bug fix, a daily brief, the weekly rhythm, review gates, or building a guardrail | `references/workflows.md` |
| Choosing guardrail tools for a stack | `references/tools.md`, then fetch the live category page it links |
| Why IMP exists, values, objections, case studies, essays | `references/background.md` |
| Which site page covers what, and when it last changed | `references/sources.md` |

## The 29 rules at a glance

**Planning:** 1 Get your story straight · 2 Call your shot every week · 3 Every green merge is a release, ideally · 4 No timeboxes; a weekly showcase is the heartbeat · 5 The One Question starts each feature

**Managing:** 6 Work in the open, with your agents · 7 Set a sustainable attention budget · 8 Agents brief the team every day · 9 Throughput is measured, and labeled honestly · 10 Move attention around · 11 Fix IMP when it breaks

**Designing:** 12 Simplicity: breathe in, breathe out · 13 Write the Contract · 14 Use artifacts for design sessions · 15 Spikes are cheap, so run several in parallel · 16 Experiment on what to build; boil the lake on how you build it · 17 Keep it regenerable; regenerate when it's worth it

**Coding:** 18 Put the solution in front of the customer · 19 Standards are enforced by machines · 20 Agree on the Contract, and make it executable · 21 All production code is pair programmed, with an Agent · 22 Retired · 23 Integrate continuously · 24 Guardrails fire on every change · 25 Collective ownership, agents included

**Testing:** 26 Every test must prove it's worth keeping · 27 Green merges itself · 28 When a bug is found, the Contract was missing something · 29 The Contract must be met, and contract coverage is published

## Working notes

- IMP is meant for teams. For a solo user, apply the parts that fit (Contract, breathe out, mutation testing, honest labels, guardrails) and skip the team rituals unless asked.
- Don't invent IMP doctrine. If the rules don't cover something, say so and offer your own suggestion, labeled as yours.
- The essays in `background.md` disagree with some rules (for example on human review gates, regeneration, and pairing). Bring up the disagreement when it matters to the user's decision.
- When quoting the site, quote only the rules or the primer, and link the page.

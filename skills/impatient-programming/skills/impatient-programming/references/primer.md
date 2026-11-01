<!-- Source: https://impatientprogramming.org/primer.md by Obie Fernandez, licensed CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/). Unchanged copy. Snapshot: 2026-10-27. -->

# Impatient Programming: a primer for coding agents

eXtreme Programming, revisited for the age of coding agents.

Paste this into a fresh agent session so the agent knows how an IMP team works. The canonical copy lives at https://impatientprogramming.org/primer.md

## What IMP is

Impatient Programming (IMP) takes the 29 rules of Extreme Programming that Don Wells published in 1999 and asks one question of each: what does it look like when typing is nearly free and you have a team of agents at your side? The people who practice it are imps, and they keep their agents on tight leashes. You are one of those agents.

## Before you write code

- Read the Contract first. It is the team's description of what the software must do, functional and non-functional. (Rule 13)
- Ask the One Question: what do we still need to learn before we can build this? (Rule 5)
- If the answer is unclear, run several spikes in parallel and let the results argue it out. Put throwaway prototypes in front of the customer. (Rules 15, 18)
- When you change existing code, pin the behavior it already has before you touch it. Find out why each fence is there before you move it. (Rule 20)

## While you write code

- As you and your human work out what the feature must do, write each obligation into the Contract, functional and non-functional, and make it executable. (Rule 20)
- Breathe in, then breathe out, in the same PR. Sprawl until the feature shows what it wants to be. Then fold what you learned back into what already exists. You add complexity by default, so the exhale is your job too. (Rule 12)
- Once you know what to build, build it complete. (Rule 16)
- Follow the team's conventions. Machines enforce the standards. (Rule 19)
- On the exhale, check that the Contract is complete and says what you agreed with your human. (Rule 20)
- Integrate continuously. Don't keep long-lived branches. (Rule 23)
- Work in public channels, so what one session learns the whole team knows. (Rule 6)
- You share ownership of the code with the people, maintenance included. (Rule 25)

## Tests

- Every test must prove it's worth keeping. Run it through the kill matrix with mutation testing, and keep it only if it catches something no other test catches. (Rule 26)
- When a bug is found in code that's live in production, add the missing obligation to the Contract first. Make it executable. Prove the new test kills the mutant that matches the bug. Then fix the code. (Rule 28)
- Report the Contract as met or not met. Publish contract coverage, the share of the system the Contract covers. (Rule 29)

## Merging and reporting

- Label PRs honestly. Use `fix:` only for a defect in code that's live in production. Everything else is `refine:`. (Rule 9)
- Green merges itself. Blast radius decides how much human review a change gets. Every green merge is a release. (Rules 3, 27)
- Each morning, post a brief on what the whole team did, people and agents alike. (Rule 8)

## The 29 rules

Each line gives the 2026 rule, then Don Wells's 1999 rule it revisits.

### Planning

1. **Get your story straight.** (1999: User stories are written.)
2. **Call your shot every week.** (1999: Release planning creates the release schedule.)
3. **Every green merge is a release, ideally.** (1999: Make frequent small releases.)
4. **No timeboxes. A weekly showcase is the heartbeat.** (1999: The project is divided into iterations.)
5. **The One Question starts each feature.** (1999: Iteration planning starts each iteration.)

### Managing

6. **Work in the open, with your agents.** (1999: Give the team a dedicated open work space.)
7. **Set a sustainable attention budget.** (1999: Set a sustainable pace.)
8. **Agents brief the team every day.** (1999: A stand up meeting starts each day.)
9. **Throughput is measured, and labeled honestly.** (1999: The Project Velocity is measured.)
10. **Move attention around.** (1999: Move people around.)
11. **Fix IMP when it breaks.** (1999: Fix XP when it breaks.)

### Designing

12. **Simplicity: breathe in, breathe out.** (1999: Simplicity.)
13. **Write the Contract.** (1999: Choose a system metaphor.)
14. **Use artifacts for design sessions.** (1999: Use CRC cards for design sessions.)
15. **Spikes are cheap, so run several in parallel.** (1999: Create spike solutions to reduce risk.)
16. **Experiment on what to build. Boil the lake on how you build it.** (1999: No functionality is added early.)
17. **Keep it regenerable. Regenerate when it's worth it.** (1999: Refactor whenever and wherever possible.)

### Coding

18. **Put the solution in front of the customer, and stop guessing what they want.** (1999: The customer is always available.)
19. **Standards are enforced by machines.** (1999: Code must be written to agreed standards.)
20. **Agree on the Contract, and make it executable.** (1999: Code the unit test first.)
21. **All production code is pair programmed, with an Agent.** (1999: All production code is pair programmed.)
22. **Retired.** (1999: Only one pair integrates code at a time.)
23. **Integrate continuously.** (1999: Integrate often.)
24. **Guardrails fire on every change.** (1999: Set up a dedicated integration computer.)
25. **Collective ownership, agents included.** (1999: Use collective ownership.)

### Testing

26. **Every test must prove it's worth keeping.** (1999: All code must have unit tests.)
27. **Green merges itself.** (1999: All code must pass all unit tests before it can be released.)
28. **When a bug is found, the Contract was missing something.** (1999: When a bug is found tests are created.)
29. **The Contract must be met, and contract coverage is published.** (1999: Acceptance tests are run often and the score is published.)

## More

- The rules, with the reasoning behind each one: https://impatientprogramming.org/rules/
- The Contract: https://impatientprogramming.org/xp-revisited/#the-metaphor-finally-has-a-home
- The values: https://impatientprogramming.org/values/
- The intro, "eXtreme Programming, Revisited": https://impatientprogramming.org/xp-revisited/
- Every page on the site: https://impatientprogramming.org/llms.txt

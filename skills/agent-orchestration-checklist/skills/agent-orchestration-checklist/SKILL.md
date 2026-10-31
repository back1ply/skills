---
name: agent-orchestration-checklist
description: Checklist for handing big coding tasks to an orchestrator agent that spins up sub-agents (Claude Code, Codex) and judging the result without reading all the code, using Maximilian Schwarzmüller's five developer skills for the AI era (judgment, orchestration, ownership, broad expertise, curiosity). Covers deciding what not to build, naming constraints and trade-offs, sandboxing agents, self-verification (tests, browser checks, strict lint the agent may not loosen), and deterministic work reports. Use when setting up an orchestrator or multi-agent workflow, scoping a large task for agents, deciding how to verify agent output, reviewing what an agent run produced, or the user asks "how should I work with agents", "what skills do devs need with AI", or "how do I trust agent output without reading every line".
---

# Agent orchestration checklist

Distilled from "What I would focus on" (Maximilian Schwarzmüller, 2026-10-28), based on his CityJS Athens talk. This is one creator's view of how to work; treat the rules as his practice, not settled fact.

## Core mental model
The developer moves up the abstraction ladder and becomes something like a technical product owner ([0:02:04](https://youtu.be/I6V5dmoZplU?t=124)). Agents implement. The human owns four things agents can't: **deciding** what to build and what to leave out, **enabling** agents to work safely and check their own work, **verifying** the result without reading every line, and **owning** the outcome ([0:03:09](https://youtu.be/I6V5dmoZplU?t=189)). Reading all the code makes you the bottleneck. Build better ways to verify instead ([0:09:04](https://youtu.be/I6V5dmoZplU?t=544)).

## Workflow: before, during and after a big agent task

**1. Judgment: decide before delegating** ([0:01:02](https://youtu.be/I6V5dmoZplU?t=62))
1. Write down what you will *not* build. AI makes every extra feature or mode cheap, and that adds no value for users.
2. List the project's constraints: cost (for example, "scale to near zero at launch, scale up later"), reliability, performance, security ([0:04:11](https://youtu.be/I6V5dmoZplU?t=251)).
3. Name the trade-offs and pick one side of each. Chasing everything stacks complexity into "a monster" that's hard to maintain ([0:05:11](https://youtu.be/I6V5dmoZplU?t=311)).
4. Set a dependency budget: few dependencies rather than zero, because of supply-chain risk. He picks libraries that pull in nothing, for example Effect, which he says has zero dependencies (per the video, 2026) ([0:06:13](https://youtu.be/I6V5dmoZplU?t=373)).
5. Discuss ideas and constraints with the AI, but make the final call yourself.

**2. Orchestration: set agents up to work**
1. Run one root orchestrator session per project (or a few). Tell it that it is an orchestrator, have it write down rules for spinning up sub-agents, then give it large tasks rather than tiny ones you micromanage ([0:02:04](https://youtu.be/I6V5dmoZplU?t=124), [0:07:15](https://youtu.be/I6V5dmoZplU?t=435)).
2. Define the task and the expected outcome clearly. How large a task can be depends on the model; find it by experience ([0:03:09](https://youtu.be/I6V5dmoZplU?t=189)).
3. Give agents rules and the right skills, "but not too many" ([0:06:13](https://youtu.be/I6V5dmoZplU?t=373)).
4. Let agents roam freely inside an isolated environment, with no access to production databases ([0:07:15](https://youtu.be/I6V5dmoZplU?t=435)).

**3. Self-verification: agents check their own work** ([0:08:02](https://youtu.be/I6V5dmoZplU?t=482))
1. Agents can run the tests (unit tests and the rest).
2. Agents can open a browser (or run the app) to look at what they built.
3. Strict linting is enforced, and agents must fix lint errors by changing the code, **never the lint rules**.

**4. Verification by you: judge without reading every line** ([0:08:02](https://youtu.be/I6V5dmoZplU?t=482))
1. Have every run end with a report or artifact that is generated as deterministically as possible (from tool output, not written up by the agent) so you can trust it.
2. Include whatever lets you decide: diagrams, tables, screenshots, videos of the change ([0:09:04](https://youtu.be/I6V5dmoZplU?t=544)).
3. Use the reports to keep an up-to-date picture of the codebase's structure and to check that problems are solved the way you want.
4. Iterate, push back, and don't accept output blindly ([0:10:07](https://youtu.be/I6V5dmoZplU?t=607)). Keep tuning which reports you ask for.

**5. Ownership: after it ships** ([0:11:10](https://youtu.be/I6V5dmoZplU?t=670))
- If it breaks, it's your fault. "Nobody cares if AI messed something up."
- You must be able to explain and defend the work. Don't be a "meat proxy" who just passes agent output along ([0:12:12](https://youtu.be/I6V5dmoZplU?t=732)).

## Quick checks
| Look for | Why |
|---|---|
| Feature list with no "won't build" section | Judgment was skipped; scope will sprawl |
| Agent edited lint config, test thresholds or disabled rules | Breaks self-verification; revert and make it fix the code |
| Agent has prod credentials or DB access | Not isolated; it can delete things |
| Run summary is free prose written by the agent | Not trustworthy; ask for generated artifacts (test output, diffs, screenshots, diagrams) |
| You can't explain how the change works | You don't own it yet; ask for a structure report or read the key parts |
| Many new dependencies in the diff | Over the dependency budget; supply-chain risk |
| Dozens of skills/rules loaded for one agent | "Not too many"; trim to what the task needs |

## Rules of thumb (per Schwarzmüller)
- Knowing what *not* to build matters more now than before AI.
- Give orchestrators big tasks; don't watch agents type.
- Enforcing the verification setup is your job: "fix the code, not the rules" is a hard rule.
- Broad expertise beats very deep expertise in one area for most developers; AI-assisted learning makes breadth cheaper. Go deep on working with agents itself ([0:13:12](https://youtu.be/I6V5dmoZplU?t=792), [0:14:17](https://youtu.be/I6V5dmoZplU?t=857)).
- Build side projects, try new models and push agents to their limits. Curiosity is how the other skills get practiced ([0:15:20](https://youtu.be/I6V5dmoZplU?t=920), [0:16:04](https://youtu.be/I6V5dmoZplU?t=964)).

## Known gaps
- Opinion talk: no orchestrator prompt, no example rules file, no named reporting tools, and no task-size guidance beyond "depends on the model".
- "Deterministically generated report" is his goal; how to build one (for example a script that collects test results, diff stats and screenshots) is not shown.
- The talk's slide with the skills list is not in the transcript.

## Sources
| Video | Channel | Date | Used for |
|---|---|---|---|
| [What I would focus on](https://www.youtube.com/watch?v=I6V5dmoZplU) | Maximilian Schwarzmüller | 2026-10-28 | All content: the five skills, orchestrator setup, self-verification, deterministic reports, ownership |

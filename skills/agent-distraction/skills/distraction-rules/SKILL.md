---
name: distraction-rules
description: Sets up a project so coding agents stay on the task they were given instead of acting on stale CLAUDE.md lines, old specs, fixed-bug TODOs and outdated memory notes, using Google's agent distraction findings - four CLAUDE.md rules, ticket status tags, and a fresh-session habit. Use when an agent builds something you dropped, "fixes" things nobody asked about, follows CLAUDE.md over the actual code, re-does a finished plan after compaction, or when writing or reviewing a CLAUDE.md, AGENTS.md or specs folder.
---

# Distraction rules

Distilled from "Google Just Released Something To Fix Claude Code's Biggest Problem" (AI LABS, 2026-11-17) and Google's "Agent Distraction" post (2026-11-06). To clean up stale files that already exist, use the `sweep` skill.

## Core mental model
A person skims past an old note. An agent treats everything it reads while planning as something to act on ([0:01:46](https://youtu.be/JhZB3spnuIY?t=106)). Google calls the result **side quests**. They happen in two ways:
- **Obsolete detour**: the agent chases something already fixed or dropped (41% of Google's unprompted detours).
- **Eager agent / scope creep**: the agent starts on an open issue nobody asked about (57%) ([0:02:05](https://youtu.be/JhZB3spnuIY?t=125)).

The task still gets finished, so you never notice the cost: 70% more steps, 77% more tokens, 105% more wait time per session (Google's regression, p<0.0001). More tools and skills give the agent more room for side quests.

## Where stale context comes from
| Source | Why it misleads |
|---|---|
| CLAUDE.md / AGENTS.md | Loaded every session and taken as true. When it disagrees with the app, the agent follows the file ("9 of 10 times" per the video) ([0:04:01](https://youtu.be/JhZB3spnuIY?t=241)) |
| Bloated agent-written CLAUDE.md | Read in full every session. Generated context files cost >20% more with no gain (Gloaguen et al., ETH Zurich, arXiv 2602.11988) |
| Contradicting rules | The agent picks one rule without asking ([0:05:02](https://youtu.be/JhZB3spnuIY?t=302)) |
| Memory notes, second brains | Never expire. A second brain has no code to check notes against |
| Specs / requirement docs | Requirements change mid-build and the spec doesn't ([0:06:11](https://youtu.be/JhZB3spnuIY?t=371)) |
| `TODO(bug/...)` / FIXME comments | Bug fixed long ago, comment still there (Google's measured case) |
| Long sessions | Failed attempts stay in context. Chroma: all 18 models tested got less reliable as context grew. Finished plans come back after compaction |

## Workflow: set up a project
1. **Status tag on every ticket/spec**: `Status: completed | in progress | not started | dropped`. Add `dropped` with a one-line reason: without it, "in the plan but not in the code" is ambiguous ([0:09:18](https://youtu.be/JhZB3spnuIY?t=558)).
2. **Add the four rules** below to CLAUDE.md (or AGENTS.md), adapted to the project's paths.
3. **Trim CLAUDE.md**: delete what the agent can find from the code itself. Remove any rule that contradicts another one.
4. **Habit**: one fresh session per task, including between planning and building ([0:10:20](https://youtu.be/JhZB3spnuIY?t=620)). Hand over through the spec file, not chat history.
5. Rules stop new rot only. Run `sweep` once for what's already stale ([0:11:21](https://youtu.be/JhZB3spnuIY?t=681)).

## The four rules (paste, then adapt)
```
## Source of truth
- The code is the source of truth. If CLAUDE.md, a spec, a memory note or a comment disagrees with the code, trust the code and tell me about the mismatch. Don't silently "fix" either side.
- Exception: for a ticket marked `in progress`, follow the plan over the half-built code.
- `dropped` tickets are decisions, not missing work. Never build them.

## Scope
- Do only what I asked. Leave anything I haven't asked about alone, including TODOs, open bugs and nearby code you think is wrong. Mention it in one line at the end instead.

## New requests vs existing plans
- Before building a feature that isn't an existing ticket, compare it with the plans in specs/. If it overlaps or conflicts with one, tell me and ask before building, so the plan can be updated first.
```
Why each rule (per the video): the source-of-truth rule turned 9/10 wrong into 9/10 right. With the scope line, Claude Code "never did extra work" in their test. The new-request rule catches requirement changes, which is where plans first fall out of date ([0:10:20](https://youtu.be/JhZB3spnuIY?t=620)).

## Quick checks (reviewing a CLAUDE.md or specs folder)
| Look for | Fix |
|---|---|
| Names or paths that no longer exist in the code | Update or delete, or run `sweep` |
| Tickets with no status, or built features still `not started` | Add or correct the tag |
| Two rules that disagree | Keep one |
| Lines the agent could get from the code (stack, file tree) | Delete |
| Memory entries older than the code they describe | Re-verify or delete |

## Known gaps
- The "9 of 10" study and the "never did extra work" test are the video's own claims. I couldn't find the study, so treat them as "per the video".
- The video showed its CLAUDE.md wording only on screen. The rules above are written from its description.

## Sources
| Video | Channel | Date | Used for |
|---|---|---|---|
| [Google Just Released Something To Fix Claude Code's Biggest Problem](https://www.youtube.com/watch?v=JhZB3spnuIY) | AI LABS | 2026-11-17 | Distraction sources, the four rules, status tags, fresh-session habit |

Also checked: [Google Developers Blog, "Agent Distraction"](https://developers.googleblog.com/agent-distraction/) (2026-11-06) for the exact numbers. [arXiv 2602.11988](https://arxiv.org/abs/2602.11988) for the context-file cost.

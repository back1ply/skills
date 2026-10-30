---
name: saas-ai-moats
description: Scores how well a SaaS business can survive AI, using Rob Walling's 10 AI attacks (6 supply-side, 4 demand-side) and the 8 moats that still work when code is nearly free (trusted by buyers, system of record, allowed to act, output nobody checks, official approval, everyone's in it, learning loop, hard to keep running). Use when judging a SaaS idea or existing product's defensibility, doing acquisition or due-diligence review of a SaaS, planning roadmap or pricing against AI risk, or when the user says "SaaS moat", "SaaSpocalypse", "will AI kill my SaaS", "vibe-coded competitor", "defensibility", "seat-based pricing risk", or "should I agentify".
---

# SaaS moats in the age of AI

Distilled from "The Only SaaS Moats Left in 2026" (Rob Walling, MicroConf talk, co-written with Anurag (sp?) of Discretion Capital). Per-attack detail in [references/attacks.md](references/attacks.md); per-moat examples and moves in [references/moats.md](references/moats.md).

## Core mental model

Assume code costs close to zero. It won't really get there, but it's heading that way, like disk space and bandwidth did. A moat counts only if a competitor with free code still can't copy it ([0:27:03](https://youtu.be/KpILHX2D-AA?t=1623)). Everyone gets AI: your customers, your competitors, open-source maintainers, agencies and platforms too ([0:03:01](https://youtu.be/KpILHX2D-AA?t=181)). Each moat is a dial from 0 to 100, not a switch. The question is how to go from 10 to 30 ([0:19:03](https://youtu.be/KpILHX2D-AA?t=1143)). One or two strong moats means you're doing well ([0:38:09](https://youtu.be/KpILHX2D-AA?t=2289)).

## Workflow: assess a SaaS business

1. **Map the attacks.** Go through the 10 attacks in [references/attacks.md](references/attacks.md) and mark each as high, medium or low exposure. Don't stop at supply-side (clones). Founders often miss the demand-side four: customers going out of business, seats shrinking, the managed thing losing its point, humans leaving the loop ([0:08:01](https://youtu.be/KpILHX2D-AA?t=481)).
2. **Strike the dead moats.** Unique features, clever code, integrations, UX familiarity and data lock-in no longer protect much. Owned traffic and SEO are 50/50 ([0:14:09](https://youtu.be/KpILHX2D-AA?t=849)). Don't count these in the business's favor.
3. **Score the 8 moats from 0 to 100** using the questions below, with evidence for each score (a named partner channel, which data can't be exported, which approvals are held).
4. **Pick one or two moats to move toward**, using the "if you are X, become Y" moves in [references/moats.md](references/moats.md) ([0:37:08](https://youtu.be/KpILHX2D-AA?t=2228)).
5. **Report:** top attack exposures → moat scorecard → recommended moves. Lead with any demand-side attack that has no matching moat.

## Quick checks: the 8 questions

Watch: [0:36:06](https://youtu.be/KpILHX2D-AA?t=2166)

| # | Moat | Ask |
|---|---|---|
| 1 | Buyers know and trust you | Who has built their business or career around recommending or defending you? |
| 2 | You are the system of record | Do you hold the definitive record of the work, or just a view of it? What can't they export, and what breaks downstream if they leave? |
| 3 | You're allowed to act | Does the product take the action (move money, step into the cancel flow), or only recommend it? |
| 4 | They don't check your work | Do customers trust your output enough to never double-check it? |
| 5 | Someone official already said yes | Which approvals, licenses or certifications do you hold that a newcomer has to wait for? |
| 6 | Everyone's already in it | Who has to agree before you can be replaced? Would a competitor have to move everyone at once? |
| 7 | Every customer makes it smarter | Does what happens to one customer make the product better for all the others? (Must pass the 3 gates.) |
| 8 | It's hard to keep running | What do you maintain that you resent maintaining? |

## Rules of thumb

- Customers don't need your 50 features. They need the 3 they use, and that's what they'll vibe-code ([0:04:01](https://youtu.be/KpILHX2D-AA?t=241)).
- Features buy far less time than they used to. Most categories reach feature parity in months ([0:05:02](https://youtu.be/KpILHX2D-AA?t=302)).
- If humans in your customers' businesses are being replaced by agents, agentify the product, or a competitor will sell "your software plus an agent" at several times your price ([0:11:06](https://youtu.be/KpILHX2D-AA?t=666)).
- Serving regulated customers isn't the same as holding an approval yourself ([0:27:03](https://youtu.be/KpILHX2D-AA?t=1623)).
- A learning loop only counts if customers can take their data but not what you learned from it ([0:33:01](https://youtu.be/KpILHX2D-AA?t=1981)).
- Treat the ops burden you hate as a candidate moat, not only as cost: scraping proxies, email deliverability, SMS compliance ([0:35:05](https://youtu.be/KpILHX2D-AA?t=2105)).
- Moats matter even if you never sell. Buyers pay the old multiples only when they believe the business survives 3 to 5 years ([0:17:02](https://youtu.be/KpILHX2D-AA?t=1022)).
- Walling's estimate, not data: 10–20% of SaaS companies will decline or go to zero. That rules out both "all SaaS is dead" and "ignore it" ([0:06:02](https://youtu.be/KpILHX2D-AA?t=362)).

## Known gaps

- The talk's 91 slides, diagrams and scorecard aren't in the transcript. MicroConf offers a field guide and scorecard at https://microconf.com/moats (not reviewed here).
- He says the "evaluate your company" section is a short version of what could be a 4-hour workshop. The Q&A isn't on YouTube.
- This talk covers defense only. The companion talk on offense and learning loops is separate.
- Market figures (HubSpot −21% vs Atlassian +35%, PE doing 70% of acquisitions, exit sizes) are from the video (2026) and weren't verified. Auto-captions garbled the co-author's name.

## Sources

| Video | Channel | Date | Used for |
|---|---|---|---|
| [The Only SaaS Moats Left in 2026](https://www.youtube.com/watch?v=KpILHX2D-AA) | Rob Walling | 2026-10-18 | The 10 attacks, dead classic moats, the 8 moats with examples, evaluation questions and moves |

# impatient-programming

An agent skill that teaches Claude Code (and other coding agents) to work the
[Impatient Programming](https://impatientprogramming.org/) way. IMP is Obie Fernandez's rewrite
of XP's 29 rules for teams that build with coding agents.

With the skill loaded, the agent:

- reads and maintains **the Contract**, the repo's executable list of obligations
- does both halves of **breathe in, breathe out** inside every PR, so no technical debt leaves it
- keeps only tests that earn their place under **mutation testing** (the kill matrix)
- fixes bugs **Contract-first**, and labels PRs honestly (`fix:` only for live production defects, otherwise `refine:`)
- states each PR's **blast radius** so green can merge itself where it's safe
- turns repeated mistakes into **guardrails** and picks guardrail tools for your stack
- writes daily team briefs and follows the weekly showcase rhythm

This is an unofficial community skill. It isn't affiliated with or endorsed by
impatientprogramming.org.

## Install

```
/plugin marketplace add back1ply/skills
/plugin install impatient-programming
```

Or with skills.sh: `npx skills add back1ply/skills` (pick `impatient-programming`).

## What's inside

```
skills/impatient-programming/
├── SKILL.md                 core moves, rule index, which reference to load
└── references/
    ├── rules.md             all 29 rules with reasoning (from the site, CC BY 4.0)
    ├── primer.md            the site's official primer for agents (CC BY 4.0)
    ├── contract.md          writing, checking and regenerating from the Contract
    ├── workflows.md         playbooks: feature start, PR, review gates, bugs, briefs, guardrails
    ├── tools.md             guardrail tool map by category, with live directory links
    ├── background.md        why IMP exists, values, FAQ, case studies, essays (condensed)
    └── sources.md           every page on the site and where it's used
tools/                       maintenance scripts (not used by the skill)
```

## Example prompts

- "Set this repo up the IMP way."
- "Breathe out on this PR before I merge it."
- "Write the Contract for `app/services/billing`."
- "We found a bug in checkout totals. Fix it Contract-first."
- "Run a kill matrix on these tests and tell me which ones to delete."
- "What's this PR's blast radius? Can green merge it?"

## Keeping it current

`tools/refresh.sh` (works from any directory)
re-downloads the rules and primer into `_source/` (gitignored) and regenerates `rules.md` and
`primer.md`. The other reference files are hand-written notes: review the site's changes and edit
them by hand. The current snapshot is from **2026-10-27**. Requires `curl` and `uv`.

## Credits and license

This plugin is **CC BY 4.0** (see [LICENSE](LICENSE)), unlike the rest of this repo (MIT).

- **The 29 rules and the agent primer** are © 2026 Obie Fernandez, from
  [impatientprogramming.org](https://impatientprogramming.org/), licensed
  [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). `rules.md` is reformatted
  from HTML to markdown, and `primer.md` is unchanged. See [NOTICE.md](NOTICE.md).
- **Everything else on the site** (intro, values, FAQ, case studies, tools directory) is
  © Obie Fernandez, and **the essays belong to their authors**. Those pages are not copied
  here; this skill has only its own condensed notes, with links back to each page.
- **This plugin's own material** (SKILL.md, the notes, the scripts) is also released under CC BY 4.0.

Moved here from `back1ply/impatient-programming-skill`.

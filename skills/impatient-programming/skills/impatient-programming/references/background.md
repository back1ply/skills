# Background: why IMP exists, its values, and common objections

Condensed notes written for this skill. The site's own pages are copyrighted by their authors and are not reproduced here. Follow the links for the full arguments.

## Why IMP exists

Source: "eXtreme Programming, Revisited" by Obie Fernandez, <https://impatientprogramming.org/xp-revisited/>

- XP spread around 2000 because it fixed two failures at once: heavyweight up-front design, and having no process at all.
- Obie argues both failures are back with coding agents. AI-written planning documents nobody reads play the part of the old up-front design (the site's word for this is "Confluslop"). Vibe coding plays the part of no process.
- XP's move was to take each good practice and push it to the extreme. IMP does the same with agents, and keeps the rules enforced by machines (mutation gates, executable contracts, merge checks) instead of by belief.
- IMP is aimed at **teams** that adopt a method as a whole. Individuals can borrow parts of it.
- The intro says the technical frontier for craft-minded programmers is now **guardrail engineering**: harnesses, orchestration, evals, knowledge graphs.

Vocabulary: practitioners are **imps**. Agents are jokingly called **clankers**, kept "on a tight leash". The mascot is Huff, an imp who walks a small robot on a leash.

## Values

Source: <https://impatientprogramming.org/values/>

IMP pairs Larry Wall's three programmer virtues with an XP value that keeps each one in check:

- **Impatience, checked by feedback.** Ship fast, release every merge, and let the customer see work this week. Wrong shapes and technical debt get removed at once.
- **Laziness, checked by simplicity.** Spend effort on automated guardrails so no agent repeats a mistake. Prefer convention over configuration. Hand maintenance to agents where it's safe.
- **Hubris, checked by courage and respect.** Build complete, near-perfect work, but don't hand teammates messes (the site calls them "slop grenades").
- XP's five values carry over unchanged: communication, simplicity, feedback, courage, respect.
- The value under all of them is **heart**: people come first. It's always a people problem (Gerald Weinberg).

## Common objections, briefly

Source: FAQ, <https://impatientprogramming.org/faq/>

- **"Isn't this just XP?"** It keeps XP's values but rewrites all 29 rules. Rule 22 (one pair integrates at a time) is retired because merge queues and CI took it over.
- **"Isn't it vibe coding with a name?"** No. Vibe coding is one of the two failures it targets. The rigor comes from builds that fail.
- **"Do we still review code?"** Only as much as the blast radius demands. The long-term aim is automated review for most changes.
- **"Do we still write tests?"** Yes, but each test must earn its place under mutation testing.
- **"Is the Contract a spec?"** It's a spec that lives in the source code and is meant to run.
- **"An agent broke production?"** Roll back, then fix the Contract, then fix the code.
- **"We run Scrum."** IMP replaces the sprint with flow plus a weekly showcase.
- **"When will it ship?"** You get a believable forecast once the unknowns are resolved.
- **"Is quality collapsing under all these small PRs?"** Count production defects labeled `fix:`, not PRs.
- **"Monday morning?"** Write down this week's success criteria, call your shot, and give your agent the primer.

## Case studies

- **Born at ZAR**, <https://impatientprogramming.org/case-studies/born-at-zar/>. Over nine days in September 2026, Obie deleted three components of ZAR's Rails agent orchestration platform (Agora) and had fresh Claude Code agents rebuild them from intent docs, decision records and an executable contract spec, without the old code. Findings across seven experiments: the contract caught more mutants than the old RSpec suite; every gap in the intent showed up as a diverging rebuild and became a new sentence; and writing the Contract exposed a production bug, where an operator's Stop during a reboot was getting lost. That bug was fixed Contract-first. Practical lessons are folded into `contract.md`.
- **exhale in a day**, <https://impatientprogramming.org/case-studies/exhale/>. Obie built the `exhale` Ruby gem, a duplication and complexity gate for the exhale step, in one Claude Code session of under eight hours from first prompt to RubyGems release. The page walks through the human steering (determinism, sweeping the whole codebase, declaring kept duplication in the Contract) and what each check caught, including adversarial review, mutation testing passes and a Codex review. It's a good worked example of the PR lifecycle.

## Essays (responses to the rules)

Each essay belongs to its author. One-line summaries:

- **Mark Ryall, "Keep pairing with humans"** (pushes back on rule 21). Agents took over the navigator's typing and lookup jobs. Human pairing still provides honesty, knowledge spread, mentoring, focus and care. <https://impatientprogramming.org/essays/mark-ryall-keep-pairing-with-humans/>
- **Matthew Canham, "The Playbook and the Contract"** (agrees on rule 6, extends 20, pushes back on 27 and 9). This reply from the author of Atlassian's AI SDLC playbook accepts the missing verification step. It questions automatic green merges and leaving spend unmeasured. <https://impatientprogramming.org/essays/matthew-canham-the-playbook-and-the-contract/>
- **Muhannad Salkini, "Rule 17: What the Contract can't hold"** (extends 17 and 27). The Contract says *what* the software must do, but regeneration also needs to know *how not* to do it. Keep a small, scoped log of rejected approaches. <https://impatientprogramming.org/essays/muhannad-salkini-rule-17-what-the-contract-can-t-hold/>
- **Sebastian Scholl, "Stop Apologizing for Being the Bottleneck"** (pushes back on impatience, extends 3 and 27). Some bottlenecks are deliberate controls, like a dam. Treat review gates as valves to tune, not obstacles to remove. <https://impatientprogramming.org/essays/sebastian-scholl-stop-apologizing-for-being-the-bottleneck/>
- **Stephen Margheim, "Code Is Cheap Now. That's Why It Matters."** (extends 12 and 19, pushes back on 17). Because code is cheap to change, apply each better pattern across the whole codebase at once. Code quality compounds, since every agent reads the codebase before writing. Regenerate rarely. <https://impatientprogramming.org/essays/stephen-margheim-code-is-cheap-now/>

## Influences named by the site

Kent Beck, Ward Cunningham, Ron Jeffries and Don Wells (XP); Larry Wall (the virtues); Gerald Weinberg (people problems); Peter Naur ("Programming as Theory Building"); Ryan Singer (Shape Up's hill chart); Garry Tan ("boil the lake"); Eric Ries (experimentation); C. Northcote Parkinson (work expanding to fill deadlines); Chad Fowler (regenerative software, the deletion test).

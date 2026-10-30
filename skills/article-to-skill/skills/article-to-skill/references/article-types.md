# What to extract, by article type

`catalog.py` guesses a type from the title and URL. Confirm it from `info.md` and the opening section.

## Contents
- Essay / opinion
- Tutorial / how-to
- Postmortem / incident write-up
- Benchmark / comparison
- Reference / docs page
- Interview / Q&A
- Research summary
- List post
- Series and whole blogs

## Essay / opinion
The author argues for a way of working (Fowler, Graham, Yegge style).
- **Extract**: the thesis as one decision rule, named concepts, the conditions under which it applies, and the counter-cases the author concedes.
- **Shape**: core mental model + rules of thumb + "when not to".
- **Skip**: the story used to set up the argument, unless it is the only worked example.

## Tutorial / how-to
Step-by-step instructions to build or configure something.
- **Extract**: the procedure as numbered checkable steps, prerequisites, the gotchas the author hit, and the verification step ("you should now see ...").
- **Shape**: workflow first; commands in code blocks with placeholders for secrets.
- **Check**: versions and CLI flags against current docs; tutorials go stale fastest.
- **Skip**: if it only repeats official docs Claude already knows, say "no skill".

## Postmortem / incident write-up
What broke, why, and what changed afterwards.
- **Extract**: trigger → contributing factors → detection gap → fix, plus each action item turned into a "check for" line.
- **Shape**: detection signals table + prevention checklist. Several postmortems on one theme make a strong skill.

## Benchmark / comparison
Numbers on tools, configs or approaches.
- **Extract**: the setup (hardware, versions, workload), the result table, and the author's "use X when" conclusions. Keep units and dates.
- **Shape**: decision table; mark every number "per the article (<date>)".
- **Watch**: vendor-written benchmarks. Note who wrote it.

## Reference / docs page
API docs, config references, cheat sheets.
- **Extract**: only what is non-obvious: defaults that surprise, option interactions, limits, deprecations.
- **Shape**: `reference` purpose; SKILL.md as an index into references.
- **Prefer**: if the docs are live and versioned, link them and keep the skill thin; it will go stale otherwise.

## Interview / Q&A
- **Extract**: answers that contain a rule, a number or a named practice; attribute each to the speaker.
- **Skip**: small talk and career anecdotes.

## Research summary
A post summarizing a paper or study.
- **Extract**: the claim, the method in one line, effect sizes, and the limits the authors state.
- **Prefer**: the paper itself when it is reachable. Mark claims that come only from the summary.

## List post
"10 ways to ...", "7 mistakes ...".
- **Extract**: only items with a concrete detection signal or fix; merge overlapping ones.
- **Often**: fold into an existing skill rather than making a new one.

## Series and whole blogs
- Use `list_articles.py` (`--mode links` on a series index, `--mode sitemap --match` for archives), then `catalog.py`.
- Group by theme, not by publish date. One skill per theme; a series usually becomes one skill with a reference file per part.
- Newer posts by the same author can revise older ones. Prefer the newer stance and note the change in the reference.

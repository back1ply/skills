# Agentic review loop: the scorecard

Source: Toward a Self-Improving Agentic Code Review Loop (https://www.robinwieruch.de/agentic-code-review-loop/, 2026-10-09). Numbers are per the article; per-skill profiles were deliberately altered by the author to anonymize teammates.

## Contents
- Building the dataset
- The two axes
- Reading the quadrants
- Tracking change
- Where the score lies
- Team totals for reference

## Building the dataset
Read: [Scoring the Reviewers](https://www.robinwieruch.de/agentic-code-review-loop/#scoring-the-reviewers)
1. Scrape every inline review comment on every PR in the period (the author did this ad hoc with an agent). Not from the article: `gh api repos/<owner>/<repo>/pulls/<n>/comments --paginate` returns inline comments, with replies linked by `in_reply_to_id`.
2. Attribute each finding to the review skill that posted it (the model label plus who fired it).
3. A second pass reads the replies under each finding and classifies: **valid** (accepted/fixed), **declined**, **refuted**, or unclear.
4. **First action**: before scoring anything, check the reply rate per author; see "silent fixes" below.

## The two axes
- **Precision** = valid ÷ answered findings. A declined nit costs the same as a wrong finding.
- **Depth** = valid findings a skill lands when several skills reviewed the same change. Only meaningful on PRs with overlapping reviews.
- **Precision alone would put the wrong skill on top**: the skill with a perfect score posted one or two findings per review and missed most of what others caught. Improve that one first.

## Reading the quadrants
The article's five profiles (names invented by the author):

| Profile | Shape | What to change |
|---|---|---|
| Never wrong, almost silent | high precision, low depth | look for more |
| The target | deep and mostly right | keep it |
| Finds the most, a quarter declined | high depth, nit-heavy | stop posting nits |
| Deep, a quarter refuted | high depth, low precision | add a verification step before posting |
| Shallow and imprecise | low on both | rework |

Nobody has to agree on a shared prompt; each developer tunes their own toward the target corner.

## Tracking change
Read: [Watching a Skill Move](https://www.robinwieruch.de/agentic-code-review-loop/#watching-a-skill-move)
- A single scorecard is a snapshot; the next one shows whether a skill change worked. Plot both weeks and look at the direction each skill moved.
- The author's own measured change: told the skill to look harder; typical review went from 4 to 12.5 findings while the valid share of answered findings slipped from 81% to 76%. A trade worth taking.
- Rule of thumb: lean toward depth until precision nears a floor (~70%), then trim the nits, not the depth.

## Where the score lies
Read: [The Silent Fix Problem](https://www.robinwieruch.de/agentic-code-review-loop/#the-silent-fix-problem), [Where the Score Can Lie](https://www.robinwieruch.de/agentic-code-review-loop/#where-the-score-can-lie)
- **Silent fixes**: only about half of findings were answered. A changed line plus a resolved thread isn't a verdict (the code may have changed for another reason), and checking follow-up commits for each costs far more tokens than reading a reply. Reply rates ranged from nearly all to nearly none per author, so a skill's score depends on whose PRs it lands on. Fix: **every AI finding gets a reply**; no fixed vocabulary needed, a model can classify any wording.
- **Goodhart's law**: rated on acceptance, a skill improves its score by posting fewer, safer findings. Depth is the counterweight.
- **The judge is a party**: the author's agent saves work by declining, so the score measures agreement between two agents, not correctness. Missing: an independent judge that runs once at merge, belongs to neither side, and is spot-checked by a human.
- **Blind spot**: what the human review or production caught that no agent flagged. The only real measure of misses; the threads can't provide it.

## Team totals for reference
Read: [Toward a Self-Improving Agentic Code Review Loop](https://www.robinwieruch.de/agentic-code-review-loop/)
- Five personal skills, three weeks: 789 findings; of answered ones, 73% accepted, 8% refuted (4 too unclear to call).
- Overall: the code changed after roughly two of three findings; about one in twenty-five was plain wrong; no human read findings before they went out.
- Copilot baseline: see running-the-loop.md.

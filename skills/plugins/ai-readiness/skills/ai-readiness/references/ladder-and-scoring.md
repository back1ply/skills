# AI readiness: the ladder and the scoring rules

Source: "AI Readiness for Engineering Organizations" (Jurgen De Smet, 2026), pp. 8-9 and 102; howreadyfor.ai/method and /assess (read 2026-11-03); "Twenty Questions, One Honest Number" (Substack, 2026-08-25).

## Contents
- The ladder
- Floor, sum and bands
- Scoring rules
- Reading the result
- Naming drift between versions

## The ladder
Read: field guide p. 8
One question climbs every rung: does the system act on this, or does a human have to choose to?

| Level | Name | Means | Who acts |
|---|---|---|---|
| 1 | Blind | The capability does not exist: no standard, metric or named structure | nobody |
| 2 | Tacit | Happens by individual effort, lives in someone's head, unrepeatable | a person, when they remember |
| 3 | Visible but inert | Written down, computable or diagrammed; nothing acts on it automatically | a person who chooses to |
| 4 | Acted on | The system acts with no human choice: a machine blocks it, a metric gates a decision | the system |
| 5 | Durable | Acted on and self-maintaining: ratchets onto new code, trends and triggers, gets tuned when it cries wolf, its own health watched | the system, over time |

- The line between 3 and 4 is the whole job: "Past this line the system acts. Before it, someone has to remember."
- Level 3 is the most dangerous score because it feels safe. In front of an agent that never opens the wiki it behaves like a 1.
- The staged shape follows Humphrey's Capability Maturity Model (1989), pointed at one question.
- Each chapter's "What good looks like · Level 4" line is the exact bar for a 4.

## Floor, sum and bands
Read: field guide p. 9; method page
- **Floor** = the lowest of the 20 scores. It is the verdict, not the average, weighted mean or percentage.
- **Sum** = the 20 scores added (20-100). Secondary context for breadth. Bands per the method page (2026): 20-40 Hope-based; 41-60 Aware, not enforced; 61-80 Enforcing, with gaps; 81-100 AI-ready.
- A floor needs all 20. Score ten and you know about ten.
- Bands describe the system, not the competence of the people running it.

## Scoring rules
Read: method page; assess page
1. Fix the scope first (one repo or service, one product or value stream, a team's estate, a business unit or org). Wider scope should score lower, because its worst case is inside it. Always print the scope next to the number.
2. Score the worst case in scope, not the typical one.
3. Not knowing is the level: if nobody can produce the answer, score 1.
4. Score what is true today, not what is planned or in flight.
5. Anything that needs a person to choose is 3 at most.
6. Supplier- or vendor-owned code still counts. If nothing enforces the rule there, it is 3 at best.
7. Mid-modernisation: run two assessments (the new platform, the estate it has not replaced) and report the gap.
8. Score alone before scoring together, so the first number said aloud does not anchor everyone.
9. Each level has a tell. A score is something checked, not agreed with. Level 4-5 tells are usually a command you can run; level 1-2 tells are usually a question for two colleagues.

## Reading the result
Read: field guide p. 102
- Close to the code: name your floor, the dimension at 1 or 2 while others look respectable. That is where AI breaks you first.
- Leading the org: count how many of your five lowest dimensions sit at 3. That count is your real exposure.
- Reaching 4 is an engineering act. Holding 5 is discipline: a level-5 gate looks identical to a level-4 one in config, and only its history (the last bypass, who flagged it) shows which it is.

## Naming drift between versions
The Substack scorecard named levels 1-2 "Absent" and "Ad hoc"; the field guide and the site use "Blind" and "Tacit". The site also flags "The wording of these levels changed". Use the live site's names and tells; `scripts/extract_questions.py` pulls them.

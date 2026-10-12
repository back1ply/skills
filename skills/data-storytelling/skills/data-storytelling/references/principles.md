# Principles in depth

Paraphrased from the *SWD + AI Primer* (storytelling with data). Read this when a critique or story plan needs more than the checklist in `SKILL.md`.

## Choosing a graph

- Don't agonize over finding the "perfect" chart. Most datasets can be shown several reasonable ways, and good design can rescue a choice that's only okay.
- A small set of common forms covers most business communication, e.g. simple text (one big number), tables, lines, bars, stacked bars, scatterplots, and slopegraphs. See the SWD chart guide (storytellingwithdata.com/chart-guide) for the full set and when to use each.
- Go beyond the common forms only for a reason:
  - the audience is specialists who already read that format, or
  - an unusual view shows something the common forms can't.
- Weigh the cost: an unfamiliar chart has to be learned before it can be understood.

## Words on graphs

- **Descriptive title** on the graph itself (what it shows).
- **Takeaway title** on the communication around it (slide, page, handout): what it means.
- Title the axes even when it feels redundant. Label the data series directly rather than through a legend.
- Readers usually start at the top-left and scan in a "z" pattern. Put the takeaway and descriptive titles at the top-left so they're read first.
- A takeaway title paired with a graph that visually reinforces it is much more memorable than either one alone.
- To write one, answer *"So what?"*, then cut it down to a short phrase or sentence.

## Finding the takeaway

- List several observations the data supports. For example, a company metric vs. an industry benchmark might give: "benchmark declined steadily while ours fluctuated", "ours fell ~30% then recovered", "ours beat the benchmark for the first time in six years."
- None of these is "right" without context. The audience and goal decide which one leads.
- Decide on the takeaway **before** formatting, because it drives every design choice.
- Stuck? Talk it through with a colleague. Explaining it out loud usually reveals the point, and the right level of detail too.

## Decluttering, worked pattern

A typical cleanup of a grouped bar chart (headcount by region, full-time vs. part-time):

- remove the chart border and gridlines
- remove trailing zeros from the y-axis and redundant data labels
- add an x-axis title; move the chart and axis titles to the top-left
- replace the legend with direct labels on the first bars
- stack the two series instead of placing them side by side (only when that suits the comparison)
- replace two unrelated colors with two shades of one hue

There are other valid choices. The aim is that every remaining element helps the reader.

## Focusing attention, worked pattern

Several years plotted as lines, where the latest year is what matters: make every other year a thin gray line, and make the latest year a thick, dark, directly labeled line. Then the reader's eye goes to the right line without any effort.

Ways to create contrast, roughly in order of strength:
1. Color (used sparingly: one accent plus grays)
2. Line/text weight
3. Size: bigger for important, smaller for supporting
4. Added marks: a few data markers or labels on the key points only
5. Position: important items top-left, supporting details lower-right

## Audience and tension

- First question: **"Who is my audience?"** Analysts tend to present what *they* found interesting (the process, the depth). Audiences engage with what affects *them*.
- Tension = what's at stake. What do they gain by acting, and what do they risk by not acting?
- Translate the metric into what they care about. Example: inventory turnover beating its benchmark matters to executives because it lowers holding costs, frees cash, and improves responsiveness. Falling back below it means storage costs, obsolete stock, and lost competitiveness.

## Story structures

- **Story mountain**: plot → twist → ending. The minimum viable story.
- **Storyboarding**: brainstorm content on sticky notes, cut and arrange it into a structure, get feedback, then turn each note into a takeaway title and a slide. A low-tech step to do before opening any slide tool.
- **Narrative arc**: plot → rising action → climax → falling action → ending. More tension and pacing for longer presentations.
- Other openings: ideal state vs. current reality, start in the middle with the problem, or begin with the ending and work backward.
- Whatever the shape, each point should lead to the next and build toward the decision or discussion you want.

## Recommending action

- Analysts often see themselves as "just providing insights." But whoever did the analysis knows the data best and is well placed to recommend.
- Being bold doesn't mean being forceful. A specific recommendation gives people something to react to, which improves the discussion and makes change more likely.
- Without enough context to recommend a strategy: go gather it, or propose next steps.

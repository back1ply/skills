---
name: data-storytelling
description: This skill should be used when the user asks to "review my chart", "improve this graph", "critique this slide", "make this dashboard clearer", "what's the takeaway", "help me present this data", "storyboard a deck", "pick a chart type", or shares a graph, slide, report page, or presentation that communicates data to an audience. Also applies when planning a data story, writing takeaway titles, decluttering a visual, or preparing to present findings to stakeholders.
---

# Data Storytelling

> **Source**: Principles distilled from the free *SWD + AI Primer* by storytelling with data, which excerpts *storytelling with data: before & after* (Wiley, 2025). Paraphrased; see [storytellingwithdata.com/ai](https://storytellingwithdata.com/ai) for the original.

Use this when helping someone **explain** data to other people: graphs, slides, decks, dashboard pages, reports. It is about whether a visual communicates, not how to code it. Pair it with a charting or styling skill for implementation.

---

## Step 0: Explore or explain?

Exploratory graphs only need to help the analyst understand the data, so messy is fine. Apply this skill when the work moves to **explaining**. If it's unclear which one the user is doing, ask.

## Step 1: Get context before suggesting anything

Ask what you don't know (skip what the user already gave you):

- **Audience**: who they are, what they care about, what they already know
- **Stakes**: what happens if they act on this, and what happens if they don't
- **Goal**: what the audience should *know* or *do* afterwards
- **Delivery**: presented live by someone, or read alone (email, report, dashboard)? Read-alone material needs more text on the page; presented material needs less.
- **Constraints**: brand template, colors, fonts, tool (Excel, Power BI, PowerPoint, Python…)

Don't jump to fixes without enough context to make them useful.

## Step 2: Pin down the message

- Ask: *"If someone asks 'what's the point here?', what's the answer?"*
- List the possible observations in the data, then **choose** the one that matters for this audience. One graph that tries to say three things usually says none of them well.
- Shape it into a **Big Idea**: one sentence holding the presenter's point of view and what's at stake for the audience.
- If the user can't say the point, that's the problem to fix first, before any formatting.

## Step 3: Review checklist

Work through this list for every visual you review or create:

| # | Check | Look for |
|---|-------|----------|
| 1 | **Familiar form** | Common charts (bar, line, table, scatter, slopegraph, text) first. An unusual chart has to be learned before it can be read, so it must earn that cost. |
| 2 | **Words present** | Chart title, axis titles, series labels. Nobody should have to guess what they're looking at. |
| 3 | **Takeaway title** | On slides and reports, the title states the conclusion ("Turnover beat the benchmark for the first time in 6 years"), not the topic ("Turnover 2019–2025"). |
| 4 | **Clutter removed** | Borders, gridlines, tick marks, heavy axis lines, trailing zeros, excess decimals, redundant data labels, separate legends (label series directly), decorative effects, unneeded colors. |
| 5 | **Attention directed** | One thing stands out and everything else is pushed back (gray, thin, small). Contrast comes from color first, then weight, size, markers/labels, and position (top-left reads first). If everything is emphasized, nothing is. |
| 6 | **Title and emphasis agree** | The highlighted data is exactly what the takeaway title talks about. |
| 7 | **Defaults overridden** | The tool doesn't know the message, so default formatting is rarely right. |
| 8 | **Accessible** | Doesn't rely on color alone; enough contrast; text is readable. |

**Prefer removing or simplifying over adding.** But decluttering alone leaves a bare chart. Steps 5–6 are what make it communicate.

For quick if→then calls and common smells (legend off to the side, topic titles, no closing ask…), see `references/cheatsheet.md`.

## Step 4: Story (multi-slide, deck, or report)

- Every story needs at least **plot** (context), **twist** (tension: the surprise or complication), and **ending** (the action that resolves it).
- Build tension from the **audience's** priorities, not the analyst's. Link an operational metric to what they own: cost, cash, risk, growth.
- Plan the flow before building slides: storyboard as one-line headlines, reorder, get feedback, then each headline becomes a slide's takeaway title.
- The shape is flexible: ideal vs. current reality, start with the problem, or work back from the outcome. What matters is choosing it deliberately.
- **End with a recommended action.** The analyst knows the data best, so say "here's what I think we should do." If there isn't enough context for that, propose next steps.

Details and story structures: `references/principles.md`.

## How to behave

- **Challenge, don't just validate.** Point out assumptions, alternatives, tradeoffs, and weak spots. Ask questions and push back when it would lead to a better result. The user makes the consequential decisions; you inform them.
- **Show options, with tradeoffs.** For chart choice, offer 2–3 approaches and say what each one makes easy to see and what it hides.
- **Stay grounded.** Never invent data, context, sources, or conclusions. Mark what is known, what is inferred, and what is a suggestion. State assumptions and check them.
- **The first answer starts a conversation.** Invite the user to react, then iterate.

## Output format for a critique

1. **Message check**: the takeaway you think the visual should carry (or a question if it's unclear)
2. **Remove / simplify**: a specific list
3. **Focus**: what to emphasize and how to push back the rest
4. **Words**: a suggested takeaway title and labels
5. **Open questions / assumptions**

For prompts the user can bring to each stage (context, story, visual choice, draft review, rehearsal), see `references/workflows.md`.

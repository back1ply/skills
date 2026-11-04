---
name: deck-ai-tells
description: Audits and builds slide decks so they don't read as AI-made, fixing first the tells that actually separated 94 AI slides from 100 real slides by consulting firms and banks in a side-by-side comparison. Use when someone asks "does this deck look AI-generated", "make my slides not look AI", "remove the AI slop", reviews slides from Gamma, Copilot, ChatGPT or Claude, or builds a deck with an AI tool.
---

# Deck AI tells

Distilled from "A complete guide to making your decks not AI" (Analyst Academy, November 2026), including Paul Moss's comparison of 94 AI slides with 100 real ones. All 31 tells with their numbers: [references/tells.md](references/tells.md). For the message, story and chart craft behind a deck, pair with `data-storytelling`.

## Core mental model

A deck reads as AI-made because of **familiar defaults**, not because a model touched it. One default on one slide is a choice; the same one on every slide is a tell. The comparison ranks them: five tells did most of the work (80% of AI slides had at least one, against 21% of real slides, per the guide (2026)). Several popular "tells" are things real decks do *more* often than AI, so stripping them makes a deck look less like a real one, not more ([results](https://aa-not-ai-decks.vercel.app/not-ai-decks-guide.md#:~:text=What%20100%20AI%20vs%20100%20real%20slides%20showed)).

## A brand template outranks this skill

If the deck follows a brand or house template, its fixed elements are not tells: a section label in a set position, a fixed edge graphic, the house card style, the brand palette. Leave them as designed and say you left them. Flag only what the tool *added* on top of the template, or a template element used somewhere it was never meant to go.

## Workflow: audit an existing deck

1. Ask for or find the brand template, the audience and the deck's point. Without the template you can't tell a tell from house style.
2. Check every slide for the **strong five** below first. Report each hit with slide number, tell number and the fix.
3. Then the **some-signal** checks, then the **substance** checks (the quick-checks table).
4. Look at the deck as a whole: same layout on every slide (tell 10), ending (tell 15), cover subtitle (tell 21).
5. Read only the titles in order. If they don't carry the argument, that's the first fix.
6. List every placeholder, `[DATA NEEDED: ...]` and unsourced number left. Never fill one with a guess.

## Workflow: build a deck with an AI tool

1. Collect real material first: numbers with their sources, the audience, the one-sentence point. These rules can stop a tool faking substance; they can't supply it.
2. Draft every slide title as a full sentence and check the titles read as a story before building any slide.
3. Build, then run the audit workflow above on the result. Look at every slide at full size: tools miss their own overlaps.

## The strong five (fix these first)

| Tell | AI vs real | Fix |
|---|---|---|
| 19. Anything above the title: ALL-CAPS label, kicker line, breadcrumb, pill | 46% vs 8% | Start with the title. Section markers only if the template has them, in one fixed place. |
| 29. Production slips: overlap, overflow, "Click to add title", "Series 1", title numbers that don't match the chart | 30% vs 7% | Look at every slide at full size; fix each one. |
| 12. Same-shape sentences: colon titles ("Growth: The Path Forward"), em-dash pivots | 40% vs 19% | Write it as you'd say it in the meeting. |
| 30. "Key takeaway" box or filled bottom banner | 18% vs 3% | Put the takeaway in the title; any so-what line is plain body text. |
| 31. Full-height coloured strip down a slide edge | 17% vs 1% | Remove it, unless it's a fixed template element. |

Percentages are per the guide (2026).

## Quick checks

| Look for | Why |
|---|---|
| Hype words (unlock, elevate, delve, leverage, seamless, game-changer) | Some signal (tell 4) |
| Centred body text and paragraphs | Some signal; never seen in the real set (tell 9) |
| "Pivotal", "a testament to", "plays a crucial role" | Some signal (tell 13) |
| Lists of three by habit | Some signal (tell 17) |
| Topic titles ("Q3 Revenue") instead of a full-sentence claim | Weak as a tell, but the biggest quality fix (tell 1) |
| A number with no source you could name, "experts say" | Weak as a tell; one caught fake kills trust (tells 8, 14) |
| Closing on "challenges and future prospects" | End on the decision or the ask (tell 15) |

## Don't over-correct

Real decks used these **more** than the AI tools did: accent colour everywhere, icons in circles, bold lead-ins on bullets, standard fonts, cards with shadows, pills and badges. Don't strip them to look less AI-made. Change them only when they hurt the slide: nothing stands out, or the decoration repeats the word it sits next to. See tells 2, 7, 23, 24, 25 and 27 in the reference.

## Known gaps

- Small, unblinded evidence: one scorer who knew which set each slide came from, AI slides taken from 720p video frames, real slides from published consulting and bank decks. The guide itself calls it "a strong hint, not a lab result".
- The real set had no cover slides and wasn't scored deck by deck, so tells 10, 15 and 21 are unmeasured.
- Judging by the firm types named (consulting firms, banks, research firms), the real set holds no sales or marketing decks, whose norms (labels, cards, badges) can differ.

## Sources

| Article | Author / site | Date | Used for |
|---|---|---|---|
| [A complete guide to making your decks not AI](https://aa-not-ai-decks.vercel.app/not-ai-decks-guide.md) | Analyst Academy, with Paul Moss's 100 vs 100 slide comparison | 2026-11 | All tells, signal ratings and fixes |

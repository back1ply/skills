---
name: deck-ai-tells
description: Audits and builds slide decks so they don't read as AI-made, fixing first the tells that actually separated 94 AI slides from 100 real slides by consulting firms and banks in a side-by-side comparison. Use when someone asks "does this deck look AI-generated", "make my slides not look AI", "remove the AI slop", reviews slides from Gamma, Copilot, ChatGPT or Claude, builds a deck with an AI tool, or wants anti-AI rules to paste into a slide tool.
---

# Deck AI tells

Distilled from "A complete guide to making your decks not AI" (Analyst Academy, November 2026), including Paul Moss's comparison of 94 AI slides with 100 real ones. References, loaded when needed:
- [references/tells.md](references/tells.md): all 31 tells with detect, fix and rates, the method, credits
- [references/checklist.md](references/checklist.md): the 34-check before-you-present list
- [references/tool-prompt.md](references/tool-prompt.md): the 28-rule prompt for another AI slide tool, with how to load it

For the message, story and chart craft behind a deck, pair with `data-storytelling`.

## Core mental model

A deck reads as AI-made because of **familiar defaults**, not because a model touched it, and an audience that spots one stops reading and starts judging. One default on one slide is a choice; the same one on every slide is a tell. The comparison ranks them: five tells did most of the work (80% of AI slides had at least one, against 21% of real slides, per the guide (2026)). Popular tells like accent lines on boxes, stat tiles or three identical boxes barely separated the sets, and some (accent colour, icons in circles, bold keywords) were *more* common in real decks. Those won't give a deck away alone, though the guide still recommends their fixes ([results](https://aa-not-ai-decks.vercel.app/not-ai-decks-guide.md#:~:text=What%20100%20AI%20vs%20100%20real%20slides%20showed)).

## Brand templates

- **From the guide**: a brand template's fixed edge element and title graphic stay exactly as designed (tells 20, 31), and its colours and typeface replace the defaults (tells 3, 23, 26). Section markers are allowed only if built into the template once, small, in sentence case, in the same place every time (tell 19).
- **Judgment call (this skill)**: the template's other fixed elements (logo, its own card, label and badge styles) stand too, including a section-label style that breaks the guide's "small, sentence case" limit (an ALL-CAPS house label, say), as long as it sits in one fixed place and the tool didn't add it. Flag only what the tool *added* on top of the template, or a template element used where it was never meant to go, and say what you left alone.

## Workflow: audit an existing deck

1. Find the brand template, the audience and the deck's point. Without the template you can't tell a tell from house style.
2. Check every slide for the **strong five** below first. Report each hit with slide number, tell number and fix.
3. Run the rest of [checklist.md](checklist.md) (some signal, then weak), using [tells.md](tells.md) for each fix.
4. Deck-level: same layout on every slide (10), the ending (15), the cover subtitle (21).
5. Read only the titles in order. If they don't carry the argument, that's the first fix.
6. List every placeholder, `[DATA NEEDED: ...]`, `[SOURCE NEEDED: ...]` and unsourced number left. Never fill one with a guess.

## Workflow: build a deck

1. Collect real material: numbers with their sources, the audience, the one-sentence point. These rules stop a tool faking substance; they can't supply it.
2. Building in another AI tool (Gamma, Copilot, ChatGPT)? Load [tool-prompt.md](tool-prompt.md) into its instructions before it starts.
3. Draft every title as a full sentence; build slides only once the titles read as a story.
4. Build, then run the audit above. Look at every slide at full size: tools miss their own overlaps.

## The strong five (fix these first)

| Tell | AI vs real | Fix |
|---|---|---|
| 19. Anything above the title: ALL-CAPS label, kicker line, breadcrumb, pill | 46% vs 8% | Start with the title. Section markers only from the template, in one fixed place; the guide adds small and sentence case (see Brand templates for the exception). |
| 29. Production slips: overlap, overflow, "Click to add title", "Series 1", split words, title numbers that don't match | 30% vs 7% | View every slide at full size and fix each one; list leftover placeholders. |
| 12. Same-shape sentences: colon titles ("Growth: The Path Forward"), em-dash pivots | 40% vs 19% | Write it as you'd say it in the meeting; vary sentence length. |
| 30. "Key takeaway" box or filled bottom banner | 18% vs 3% | Takeaway in the title; any so-what line is plain body text. |
| 31. Full-height coloured strip down a slide edge | 17% vs 1% | Remove it, unless it's a fixed template element. |

Percentages are per the guide (2026).

## Judgment calls (this skill, not the guide)

Real decks used these **more** than AI tools did: accent colour everywhere (25), icons in circles (2), bold lead-ins on bullets (7; the bullet wall itself is not on this list), default type such as Inter, Roboto or the system font (23), cards with shadows (24), pills and badges (27). The guide's strict fix for each is in [tells.md](tells.md) and in the tool prompt. When auditing, apply it only where the element hurts the slide (nothing stands out, decoration repeats the word next to it, cards in cards) or the user asks for the strict version; otherwise report it as a style choice, not an AI tell.

## Known gaps

- Small, unblinded evidence: one scorer who knew which set each slide came from, AI slides from 720p video frames, real slides from published decks. The guide calls it "a strong hint, not a lab result".
- No cover slides in the real set and no deck-level scoring, so tells 10, 15 and 21 are unmeasured.
- Our inference, not the guide's: judging by the firm types named (consulting firms, banks, research firms), the real set likely holds no sales or marketing decks, whose norms (labels, cards, badges) can differ.

## Sources

| Article | Author / site | Date | Used for |
|---|---|---|---|
| [A complete guide to making your decks not AI](https://aa-not-ai-decks.vercel.app/not-ai-decks-guide.md) | Analyst Academy, with Paul Moss's 100 vs 100 slide comparison | 2026-11 | All tells, rates, fixes, checklist and tool prompt |

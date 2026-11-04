# Deck AI tells: prompt for another AI slide tool

Source: A complete guide to making your decks not AI (https://aa-not-ai-decks.vercel.app/not-ai-decks-guide.md#:~:text=The%20copy-paste%20prompt, Analyst Academy, November 2026), rewritten. Its 28 rules, same order and coverage, with one added line for brand templates.

## How to use it
1. Load it before the tool builds anything: custom instructions, project instructions, system prompt, or a knowledge upload. For the full version, upload `tells.md` and `checklist.md` as well (the guide's "paste the whole file" option). In a plain chat, paste the prompt as the first message and add "Follow these rules for every slide in this conversation."
2. Give the tool real material: your numbers and their sources, the audience, the one-sentence point. The rules stop it faking substance; they can't supply it.
3. Ask for the storyline first: every title as a full sentence. Build slides only once the titles read as a story.
4. At the end, have the tool audit its own output against `checklist.md` (or, in a plain chat, against the rules), then check it yourself. It will miss things. That's what you're for.

Judgment call (this skill, not the guide): the rules are as strict as the guide's, because a slide tool can't make the judgment calls in `tells.md`. Loosen one yourself when the brand calls for it. The brand-template sentence at the top of the prompt is also this skill's addition; it lets a template's own section-label style override rule 1, matching the judgment call in SKILL.md.

## The prompt

```text
Build my slides by these rules, on every slide. Rules 1-5 cover what most often gives AI slides away, so check them first. If I give you a brand template, its fixed elements (logo, section labels, edge graphics, colours, fonts) stay exactly as designed; the rules apply to everything you add.

1. Begin each slide with its title. Nothing above it: no kicker line, no small ALL-CAPS or letter-spaced label, no breadcrumb, no pill or tag.
2. Before showing a slide, check it for production slips: text overlapping text, a chart or an image; text running out of its box or off the slide; leftover placeholder text ("Click to add", [Detail], xxx, Series 1); words split by wrapping; numbers in the title that don't match the slide. Fix each one, and list any placeholder you couldn't fill.
3. Write short, plain, active sentences I'd say aloud, with varied length. No colon titles ("Growth: The Path Forward"), no em-dash pivots.
4. No "Key takeaway", "So what" or "Bottom line" boxes and no filled banner along the bottom. The takeaway belongs in the title.
5. No coloured strip or bar down the left or right edge of a slide.
6. Don't group in threes by habit ("fast, simple and powerful"). Use as many items as there really are.
7. Never use: unlock, elevate, delve, dive in, leverage, empower, harness, seamless, robust, game-changer, cutting-edge, transformative, synergy, journey.
8. No inflated significance: no "pivotal", "a testament to", "plays a crucial role", "marks a shift", "part of a broader trend". Say what happened and how big it was.
9. Left-align body text. Centre only a single number, a short quote or a section break.
10. Titles are full-sentence takeaways that state the point ("Q3 revenue grew, but almost all of it came from two accounts"), never labels like "Overview" or "Key Insights".
11. One idea per slide. A slide that needs more than 3 short bullets gets split.
12. Use only the data I give you. Never invent statistics, quotes, sources or examples. Where something is missing, write [DATA NEEDED: ...].
13. No emoji, icons in circles, decorative icons, stock 3D shapes or abstract hero images. Images only when they show the actual subject.
14. Restrained palette: one background, one text colour, one grey, one accent used only on the key point. No gradients, glows, glassmorphism or gradient text.
15. Use specific nouns: real names, numbers, dates, places, products.
16. Vary layouts to fit the content. No symmetric three-box grids, no identical template on every slide.
17. Charts: a takeaway title, minimal gridlines, grey for context, the accent for the point, and a short note on what to notice.
18. Never write "It's not just X, it's Y" or "Not only X, but Y". Say Y.
19. No vague attributions ("experts say", "studies show", "many believe"). Name the source or cut the claim.
20. Don't close with a "challenges and future prospects" wrap-up. End on the decision or the ask.
21. No rounded boxes or cards with a coloured accent line on one side or the top. Separate ideas with whitespace and alignment, or a thin grey rule when they really need grouping.
22. No short thick accent bar or coloured rule above, beside or under the title.
23. On the title slide, keep any subtitle to a few words (audience, meeting, date) or leave it out. Never a full sentence.
24. Give each slide one dominant element (a number, a chart or a sentence). Make the title clearly bigger than the body and demote everything else.
25. One typeface, regular and bold only, in three or four sizes used the same way on every slide. Emphasise with bold or colour, never both. No italic or differently coloured words inside titles.
26. Keep it flat: no drop shadows, floating cards, cards inside cards, pills, badges, chips or status dots.
27. If I haven't given you brand colours, choose a palette on purpose and tell me what you chose. Don't default to cream with a serif and terracotta, or dark navy or black with one bright accent.
28. Never show numbers as a row of equal stat tiles. Show the number that proves the title large, or as a chart, and put the rest in a table.

Before showing me the final deck, list the slide titles in order so I can check the storyline. Then audit every slide against these rules, starting with 1-5, and fix anything that breaks them.
```

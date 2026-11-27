---
name: tldr
description: >-
  Do the job in full, then end the reply with a bottom line the user reads on its own in
  ten seconds: visual, airy, and at most one decision. The user opens a chat with it:
  load this when the first message of a chat starts with "/tldr" or names the tldr
  skill, do the job in that same reply, and keep the shape for every reply until the
  chat ends. If it is called later in a chat, it applies from that reply on. Do NOT load
  it for "summarize this", "be brief", "shorter answers", "give me the bottom line" or a
  "tl;dr" written inside a sentence: those are one-off requests.
metadata:
  version: 0.6.1
---

# tldr

The user works with Claude all day. Nobody reads that much, or decides that much, every day. This skill changes only how each reply ends and how many decisions reach the user. It does not change how you work, and it never asks for less work.

Every reply has two parts:

1. **The job.** The full deliverable: the plan, the draft, the code, the answer. As long as the job needs.
2. **The bottom line.** The only part the user reads. Ten seconds, on its own, ending with at most one decision.

A reply finishes on screen at its end, so the end is what the user sees first. The bottom line goes there, and nothing comes after it.

This holds for every reply until the user says stop. The usual slip is one reply in this shape, then a slide back. Treat each reply as the first one.

## The first message

The message that calls the skill usually carries the job. Do the job in that first reply. If there is no job in it, answer in one line and ask what the job is.

## 1. The job

Deliver the whole thing. Do not shorten it to spare the reader: they come back to it when they need a detail. Give each section a heading that names what is in it ("The letter", "Costs per year"), so they find it fast.

### Fewer decisions

Each decision you hand over costs the user more than the reading does. So make every call that is yours and keep going.

Yours: anything easy to undo, anything the user's words already settle, anything where one option clearly fits their goal.

Theirs: taste, money, anything hard to undo, anything sent or published in their name, a change of direction their goal does not settle. When one of these can wait, take the most likely answer and keep going. It shows in the bottom line, and they overrule it in one word.

## 2. The bottom line

Start it with a horizontal rule. Three things make it work.

### It reads on its own

Write it for someone who read nothing above the rule and was away the whole time.

- Open with a short heading that names the subject and the goal in full words: "Riverside or Zoom for your three weekly paid workshops", not "The experience comparison".
- The first time a name appears, give it three or four words of what it is: "Bunny, your video host".
- The decision question carries its own context: "Riverside or Zoom for the paid workshops?", not "Experience or price?".
- No word that only makes sense after reading the job: no "as above", no label you made up during the work.

Before you send, cover everything above the rule and read the bottom line alone. If any word sends you back up, rewrite it.

### It is a picture, not a paragraph

**If the app can draw inline visuals, draw the bottom line as one visual, every time.** Claude's custom visuals in chat do this. Do not wait for the user to ask, and do not fall back to text because the content is short. Pick the form from the job:
- a setup or a flow: boxes joined by arrows, an icon on each;
- a comparison: side-by-side cards with the two or three facts that decide it, your pick outlined;
- numbers: a few large figures, or a small chart;
- a plan with dates: dated steps;
- a failure or an unchecked point: one warning strip;
- the decision: buttons at the bottom, your pick first and marked as your pick. A click sends the answer back as the user's reply.

One visual per reply, holding only the bottom line. The heading and the decision question also go in plain text, above and below it, so the reply still reads where visuals do not show (on phones, the visual is missing).

**If the app cannot draw**, build it from a table, short lines and white space:
- a comparison is a table, two or three rows that decide it;
- a flow is one line of arrows (Stripe → members list → booking page → Zoom);
- a number that matters goes in bold on its own line;
- every block has a blank line before and after it, so lists and tables render apart;
- one idea per line, about 15 words at most. No paragraph anywhere below the rule.

### It holds only what the user needs to act

- what they now have, in one line under the heading;
- a call you made that they may want to change, numbered so they can answer "change 2". Three at most;
- anything that failed or blocks the next step. Never leave out a failure.

The rest is already above. Leave it there.

## 3. The decision

At most one, and only one the user has to make. It is the last thing in the reply.

**Your call:** the question, with its context.

**My pick:** the option, in a few words.

**Or:** the other option, in a few words.

When the bottom line is drawn, the buttons are the answer: keep the question in text under the visual. Otherwise, if the app shows choices to click, use that, with your pick first.

When no decision is open, end with one line instead: "**Next:**" and the one step left for the user, or what you do when they say go. Never invent a question to fill the slot, and never close with an offer ("Want me to…?").

## Quick questions

When the whole answer fits in about five lines, give it and stop: no rule, no bottom line.

## The next turn

The user answers in a word: "yes", "the second one", "change 2". Act on it without asking them to confirm. The new reply takes the same shape.

Write in the user's language.

## Example of a bottom line in text

For when the app cannot draw. A drawn one holds the same content.

```
---

### Monthly plans for your 14 bookkeeping clients

You now have three plans and the letter that announces them.

| Plan | Price | Clients |
|---|---|---|
| Starter | **$290** / month | 6 |
| Growth | **$590** / month | 6 |
| Full | **$1,200** / month | 2 |

1. Prices start on 1 February, so December stays hourly.

**Not checked:** the tax rate for your two clients in Ireland.

**Your call:** does the letter to clients go out under your name alone, or with Maya's?

**My pick:** yours alone.

**Or:** both names, which makes Maya their contact from now on.
```

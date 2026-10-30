# What to extract, by video type

Confirm the type from the transcript; the catalog's guess comes from the title only. Many videos mix types. Then extract each part with its own shape, and keep fixed steps apart from judgment calls.

## Contents
- Quick table
- Course / tutorial / code-along
- Explainer
- Postmortem / incident
- Benchmark / experiment
- Interview / podcast
- Advice / opinion
- Shorts and news clips
- Collections (playlists, channels)

## Quick table

| Type | Usually worth a skill? | Extract | Skill shape |
|---|---|---|---|
| Course / tutorial | Yes, if not beginner material | Procedures, commands, gotchas, "done" checks | Workflow + references |
| Explainer | Often no (Claude knows it) | Only the creator's opinionated decision rules | Decision table, or fold into a collection |
| Postmortem | Yes, high yield | Timeline, root cause, detection gap, fixes | Checklist + incident references |
| Benchmark | Sometimes | Setup, method, results, caveats | Decision rules + dated results table |
| Interview / podcast | Sometimes, thin | Advice and decision rules, not life story | Rules of thumb; fold into a theme |
| Advice / opinion | Sometimes | Criteria and how they're weighed | Decision framework |
| Short / news clip | Rarely alone | One fact or warning | A supporting line in a collection |

## Course / tutorial / code-along

- Keep the order someone would actually follow, not the order the video showed (it may show the result first).
- Keep exact names: commands, flags, settings paths, file names, versions.
- Keep the gotchas ("don't do this", "this used to work differently") and how to tell it worked.
- On-screen code is mostly not in the transcript. If the exact syntax wasn't spoken, write a **Known gap** line instead of inventing plausible code. Check `repo_urls` for the real code.
- "5 tips for X" videos are several processes. Offer each one as its own candidate.

## Explainer

- Test: would Claude get this right without the skill? If yes, skip it.
- Keep what is particular to the creator: their ranking, defaults, "I'd pick X unless Y", their analogies when they are what people search for.
- A series of explainers (for example "System Design 101") works better as one reference skill with a topic index than as one skill per video.

## Postmortem / incident

Extract per incident:
- **What failed** and the user-visible impact.
- **Timeline**: trigger → amplification (retries, saturation, cascading) → detection → mitigation → recovery.
- **Root cause and contributing factors**: name the mechanisms (retry storm, sidecar saturation, auto-scaling on the wrong metric).
- **Detection gap**: why the monitoring didn't catch it sooner.
- **Fixes** in the order they were applied, plus the action items.
- **Transferable check**: "In your system, check …".

The skill: a review checklist built from the transferable checks, plus one reference section per incident. Several postmortems on one theme make a strong collection skill.

## Benchmark / experiment

- **Setup**: hardware, sizes, versions, config. Results mean nothing without it.
- **Method**: load pattern, what was measured, how long.
- **Results**: keep the numbers, but in a table labelled with the video date and "per the video". They depend on the hardware and go stale, so this type may keep dates in the body.
- **Caveats**: what the creator says limits the result, plus obvious ones they didn't mention.
- **Decision rule**: what the result should change ("for N users on a small server, prefer …").

## Interview / podcast

- Auto-captions have no speaker labels. Name a speaker only when context makes it certain (the host introduces a question, the guest describes "my company"). Otherwise write the advice without naming anyone.
- Extract advice, criteria, and named practices. Drop biography, small talk, and plugs.
- Chapter titles help a lot here: skip chapters like "Where to find …" and sponsor chapters.
- An interview usually yields a few rules of thumb. Fold it into a theme skill rather than giving it its own skill, unless it's dense.

## Advice / opinion

- Write a decision framework: the criteria, how they're weighed, and the branches ("if X, do A; if Y, do B").
- Drop anecdotes unless one is the example that makes the rule clear.
- Mark strong opinions as the creator's view ("per <channel>"), not as fact.

## Shorts and news clips

- One Short is too thin for a skill. Use it as a supporting line or "recent example" inside a theme skill, with its date.
- News ("X got hacked") goes stale fast. Verify against a primary source before keeping it.

**Shorts batch** (the user wants Shorts as the main source, for example a channel's tips):
1. `list_videos.py "<channel>/shorts" --limit 50`, then fetch and `catalog.py`. Shorts are 100-500 words each, so 50 cost about 15-30K tokens.
2. Read them straight from `data/raw` with `jq -r '.title, (.segments | map(.[1]) | join(" "))'`. There is no need to split them.
3. Group by topic. Drop jokes, reactions and teasers for long videos.
4. Write one skill per topic: rules of thumb or a quick-check table. Each line cites its Short (`youtube.com/shorts/<id>`) in a Sources table.
5. Each line is one creator's quick claim. Mark numbers and hot takes "per <channel>", and check anything you'd act on.

## Collections (playlists, channels)

- Group by theme, not by upload order. A channel usually splits into 2-4 themes (for this kind of channel: incidents, performance, system design, career).
- Build one skill per theme: create it from the strongest video, then add the rest with *Update / fold-in mode*.
- SKILL.md keeps a source table (video, date, what it added) and a topic index pointing into `references/`.

# Prompt Quality Scorecard & Worksheet

Tools for evaluating and refining prompts.

## Contents

- Prompt Quality Scorecard
  - Scoring Guide
- Prompt Refinement Worksheet
- Quick Diagnostic Checklist
- Testing Tips

## Prompt Quality Scorecard

Rate each item 1-5. Use to evaluate prompt strength before sending.

| # | Question                                                 | Score (1-5) |
| - | -------------------------------------------------------- | ----------- |
| 1 | Is the task clearly defined?                             | ___         |
| 2 | Did I assign a clear role or persona?                    | ___         |
| 3 | Did I provide the right context or background?           | ___         |
| 4 | Did I specify a desired output format?                   | ___         |
| 5 | Did I include tone, length, or constraint instructions?  | ___         |
| 6 | If applicable, did I request reasoning/step-by-step?     | ___         |
| 7 | Is the prompt clear and free of ambiguity?               | ___         |
|   | **TOTAL**                                                | ___/35      |

### Scoring Guide

| Score    | Interpretation                                  |
| -------- | ----------------------------------------------- |
| 30-35    | Strong, high-confidence prompt                  |
| 20-29    | Decent, may benefit from revisions              |
| Below 20 | Likely to produce inconsistent/unclear outputs  |

---

## Prompt Refinement Worksheet

Use this template to document and improve important prompts over time.

```text
PROMPT NAME: ________________________________

GOAL: ________________________________

MODEL: [ ] ChatGPT-4  [ ] Claude  [ ] Gemini  [ ] Other: ____

TEMPERATURE: ____  (0-0.3 factual, 0.7-1.0 creative)

OUTPUT FORMAT: [ ] JSON  [ ] Table  [ ] Bullets  [ ] Paragraph  [ ] Other: ____

---

INITIAL PROMPT:
________________________________________________
________________________________________________
________________________________________________

---

OUTPUT SAMPLE:
________________________________________________
________________________________________________

---

WHAT WORKED:
________________________________________________

WHAT NEEDS REVISION:
________________________________________________

---

FINAL VERSION:
________________________________________________
________________________________________________
________________________________________________

---

RESULT RATING: [ ] Strong  [ ] Okay  [ ] Needs Work
```

---

## Quick Diagnostic Checklist

When output is poor, check:

1. **Am I being too vague?**
   → Add specifics about task and expectations

2. **Did I include a role?**
   → Add "You are a..." to set tone and mindset

3. **Is the input complete?**
   → Include all necessary info for model to reason

4. **Have I requested a format?**
   → Specify bullets, paragraph, JSON, etc.

5. **Am I asking for reasoning?**
   → Add "think step by step" or "explain your logic"

6. **Is the task too complex?**
   → Split into multiple focused steps

---

## Testing Tips

- Change **one variable at a time** (role, tone, format)
- Compare outputs using **different models** with same prompt
- Keep a **prompt library** to reuse and adapt
- If prompt fails, isolate why: unclear instruction? missing input? poor format?

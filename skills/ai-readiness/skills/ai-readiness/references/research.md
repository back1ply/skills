# AI readiness: what the cited research does and does not show

Source: a check of all 40 citations on howreadyfor.ai/assess (2026-11-03): each source looked up, read in full where open (8 of 39 only as abstract or secondary summary), and graded against how the page frames its question. Use this before quoting a paper in a readiness report.

## Contents
- Bottom line
- Per-dimension grades
- Citation errors on the page
- How to cite

## Bottom line
- All 40 citations exist (39 distinct; Lehman 1980 appears twice).
- No source tests the 1-5 ladder. The method page says so itself: the levels are "observed" in client engagements; the research supports why a dimension matters.
- Most sources predate AI coding agents; the agent framing is the author's extrapolation.
- Strongest support: test meaningfulness (6), security assumptions (15), guardrails (17a), dependency hygiene (19a), release discipline (20b).

## Per-dimension grades
| # | Dimension | Grade | Note |
|---|---|---|---|
| 1 | Repository structure | Weak | RepoCod is a model benchmark; it does not vary repo structure. Zhang et al.: about a quarter of hallucinations are project-context conflicts |
| 2 | Cognitive load | Partial | He et al. (MSR 2026): Cursor adoption raised cognitive complexity about 42% persistently; project level, not per module |
| 3 | Domain language | Weak | Fakhoury: lexical inconsistency raises human cognitive load. Aghajani's API study may report no effect (full text not read) |
| 4 | Semantic drift | Weak | Lehman's second law; the name-inconsistency detector paper shows automated detection is poor on realistic data |
| 5 | CI reliability | Partial | Reruns of passing jobs hide silent failures (11% rerun); Gruber and Fraser survey supports "rerun is the reflex" |
| 6 | Test meaningfulness | Strong | Inozemtseva and Holmes: coverage is not effectiveness; LLM oracles tend to encode actual, not expected, behaviour |
| 7 | Change absorption | Weak | Relative churn predicts defects, but churn is not revert rate; absorptive capacity is a 1990 management paper |
| 8 | Technical debt | Weak | METR found AI slowed experienced developers 19% but no PR-quality drop; GitClear is a vendor report |
| 9 | Trunk-based | Weak | Conflicts double bug likelihood; no source measures branch age |
| 10 | Velocity and the constraint | Principle | Reinertsen (book): queues explode near full utilisation |
| 11 | Organizational design | Partial | Mirroring hypothesis and Vista org metrics; neither studies handoff queues |
| 12 | Code ownership and review | Partial | Reviewers without expertise relate to post-release defects (Qt, OpenStack) |
| 13 | Decision memory | Partial | Turnover loses design rationale (interviews, 27 people); Storey's intent-debt essay |
| 14 | Requirements quality | Partial | ClarEval: about 89% vs 9% pass on clarified vs ambiguous tasks; agents rarely ask |
| 15 | Security assumptions | Strong | AI-assisted users wrote less secure code and felt more confident; about 40% of Copilot outputs vulnerable |
| 16 | Documentation integrity | Weak | Library-API docs and comment inconsistency, not executable setup docs |
| 17 | Guardrails vs agreements | Strong / unrelated | Sadowski (Google): checks as build errors get fixed, warnings get ignored. The MIT News item is unrelated |
| 18 | Architecture in CI | Thin | A 15-sample preprint and a smell case study that never enforces |
| 19 | Dependency hygiene | Strong | About 20% of LLM-recommended packages do not exist, and names repeat |
| 20 | Release discipline | Partial | LLMs emit deprecated APIs 25-37% of the time; Lehman's first law |

Figures are as the sources report them, checked by the reviewing agents, not re-derived.

## Citation errors on the page
- Q1: RepoCod is by Liang, Hu, Jiang and Tan (ACL 2025), not "Luo et al."; the title is "Can Language Models Replace Programmers for Coding? REPOCOD Says 'Not Yet'".
- Q9: the merge-conflict paper is by Brindescu, Ahmed, Jensen and Sarma (Empirical Software Engineering, 2020), not Kasi and Sarma. The field guide's reference list repeats the misattribution.
- Q5: the build-reruns paper is from 2025, not 2024.
- Q3: both titles are paraphrased; the "Distinguished Paper" claim could not be confirmed.
- Q17: cites a news article; its underlying paper (Gu et al., 2025) is a position paper not about guardrails.

## How to cite
Say "the research supports that X matters" and name the strongest source; never cite a paper as evidence for a level or a tell.

# Report template

Write the report as `$OUT/report.md` and show the top of it in chat. Keep it scannable.

```markdown
# Code quality report: <project> (<language>)

<N> classes/modules, <M> methods, <P> packages, <LOC> lines. Tools: <list + versions>.
Thresholds: Designite defaults (see catalog). Findings marked *judged* were decided by reading code, not by a tool.

## Top priorities
1. **<Smell> in `<Class>`** (<file>:<line>): <cause in one line>. Fix: <refactoring>.
   (Pick 5-10. Rank by impact: architecture > design > implementation; prefer hotspots with
   several smells, high fan-in, or recent churn from `git log --since=6.months --name-only`.)

## Architecture
| Smell | Component(s) | Cause | Fix |

## Design
| Smell | Class | Cause | Fix | Source |        <- Source = tool rule / threshold / judged

## Implementation (grouped)
| Smell | Count | Worst examples (file:line) |

## Testability / Test (or ML for Python)
| Smell | Where | Cause |

## Metrics snapshot
Top 10 by WMC and by method CC; packages/namespaces by size and instability.

## Not checked / caveats
Tools that failed or were skipped, approximations that matter for this codebase.
```

Rules:
- Every finding names a location and a cause with the actual numbers ("NOPM 38 >= 20"), the way Designite's cause column does.
- Group repetitive implementation smells (Magic Number, Long Statement); list a few examples, not hundreds.
- Drop false positives after checking the code, and say how many were dropped and why.
- Suggest fixes only; do not edit code unless the user asks.

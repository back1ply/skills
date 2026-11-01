# designite-skills

Three agent skills that reproduce what the [Designite](https://www.designite-tools.com) tools report,
without Designite: open-source tools collect the facts, and the agent applies Designite's published
rules and thresholds, judges the smells no tool covers, and writes a report with causes and fixes.

| Skill | Mirrors | Tools |
|---|---|---|
| `designite-java` | DesigniteJava | CK, PMD 7, TSDetect, ripgrep, DuckDB |
| `designite-csharp` | Designite (C#) | lizard, .NET analyzers (injected), PMD CPD, ripgrep, DuckDB |
| `designite-python` | DPy | radon, lizard, pydeps, ruff, pylint, dslinter (optional), ripgrep, DuckDB |

Each skill has `SKILL.md` (workflow), `references/catalog.md` (every smell, its rule, the source of
the threshold, how it is detected), `references/tools.md` (exact commands, verified), and `assets/`
(PMD ruleset, MSBuild injection files, DuckDB queries).

## Install

```
/plugin marketplace add back1ply/skills
/plugin install designite-skills
```

Or with skills.sh: `npx skills add back1ply/skills` (pick the `designite-*` skills).

Tools download to `$DESIGNITE_TOOLS` (default `~/.designite-tools`) on first use. Python tools run
through `uvx`, so nothing is installed into the analyzed project. Output goes to `<repo>/.designite/`.

## How faithful is it?

- Thresholds come from DesigniteJava's source (`ThresholdsDTO.java`), the DPy paper (MSR 2025) and
  Designite's architecture-smell blog posts; each catalog row says which.
- Tools define some metrics differently (CC with `&&`/`||`, source-line LOC, CK's DIT counting
  `Object`, Henderson-Sellers LCOM); `tools.md` lists every mismatch.
- Smells with no published rule (Designite Professional features such as testability smells,
  Feature Envy) use rules chosen here, marked `approx`.

## Tested on

DesigniteJava's own source (Java), codespell (Python, one of the DPy paper's validation repos),
MediatR (C#, static steps; the build step was tested on the sample project in `dev/samples`).

## Disclaimer

Not affiliated with, endorsed by, or a replacement for Designite. "Designite", "DesigniteJava" and
"DPy" are products of Designite Tools. These skills approximate their analyses with other tools and
will not reproduce their exact results. For exact output, use the real tools: https://www.designite-tools.com

## License

MIT. The third-party tools the skills download keep their own licenses (CK Apache-2.0, PMD BSD-style,
TSDetect GPL-3.0, dslinter GPL-3.0, lizard MIT-style, radon MIT, pydeps BSD-2, pylint GPL-2.0).

Moved here from `back1ply/designite-skills`.

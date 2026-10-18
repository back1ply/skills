# Skills

> Personal AI agent skill toolkit — 11 independently installable plugins.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Agent Skills](https://img.shields.io/badge/Agent_Skills-Open_Standard-blue.svg)](https://agentskills.io)
[![Claude Code](https://img.shields.io/badge/Claude_Code-Compatible-blueviolet.svg)](https://code.claude.com/)

## Install

Two ways to install — the Claude Code plugin marketplace, or skills.sh.

### Claude Code plugin marketplace

Add the marketplace, then install the plugins you want:

```
/plugin marketplace add back1ply/skills

/plugin install writing-dax-measures
/plugin install etl-pipeline-design
/plugin install kpi-checklists
/plugin install skill-finder
/plugin install skill-curator
/plugin install channel-artifact
/plugin install humanitys-last-prompt-engineer
/plugin install improve-system
/plugin install arjancodes-playbook
/plugin install data-storytelling
/plugin install quality-pass
```

### skills.sh

```
npx skills add back1ply/skills
```

Add `-g` to install globally, or `-a claude-code` to target a specific agent.

---

## Skills

| Plugin | Description |
|--------|-------------|
| `writing-dax-measures` | Write, review, and debug DAX measures in Power BI and Analysis Services |
| `etl-pipeline-design` | Design, evaluate, and troubleshoot ETL/ELT data pipeline architectures |
| `kpi-checklists` | Define, align, and implement KPIs from strategy through dashboard go-live |
| `skill-finder` | Discover and activate the right Claude Code skill for any task |
| `skill-curator` | Audit, improve, and maintain Claude Code skill libraries |
| `channel-artifact` | Create shareable Claude Code channel artifacts with live web UIs |
| `humanitys-last-prompt-engineer` | Advanced prompt engineering techniques, role templates, and scoring frameworks |
| `improve-system` | Review your setup, capture learnings, audit for rot, recap sessions |
| `arjancodes-playbook` | Pythonic design patterns, clean architecture, typing/idioms, and testing practices |
| `data-storytelling` | Critique and build graphs, slides, and data presentations around audience, message, and story |
| `quality-pass` | One-command code-quality pass: routes changed files to the best installed review skill, with built-in fallbacks |

---

## Structure

```
skills/
├── .claude-plugin/
│   ├── marketplace.json   ← lists all 11 plugins
│   └── plugin.json        ← flat install fallback
└── skills/
    ├── writing-dax-measures/
    ├── etl-pipeline-design/
    ├── kpi-checklists/
    ├── skill-finder/
    ├── skill-curator/
    ├── channel-artifact/
    ├── humanitys-last-prompt-engineer/
    ├── improve-system/
    ├── arjancodes-playbook/
    ├── data-storytelling/
    └── quality-pass/
```

Each plugin is a self-contained directory with its own `plugin.json` and `skills/` folder.

### quality-pass: works best with

`quality-pass` is a router. It runs on its own with built-in checks, and gets better with these installed:

```
npx skills add amElnagdy/guard-skills -g        # test-guard, clean-code-guard, docs-guard
/plugin install mattpocock-skills@claude-plugins-official   # tdd, codebase-design, improve-codebase-architecture
```

The full list is in its `SKILL.md`. Installed as a plugin, the command is `/quality-pass:quality-pass`; installed with skills.sh, it is `/quality-pass`.

---

## License

MIT — see [LICENSE](LICENSE).

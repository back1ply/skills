# LLM Skills

> Personal AI agent skill toolkit - 10 independently installable plugins.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Agent Skills](https://img.shields.io/badge/Agent_Skills-Open_Standard-blue.svg)](https://agentskills.io)
[![Claude Code](https://img.shields.io/badge/Claude_Code-Compatible-blueviolet.svg)](https://code.claude.com/)

## Install

### Add the marketplace

```
/plugin marketplace add back1ply/LLM-Skills
```

### Install individual plugins

```
/plugin install writing-dax-measures
/plugin install etl-pipeline-design
/plugin install kpi-checklists
/plugin install skill-finder
/plugin install skill-curator
/plugin install improve-system
/plugin install multi-model-review
/plugin install channel-artifact
/plugin install humanitys-last-prompt-engineer
/plugin install xquik-social-automation
```

### Install everything at once

```
/plugin install llm-skills
```

---

## Skills

| Plugin | Description |
|--------|-------------|
| `writing-dax-measures` | Write, review, and debug DAX measures in Power BI and Analysis Services |
| `etl-pipeline-design` | Design, evaluate, and troubleshoot ETL/ELT data pipeline architectures |
| `kpi-checklists` | Define, align, and implement KPIs from strategy through dashboard go-live |
| `skill-finder` | Discover and activate the right Claude Code skill for any task |
| `skill-curator` | Audit, improve, and maintain Claude Code skill libraries |
| `improve-system` | Review Claude Code setups, capture learnings, recap sessions, and audit configuration health |
| `multi-model-review` | Cross-model code review using multiple LLM providers for independent perspectives |
| `channel-artifact` | Create shareable Claude Code channel artifacts with live web UIs |
| `humanitys-last-prompt-engineer` | Advanced prompt engineering techniques, role templates, and scoring frameworks |
| `xquik-social-automation` | Use Xquik for X data extraction, webhook delivery, MCP workflows, and confirmation-gated publishing |

---

## Structure

```
LLM-Skills/
├── .claude-plugin/
│   ├── marketplace.json   ← lists all 10 plugins
│   └── plugin.json        ← flat install fallback
└── skills/
    ├── writing-dax-measures/
    ├── etl-pipeline-design/
    ├── kpi-checklists/
    ├── skill-finder/
    ├── skill-curator/
    ├── improve-system/
    ├── multi-model-review/
    ├── channel-artifact/
    ├── humanitys-last-prompt-engineer/
    └── xquik-social-automation/
```

Each plugin is a self-contained directory with its own `plugin.json` and `skills/` folder.

---

## License

MIT - see [LICENSE](LICENSE).

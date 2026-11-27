# Skills

{{skill_count}} agent skills in {{plugin_count}} plugins, for data work, dbt, code quality, and working with coding agents. Each plugin installs on its own.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Agent Skills](https://img.shields.io/badge/Agent_Skills-Open_Standard-blue.svg)](https://agentskills.io)
[![Claude Code](https://img.shields.io/badge/Claude_Code-Compatible-blueviolet.svg)](https://code.claude.com/)

## Install

**Claude Code:** add the marketplace once, then install any plugin from the [catalog](#catalog) by name:

```
/plugin marketplace add back1ply/skills
/plugin install mcp-security@skills
```

**Any agent ([skills.sh](https://skills.sh)):**

```
npx skills add back1ply/skills
```

Add `-g` to install globally, or `-a claude-code` to target one agent.

**Running a skill:** installed as a plugin, a skill runs as `/<plugin>:<skill>` (for example `/quality-pass:quality-pass`). Installed with skills.sh, it runs as `/<skill>`. The plugin and skill names match except in `arjancodes-playbook` (skill: `design-patterns-pythonic`), `designite-skills` (skills: `designite-java`, `designite-csharp`, `designite-python`), and `agent-distraction` (skills: `distraction-rules`, `sweep`).

## Catalog

{{catalog}}

### quality-pass: works best with

`quality-pass` works alone with built-in checks, and does more with these installed:

```
npx skills add amElnagdy/guard-skills -g                    # test-guard, clean-code-guard, docs-guard
/plugin install mattpocock-skills@claude-plugins-official   # tdd, codebase-design, improve-codebase-architecture
```

The full list is in its `SKILL.md`.

## Sources

Some skills are distilled from talks and articles. The source text is kept in `data/` (never installed) so each skill can be checked against it. That text belongs to its authors, so check their terms before reusing it.

<details>
<summary>Skills made from videos</summary>

Built with `youtube-to-skill`. Transcripts are in `data/raw/<id>.json`. Regenerate this table with `uv run skills/youtube-to-skill/skills/youtube-to-skill/scripts/sources.py --readme README.md --marker video-skills`.

<!-- video-skills:start -->
<!-- video-skills:end -->

</details>

<details>
<summary>Skills made from articles</summary>

Built with `article-to-skill`. Article text is in `data/articles/<id>.json`. Regenerate this table with `uv run skills/article-to-skill/skills/article-to-skill/scripts/sources.py --readme README.md`.

<!-- articles:start -->
<!-- articles:end -->

</details>

## Contributing

Each plugin is a folder under `skills/`. That's why `skills` appears three times in a path like `skills/mcp-security/skills/mcp-security/SKILL.md`:

```
skills/                                  <- this repo (marketplace name: "skills")
├── .claude-plugin/marketplace.json      <- one entry per plugin; what /plugin install reads
├── skills/
│   └── <plugin>/                        <- one installable plugin
│       ├── .claude-plugin/plugin.json   <- name, description, keywords
│       └── skills/                      <- folder name Claude Code requires inside a plugin
│           └── <skill>/
│               ├── SKILL.md             <- what the agent loads
│               ├── references/          <- detail files, loaded on demand
│               └── scripts/             <- helper scripts, where needed
└── data/                                <- source text for the Sources tables; never installed
```

To add a skill: create `skills/<plugin>/` with `plugin.json` and `skills/<name>/SKILL.md`, and add an entry to `.claude-plugin/marketplace.json` with a `description` (what it does and when to use it) and a `category` (`data`, `dbt`, `code-quality`, `agents`, `backend`, `business`, or `skills`). The [catalog](#catalog) is built from those entries. skills.sh ignores the plugin layer and picks up every `SKILL.md`.

`.gitignore` ignores everything by default and lists what gets published, so other files at the repo root stay local.

## License

MIT (see [LICENSE](LICENSE)), except `impatient-programming`, which is CC BY 4.0 (see its [LICENSE](skills/impatient-programming/LICENSE) and [NOTICE](skills/impatient-programming/NOTICE.md)).

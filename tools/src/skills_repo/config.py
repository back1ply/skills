"""Repo-specific settings. Everything that names a path, a URL, or a limit lives here."""

REPO_URL = "https://github.com/back1ply/skills"
MARKETPLACE = ".claude-plugin/marketplace.json"
PLUGINS_DIR = "skills"
PRIVATE_DIRS = frozenset({"plugins"})  # skills/plugins/ holds unpublished, gitignored plugins
README = "README.md"
README_TEMPLATE = "tools/readme_template.md"

# marketplace.json `category` -> README heading, in README order
CATEGORIES = {
    "data": "Data and BI",
    "dbt": "dbt",
    "code-quality": "Code quality and design",
    "agents": "Working with coding agents",
    "backend": "Backend, infrastructure, and security",
    "business": "Business",
    "skills": "Making and managing skills",
}

# Agent Skills spec (agentskills.io/specification)
NAME_PATTERN = r"^[a-z0-9]+(-[a-z0-9]+)*$"
NAME_MAX = 64
DESCRIPTION_MAX = 1024
COMPATIBILITY_MAX = 500
SKILL_LINES_MAX = 500
SPEC_FIELDS = frozenset(
    {"name", "description", "license", "compatibility", "metadata", "allowed-tools"}
)

# spec guidance: keep the SKILL.md body under about 5,000 tokens (estimated as chars / 4)
BODY_TOKENS_MAX = 5000
CHARS_PER_TOKEN = 4

# Characters a reviewer can't see: zero-width space/non-joiner, word joiner and invisible
# operators, soft hyphen, BOM, bidi embeddings/overrides/isolates, and Unicode tag characters
# (used to smuggle hidden text). U+200D (zero-width joiner) is left out: emoji need it.
HIDDEN_CHARS = (
    "[\u200b\u200c\u2060-\u2064\u00ad\ufeff\u202a-\u202e\u2066-\u2069\U000e0000-\U000e007f]"
)
TEXT_SUFFIXES = frozenset(
    {".md", ".py", ".sh", ".ps1", ".json", ".yaml", ".yml", ".toml", ".txt", ".js", ".ts",
     ".html", ".svg", ".sql", ".csv"}
)  # fmt: skip

# Claude Code skills docs: extra frontmatter it reads, and the listing cut-off
CLAUDE_FIELDS = frozenset(
    {
        "when_to_use", "argument-hint", "arguments", "disable-model-invocation",
        "user-invocable", "disallowed-tools", "model", "effort", "context", "agent",
        "background", "hooks", "paths", "shell",
    }
)  # fmt: skip
LISTING_MAX = 1536  # description + when_to_use

# Claude Code refuses plugin names with these prefixes, or equal to these words
RESERVED_PREFIXES = ("claude-", "anthropic-", "anthropics-", "cc-plugin-")
RESERVED_NAMES = frozenset({"claude", "anthropic", "anthropics", "claude-code", "claude-mods"})

# Anthropic skill guidance: reference files over 100 lines open with a table of contents
REFERENCE_LINES_MAX = 100
CONTENTS_WITHIN = 30

# skills.sh CLI used by the discovery rule; its list output format is parsed, so bump deliberately
SKILLS_CLI = "skills@1.9.1"

# Shared CLI rules: agent-friendly-cli is the source, python-cli-packaging the copy
SHARED_SOURCE = "skills/agent-friendly-cli/skills/agent-friendly-cli"
SHARED_COPY = "skills/python-cli-packaging/skills/python-cli-packaging"
# prose that states how many rows are shared: file -> regex with one count group
SHARED_COUNT_CLAIMS = {
    "AGENTS.md": r"copies (\d+) of its checklist rows",
    f"{SHARED_COPY}/references/checklist.md": r"(?m)^\*\*Shared rows:\*\* (\d+) items",
    f"{SHARED_SOURCE}/references/checklist.md": r"(?m)^\*\*Shared with python-cli-packaging:\*\* (\d+) rows",
}

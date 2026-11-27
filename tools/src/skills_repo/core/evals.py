"""Trigger eval cases for `claude plugin eval` (code.claude.com/docs/en/plugin-evals).

Each skill gets two cases in its plugin's evals/ folder:
- trigger-<skill>: a request that should load the skill (tool_used Skill grader);
- no-trigger-<skill>: a near-miss request that must not load it (min 0, max 0, arm both).
Skills with `disable-model-invocation: true` only load when the user names them, so they get
the no-trigger case only. These cases are billed model runs: `just trigger-evals` runs them by
hand; the hook and CI only check their shape (rules EVL001, EVL002).
"""

from __future__ import annotations

from pathlib import Path

EVALS_DIR = "evals"
POSITIVE = "trigger-{skill}"
NEGATIVE = "no-trigger-{skill}"

# prompt.md keys the eval runner accepts; unknown keys fail the run (docs, prompt.md reference)
PROMPT_KEYS = frozenset(
    {"schema_version", "name", "description", "tags", "plugins", "runs", "expected_outcome",
     "model", "max_turns", "timeout_seconds", "allowed_tools", "disallowed_tools",
     "append_system_prompt", "env"}
)  # fmt: skip
GRADER_TYPES = frozenset({"regex", "tool_used", "tool_order", "file_exists", "llm", "baseline"})
TOOL_USED_KEYS = frozenset({"type", "weight", "arm", "tool", "input_match", "min", "max"})

# Neutral on purpose: it keeps runs short without nudging the agent toward loading a skill.
SYSTEM_PROMPT = (
    "This is a short test session. If a skill applies, use it as you normally would. "
    "Keep the reply under 150 words and do not edit files."
)
PROMPT = """---
description: {description}
tags: [trigger, {kind}]
max_turns: 6
timeout_seconds: 180
allowed_tools: [Read, Glob, Grep, Skill]
append_system_prompt: "{system}"
---

{prompt}
"""
SKILL_MATCH = r"""'"skill"\s*:\s*"(?:[\w-]+:)?{skill}"'"""  # verbatim from the docs
FIRED = """---
type: tool_used
tool: Skill
input_match: {match}
---
"""
NOT_FIRED = """---
type: tool_used
tool: Skill
input_match: {match}
min: 0
max: 0
arm: both
---
"""


def model_invocable(frontmatter: dict) -> bool:
    return not frontmatter.get("disable-model-invocation")


def expected_cases(skill: str, frontmatter: dict) -> list[str]:
    cases = [NEGATIVE.format(skill=skill)]
    if model_invocable(frontmatter):
        cases.insert(0, POSITIVE.format(skill=skill))
    return cases


def _write_case(case_dir: Path, prompt: str, grader_name: str, grader: str) -> None:
    (case_dir / "graders").mkdir(parents=True, exist_ok=True)
    (case_dir / "prompt.md").write_text(prompt, encoding="utf-8", newline="\n")
    (case_dir / "graders" / grader_name).write_text(grader, encoding="utf-8", newline="\n")


def write_trigger_cases(
    plugin_dir: Path, skill: str, positive: str | None, negative: str
) -> list[Path]:
    """Write trigger-<skill> (when `positive` is given) and no-trigger-<skill>; return the dirs."""
    evals = plugin_dir / EVALS_DIR
    match = SKILL_MATCH.format(skill=skill)
    written = []
    if positive is not None:
        case = evals / POSITIVE.format(skill=skill)
        description = f"Trigger test. This request should load the {skill} skill."
        text = PROMPT.format(
            description=description, kind="positive", system=SYSTEM_PROMPT, prompt=positive
        )
        _write_case(case, text, "fired.md", FIRED.format(match=match))
        written.append(case)
    case = evals / NEGATIVE.format(skill=skill)
    description = f"Trigger test. This near-miss request must not load the {skill} skill."
    text = PROMPT.format(
        description=description, kind="negative", system=SYSTEM_PROMPT, prompt=negative
    )
    _write_case(case, text, "not-fired.md", NOT_FIRED.format(match=match))
    written.append(case)
    return written

"""Rule registry. A rule is a function (repo) -> iterable of Findings, registered with @rule.

Each rule has an ID (three letters for its family, three digits), a one-line title, and a
`default` flag: default rules run on a plain `repo check`; the others (DSC) run only when
selected with --select, because they need the network.
"""

from __future__ import annotations

import importlib
from collections.abc import Callable, Iterable
from dataclasses import dataclass

from skills_repo.findings import Finding
from skills_repo.model import Repo

RuleFunc = Callable[[Repo], Iterable[Finding]]
FixFunc = Callable[[Repo], None]

# Explicit list, not a folder scan, so the wheel and the tests load the same rules.
MODULES = (
    "skills", "registry", "manifests", "counts", "docs", "references", "evals", "discovery",
)  # fmt: skip
FAMILIES = {
    "SKL": "SKILL.md meets the Agent Skills spec and Claude Code's rules",
    "REG": "plugin folders, plugin.json and marketplace.json agree",
    "MAN": "manifest rules from past fixes",
    "CNT": "counts written in prose match the files",
    "DOC": "generated files are up to date",
    "REF": "reference files are easy to navigate",
    "EVL": "every skill has trigger eval cases that `claude plugin eval` accepts",
    "DSC": "skills.sh finds exactly the published skills",
}


@dataclass(frozen=True)
class Rule:
    id: str
    title: str
    func: RuleFunc
    default: bool
    fix: FixFunc | None = None  # rewrites files so the rule passes; `repo check --fix` runs it

    @property
    def family(self) -> str:
        return self.id[:3]


REGISTRY: dict[str, Rule] = {}


def rule(
    rule_id: str, title: str, *, default: bool = True, fix: FixFunc | None = None
) -> Callable[[RuleFunc], RuleFunc]:
    def register(func: RuleFunc) -> RuleFunc:
        if rule_id in REGISTRY:
            raise ValueError(f"rule {rule_id} is registered twice")
        REGISTRY[rule_id] = Rule(rule_id, title, func, default, fix)
        return func

    return register


def load_all() -> dict[str, Rule]:
    for module in MODULES:
        importlib.import_module(f"skills_repo.rules.{module}")
    return REGISTRY


def select(codes: list[str] | None) -> list[Rule]:
    """Rules whose ID starts with any code (SKL, SKL003); default rules when codes is empty."""
    rules = load_all().values()
    if not codes:
        return [r for r in rules if r.default]
    return [r for r in rules if any(r.id.startswith(c.upper()) for c in codes)]


def run(repo: Repo, rules: list[Rule]) -> list[Finding]:
    return [finding for r in rules for finding in r.func(repo)]

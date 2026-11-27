"""Finding: one problem a rule found, and the formats a list of them is printed in."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from typing import TextIO

from skills_repo import config

ERROR = "error"
NOTE = "note"  # informational; never fails a check
FORMATS = ("text", "json", "github", "sarif")
SARIF_SCHEMA = "https://json.schemastore.org/sarif-2.1.0.json"


@dataclass(frozen=True, order=True)
class Finding:
    path: str  # repo-relative POSIX path of a real file or folder
    rule: str  # rule ID, e.g. SKL003
    message: str
    severity: str = ERROR
    line: int | None = None  # 1-based, when the rule knows it
    subject: str = ""  # what inside the file, e.g. a marketplace entry name

    @property
    def where(self) -> str:
        where = f"{self.path}:{self.line}" if self.line else self.path
        return f"{where} ({self.subject})" if self.subject else where

    def text(self) -> str:
        prefix = "note: " if self.severity == NOTE else ""
        return f"{prefix}{self.where}: {self.rule} {self.message}"

    @property
    def full_message(self) -> str:
        return f"{self.subject}: {self.message}" if self.subject else self.message


def errors(findings: list[Finding]) -> list[Finding]:
    return [f for f in findings if f.severity == ERROR]


def _sorted(findings: list[Finding]) -> list[Finding]:
    return sorted(findings, key=lambda f: (f.severity != NOTE, f.path, f.line or 0, f.rule))


def print_text(findings: list[Finding], ok_line: str, out: TextIO) -> None:
    for finding in _sorted(findings):
        print(finding.text(), file=out)
    failed = errors(findings)
    print(f"{len(failed)} problem(s)" if failed else ok_line, file=out)


def print_json(findings: list[Finding], summary: dict, out: TextIO) -> None:
    payload = {
        "ok": not errors(findings),
        **summary,
        "findings": [asdict(f) for f in _sorted(findings)],
    }
    json.dump(payload, out, indent=2)
    out.write("\n")


def _escape(value: str, *, prop: bool = False) -> str:
    """GitHub workflow-command escaping; properties also escape ':' and ','."""
    value = value.replace("%", "%25").replace("\r", "%0D").replace("\n", "%0A")
    return value.replace(":", "%3A").replace(",", "%2C") if prop else value


def print_github(findings: list[Finding], ok_line: str, out: TextIO) -> None:
    """GitHub Actions annotations: errors and notes show inline on the PR diff."""
    for f in _sorted(findings):
        level = "notice" if f.severity == NOTE else "error"
        props = [f"file={_escape(f.path, prop=True)}", f"title={_escape(f.rule, prop=True)}"]
        if f.line:
            props.insert(1, f"line={f.line}")
        print(f"::{level} {','.join(props)}::{_escape(f.full_message)}", file=out)
    failed = errors(findings)
    print(f"{len(failed)} problem(s)" if failed else ok_line, file=out)


def print_sarif(
    findings: list[Finding], rules: list[tuple[str, str]], version: str, out: TextIO
) -> None:
    """SARIF 2.1.0, for code-scanning tools. `rules` is (id, title) for every rule that ran."""

    def result(f: Finding) -> dict:
        location: dict = {"artifactLocation": {"uri": f.path}}
        if f.line:
            location["region"] = {"startLine": f.line}
        return {
            "ruleId": f.rule,
            "level": "note" if f.severity == NOTE else "error",
            "message": {"text": f.full_message},
            "locations": [{"physicalLocation": location}],
        }

    driver = {
        "name": "skills-repo",
        "version": version,
        "informationUri": config.REPO_URL,
        "rules": [{"id": i, "shortDescription": {"text": t}} for i, t in rules],
    }
    sarif = {
        "$schema": SARIF_SCHEMA,
        "version": "2.1.0",
        "runs": [{"tool": {"driver": driver}, "results": [result(f) for f in _sorted(findings)]}],
    }
    json.dump(sarif, out, indent=2)
    out.write("\n")

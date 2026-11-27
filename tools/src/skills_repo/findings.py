"""Finding: one problem a rule found, and how a list of them is printed."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from typing import TextIO

ERROR = "error"
NOTE = "note"  # informational; never fails a check


@dataclass(frozen=True, order=True)
class Finding:
    path: str  # repo-relative POSIX path, or a pseudo-path like "marketplace.json (name)"
    rule: str  # rule ID, e.g. SKL003
    message: str
    severity: str = ERROR

    def line(self) -> str:
        prefix = "note: " if self.severity == NOTE else ""
        return f"{prefix}{self.path}: {self.rule} {self.message}"


def errors(findings: list[Finding]) -> list[Finding]:
    return [f for f in findings if f.severity == ERROR]


def print_text(findings: list[Finding], ok_line: str, out: TextIO) -> None:
    for finding in sorted(findings, key=lambda f: (f.severity != NOTE, f.path, f.rule)):
        print(finding.line(), file=out)
    failed = errors(findings)
    print(f"{len(failed)} problem(s)" if failed else ok_line, file=out)


def print_json(findings: list[Finding], summary: dict, out: TextIO) -> None:
    payload = {
        "ok": not errors(findings),
        **summary,
        "findings": [asdict(f) for f in sorted(findings)],
    }
    json.dump(payload, out, indent=2)
    out.write("\n")

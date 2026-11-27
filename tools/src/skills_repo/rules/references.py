"""REF: long reference files open with a Contents section.

Anthropic's skill authoring guidance: a reference file over 100 lines gets a table of contents
at the top, so an agent previewing the first lines still sees everything the file covers.
"""

from __future__ import annotations

import re
from collections.abc import Iterator

from skills_repo import config
from skills_repo.findings import Finding
from skills_repo.model import Repo
from skills_repo.rules import rule

CONTENTS = re.compile(r"^#{1,6}\s+(contents|table of contents)\s*$", re.IGNORECASE | re.MULTILINE)


@rule("REF001", "reference files over 100 lines have a Contents section")
def contents_section(repo: Repo) -> Iterator[Finding]:
    for skill in repo.skills:
        for path in skill.references:
            lines = path.read_text(encoding="utf-8").splitlines()
            if len(lines) <= config.REFERENCE_LINES_MAX:
                continue
            if not CONTENTS.search("\n".join(lines[: config.CONTENTS_WITHIN])):
                message = f"{len(lines)} lines and no '## Contents' in the first {config.CONTENTS_WITHIN} lines"
                yield Finding(repo.rel(path), "REF001", message)

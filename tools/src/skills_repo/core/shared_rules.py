"""Shared CLI rules: agent-friendly-cli owns them, python-cli-packaging carries a copy.

For each shared item, the rule text and severity are copied into python-cli-packaging's
checklist (keeping that skill's IDs, modes, Verify cell, and sources), and
scripts/cli_contract.py is copied with item IDs translated. Citations are rewritten so they
still resolve: agent-friendly sources become `afc:S30`, and agent-friendly item IDs become the
Python skill's IDs (or `afc:ID` when there is no match).

Ported verbatim from scripts/sync_shared.py; only the paths became a `root` parameter.
"""

import re
from pathlib import Path

from skills_repo.config import SHARED_COPY, SHARED_SOURCE

# python-cli-packaging ID -> agent-friendly-cli ID, for items that state the same rule.
SHARED = {
    "CLI-02": "CLI-02",
    "CLI-03": "CLI-05",
    "CLI-05": "CLI-06",
    "CLI-06": "CLI-08",
    "CLI-07": "CLI-09",
    "CLI-08": "CLI-03",
    "CLI-09": "CLI-10",
    "CLI-10": "CLI-11",
    "OUT-01": "OUT-01",
    "OUT-02": "EXIT-01",
    "OUT-03": "EXIT-02",
    "OUT-04": "OUT-02",
    "OUT-05": "OUT-03",
    "OUT-06": "OUT-04",
    "OUT-07": "OUT-07",
    "OUT-08": "OUT-06",
    "OUT-09": "OUT-08",
    "OUT-10": "OUT-09",
    "OUT-11": "OUT-10",
    "AGT-01": "AGT-01",
    "AGT-02": "AGT-02",
    "AGT-03": "AGT-05",
    "AGT-04": "AGT-06",
    "AGT-05": "AGT-07",
    "AGT-06": "AGT-08",
    "AGT-07": "AGT-09",
    "AGT-08": "AGT-11",
    "AGT-09": "AGT-12",
    "AGT-10": "ERR-02",
    "AGT-12": "DISC-01",
    "AGT-13": "AGT-15",
    "AGT-14": "AGT-13",
    "AGT-15": "AGT-14",
    "AGT-16": "DISC-04",
    "AGT-17": "AGT-16",
    "ERR-01": "ERR-01",
    "ERR-02": "ERR-03",
    "CFG-01": "CFG-01",
    "CFG-02": "CFG-02",
    "CFG-03": "CFG-03",
    "CFG-04": "CFG-04",
    "CFG-05": "CFG-05",
    "CFG-06": "CFG-06",
    "CFG-07": "CFG-07",
}
TO_PY = {afc: py for py, afc in SHARED.items()}
CELL = re.compile(r"(?<!\\)\|")
ROW = re.compile(r"^\| ([A-Z]+-\d+) \|.*$", re.MULTILINE)
REF = re.compile(
    r"py:(S\d+)"  # a python-cli-packaging source cited from afc
    r"|\bpy ([A-Z]+-\d{2})\b"  # a python-cli-packaging item cited from afc
    r"|(?<![\w:])([SEP]\d{1,2})\b"  # an afc source, experiment, or test run
    r"|\b((?:CLI|OUT|EXIT|AGT|ERR|CFG|DISC|TST)-\d{2})\b"  # an afc item
)


def translate(text):
    def repl(m):
        py_src, py_item, afc_src, afc_item = m.groups()
        if py_src or py_item:
            return py_src or py_item
        if afc_src:
            return f"afc:{afc_src}"
        return TO_PY.get(afc_item, f"afc:{afc_item}")

    return REF.sub(repl, text)


def cells(row):
    return [c.strip() for c in CELL.split(row)[1:-1]]


def sync_checklist(root: Path):
    afc, py = root / SHARED_SOURCE, root / SHARED_COPY
    afc_rows = {
        m.group(1): cells(m.group(0))
        for m in ROW.finditer((afc / "references/checklist.md").read_text(encoding="utf-8"))
    }
    path = py / "references/checklist.md"
    text = path.read_text(encoding="utf-8")

    def repl(m):
        py_id = m.group(1)
        if py_id not in SHARED:
            return m.group(0)
        afc_id = SHARED[py_id]
        src = afc_rows[afc_id]
        mine = cells(m.group(0))
        sources = [s for s in re.split(r",\s*", mine[5]) if not s.startswith("afc:")]
        mine[1] = translate(src[1])
        mine[2] = src[2]
        mine[5] = ", ".join([f"afc:{afc_id}", *sources])
        return "| " + " | ".join(mine) + " |"

    return path, ROW.sub(repl, text)


def sync_script(root: Path):
    afc, py = root / SHARED_SOURCE, root / SHARED_COPY
    text = (afc / "scripts/cli_contract.py").read_text(encoding="utf-8")
    ids = re.compile(r"\b((?:CLI|OUT|EXIT|AGT|ERR|CFG|DISC|TST)-\d{2})\b")
    return py / "scripts/cli_contract.py", ids.sub(
        lambda m: TO_PY.get(m.group(1), f"afc:{m.group(1)}"), text
    )


def present(root: Path) -> tuple[bool, bool]:
    """Whether the source and the copy skill exist (a fixture repo has neither)."""
    return (root / SHARED_SOURCE).is_dir(), (root / SHARED_COPY).is_dir()


def stale_files(root: Path) -> list[tuple[Path, str]]:
    """(path, new text) for every copied file that differs from what sync would write."""
    stale = []
    for path, new in (sync_checklist(root), sync_script(root)):
        new = new.replace("\r\n", "\n")
        if path.read_bytes().decode("utf-8").replace("\r\n", "\n") != new:
            stale.append((path, new))
    return stale


def write(files: list[tuple[Path, str]]) -> None:
    for path, text in files:
        path.write_bytes(text.encode("utf-8"))

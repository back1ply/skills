"""Keep python-cli-packaging in step with agent-friendly-cli, its source for the shared CLI contract.

agent-friendly-cli owns the language-neutral rules. For each shared item, this script copies the
rule text and severity into python-cli-packaging's checklist (keeping that skill's IDs, modes,
Verify cell, and sources), and copies scripts/cli_contract.py with item IDs translated.
Citations are rewritten so they still resolve: agent-friendly sources become `afc:S30`, and
agent-friendly item IDs become the Python skill's IDs (or `afc:ID` when there is no match).

    python scripts/sync_shared.py          # write the files
    python scripts/sync_shared.py --check  # exit 1 if they are out of date (CI)
"""

import argparse
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent / "skills"
AFC = ROOT / "agent-friendly-cli/skills/agent-friendly-cli"
PY = ROOT / "python-cli-packaging/skills/python-cli-packaging"

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


def sync_checklist():
    afc_rows = {
        m.group(1): cells(m.group(0))
        for m in ROW.finditer(
            (AFC / "references/checklist.md").read_text(encoding="utf-8")
        )
    }
    path = PY / "references/checklist.md"
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


def sync_script():
    text = (AFC / "scripts/cli_contract.py").read_text(encoding="utf-8")
    ids = re.compile(r"\b((?:CLI|OUT|EXIT|AGT|ERR|CFG|DISC|TST)-\d{2})\b")
    return PY / "scripts/cli_contract.py", ids.sub(
        lambda m: TO_PY.get(m.group(1), f"afc:{m.group(1)}"), text
    )


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Sync python-cli-packaging from agent-friendly-cli."
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="exit 1 if any file is out of date; write nothing",
    )
    args = parser.parse_args(argv)
    stale = []
    for path, new in (sync_checklist(), sync_script()):
        old = path.read_bytes().decode("utf-8").replace("\r\n", "\n")
        if old != new.replace("\r\n", "\n"):
            stale.append(path.relative_to(ROOT.parent))
            if not args.check:
                path.write_bytes(new.replace("\r\n", "\n").encode("utf-8"))
    if args.check and stale:
        print(
            "out of date (run python scripts/sync_shared.py):",
            *stale,
            sep="\n  ",
            file=sys.stderr,
        )
        return 1
    print(f"{'stale' if args.check else 'updated'}: {len(stale)} file(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

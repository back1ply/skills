"""repo rules: list every rule. This list is the source of truth; nothing copies it by hand."""

from __future__ import annotations

import argparse
import json
import sys

from skills_repo import rules


def build_parser():
    p = argparse.ArgumentParser(
        prog="repo rules", description="List every rule with its ID and title."
    )
    p.add_argument("--json", action="store_true", help="print one JSON array")
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    registry = rules.load_all()
    if args.json:
        rows = [
            {"id": r.id, "title": r.title, "default": r.default, "fixable": r.fix is not None}
            for r in registry.values()
        ]
        json.dump(rows, sys.stdout, indent=2)
        sys.stdout.write("\n")
        return 0
    for family, about in rules.FAMILIES.items():
        print(f"{family}  {about}")
        for r in (r for r in registry.values() if r.family == family):
            tags = ("" if r.default else "  [opt-in]") + ("  [fixable]" if r.fix else "")
            print(f"  {r.id}  {r.title}{tags}")
    return 0

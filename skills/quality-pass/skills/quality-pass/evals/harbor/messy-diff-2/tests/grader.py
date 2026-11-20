#!/usr/bin/env python3
"""Deterministic grader for the quality-pass messy-diff task.

Scores the final /workspace/project/orders.py on six equally weighted checks
and writes the SkillEvaluator reward files.
"""

from __future__ import annotations

import ast
import importlib.util
import json
import os
import subprocess
import sys
from pathlib import Path

PROJECT = Path(os.environ.get("GRADER_PROJECT", "/workspace/project"))
REWARD_JSON = Path(os.environ.get("HARBOR_REWARD_JSON", "/logs/verifier/reward.json"))
REWARD_TXT = Path(os.environ.get("HARBOR_REWARD_TXT", "/logs/verifier/reward.txt"))
MAGIC_NUMBERS = {100, 0.9, 0.95}
CHECKS = ("no_bare_except", "no_unused_imports", "no_magic_numbers", "no_duplication", "behavior_kept", "tests_added")

# (order, expected calc result, expected calc2 result) for valid orders.
CASES = [
    ({"items": [{"price": 10, "qty": 2}]}, 20.0, 20.0),
    ({"items": [{"price": 60, "qty": 2}]}, 108.0, 108.0),
    ({"items": [{"price": 60, "qty": 2}], "member": True}, 102.6, 102.6),
    ({"items": [{"price": 30, "qty": 1}], "member": True, "shipping": 5}, 28.5, 33.5),
    ({"items": []}, 0, 0),
]


def result(ok: bool, reason: str) -> dict:
    return {"score": 1.0 if ok else 0.0, "reason": reason}


def check_bare_except(tree: ast.Module) -> dict:
    lines = [h.lineno for h in ast.walk(tree) if isinstance(h, ast.ExceptHandler) and h.type is None]
    return result(not lines, f"bare except at lines {lines}" if lines else "none")


def bound_name(node: ast.Import | ast.ImportFrom, alias: ast.alias) -> str:
    name = alias.asname or alias.name
    return name.split(".")[0] if isinstance(node, ast.Import) else name


def check_unused_imports(tree: ast.Module) -> dict:
    imports = [n for n in ast.walk(tree) if isinstance(n, (ast.Import, ast.ImportFrom))]
    imported = {bound_name(node, alias) for node in imports for alias in node.names}
    used = {n.id for n in ast.walk(tree) if isinstance(n, ast.Name)}
    unused = sorted(imported - used)
    return result(not unused, f"unused: {unused}" if unused else "none")


def check_magic_numbers(tree: ast.Module) -> dict:
    functions = [n for n in ast.walk(tree) if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]
    hits = sorted(
        {
            (c.value, c.lineno)
            for f in functions
            for c in ast.walk(f)
            if isinstance(c, ast.Constant) and type(c.value) in (int, float) and c.value in MAGIC_NUMBERS
        }
    )
    return result(not hits, f"literals inside functions: {hits}" if hits else "named")


def check_duplication(tree: ast.Module) -> dict:
    # The original change copies the price * qty loop into calc and calc2;
    # line_total already holds one lookup, so one is the minimum.
    refs = sum(1 for n in ast.walk(tree) if isinstance(n, ast.Constant) and n.value == "price")
    return result(refs <= 1, f"'price' lookups: {refs}")


def load_module(source_path: Path):
    spec = importlib.util.spec_from_file_location("orders_under_test", source_path)
    if spec is None or spec.loader is None:
        raise ImportError("orders.py cannot be imported")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def behavior_mismatches(module) -> list[object]:
    bad: list[object] = [
        (order, module.calc(dict(order)), module.calc2(dict(order)))
        for order, want_calc, want_calc2 in CASES
        if abs(module.calc(dict(order)) - want_calc) > 1e-6 or abs(module.calc2(dict(order)) - want_calc2) > 1e-6
    ]
    if module.dump({"a": 1}) != json.dumps({"a": 1}) or module.line_total({"price": 2, "qty": 3}) != 6:
        bad.append("dump or line_total changed")
    return bad


def check_behavior(source_path: Path) -> dict:
    try:
        bad = behavior_mismatches(load_module(source_path))
    except Exception as exc:  # noqa: BLE001 - any failure means behavior was not kept
        return result(False, f"import or call failed: {exc}")
    return result(not bad, f"mismatches: {bad}" if bad else "all cases match")


def check_tests() -> dict:
    files = list(PROJECT.glob("test_*.py")) + list((PROJECT / "tests").glob("test_*.py"))
    mentions = any("calc" in f.read_text(encoding="utf-8").replace("line_total", "") for f in files)
    run = subprocess.run([sys.executable, "-m", "pytest", "-q"], check=False, cwd=PROJECT, capture_output=True, text=True, timeout=120)
    return result(mentions and run.returncode == 0, f"tests cover calc: {mentions}; pytest exit {run.returncode}")


def grade() -> dict:
    source_path = PROJECT / "orders.py"
    sys.path.insert(0, str(PROJECT))
    try:
        tree = ast.parse(source_path.read_text(encoding="utf-8"))
    except (OSError, SyntaxError) as exc:
        return {name: result(False, f"orders.py unreadable: {exc}") for name in CHECKS}
    return {
        "no_bare_except": check_bare_except(tree),
        "no_unused_imports": check_unused_imports(tree),
        "no_magic_numbers": check_magic_numbers(tree),
        "no_duplication": check_duplication(tree),
        "behavior_kept": check_behavior(source_path),
        "tests_added": check_tests(),
    }


def write(results: dict) -> None:
    score = round(sum(r["score"] for r in results.values()) / len(results), 4)
    reward = {"overall": score, "custom_metrics": {k: v["score"] for k, v in results.items()}, "details": results}
    REWARD_JSON.parent.mkdir(parents=True, exist_ok=True)
    REWARD_JSON.write_text(json.dumps(reward, indent=2), encoding="utf-8")
    REWARD_TXT.write_text(str(score), encoding="utf-8")


if __name__ == "__main__":
    write(grade())

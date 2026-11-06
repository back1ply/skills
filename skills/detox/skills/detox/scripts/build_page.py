#!/usr/bin/env python3
"""Build the /detox plan page from the five findings files.

Usage: python3 build_page.py <run_dir> [--sample]

Reads  <run_dir>/findings/{interface,memory,skills,connectors,scheduled}.json
Writes <run_dir>/page/index.html and <run_dir>/page/state.json

The page keeps its findings inline. Ticks live in state.json, which the page
saves itself (artifact files form). Claude reads state.json back after "Begin".
State ticks: {row id: {"action": label, "comment": text}}.
"""
import json
import os
import re
import sys
from datetime import date

PARTS = ["interface", "memory", "skills", "connectors", "scheduled"]
BANNED = [("—", "em dash"), ("–", "en dash")]
BANNED_WORD = re.compile(r"\bship(s|ped|ping)?\b", re.I)


def load_findings(run_dir):
    out, missing = [], []
    for part in PARTS:
        p = os.path.join(run_dir, "findings", part + ".json")
        if not os.path.exists(p):
            missing.append(part)
            continue
        with open(p) as f:
            data = json.load(f)
        data.setdefault("part", part)
        data.setdefault("title", part.title())
        out.append(data)
    return out, missing


def check(findings):
    """Return a list of problems. Fixes what it safely can.

    Duplicate ids, pre-ticked rows, bad modes, cell and column counts, approve
    rows without actions, a bad default, bad token values, banned text.
    """
    problems, seen = [], set()
    for p in findings:
        for t in p.get("tables", []):
            for r in t.get("rows", []):
                rid = r.get("id")
                if not rid:
                    problems.append(f"{t.get('id')}: row without id")
                elif rid in seen:
                    problems.append(f"duplicate row id {rid}")
                seen.add(rid)
                if r.get("tick"):
                    problems.append(f"{rid}: pre-ticked, forcing false")
                    r["tick"] = False
                if r.get("mode") not in ("approve", "flag", "info"):
                    problems.append(f"{rid}: bad mode {r.get('mode')}, set to info")
                    r["mode"] = "info"
                if len(r.get("cells", [])) != len(t.get("columns", [])):
                    problems.append(f"{rid}: {len(r.get('cells', []))} cells for {len(t.get('columns', []))} columns")
                if r["mode"] == "approve":
                    acts = r.get("actions") or []
                    if not acts or not all(isinstance(a, dict) and a.get("label") and a.get("apply") for a in acts):
                        problems.append(f"{rid}: approve row needs actions with label and apply, set to flag")
                        r["mode"] = "flag"
                    elif not isinstance(r.get("default"), int) or not 0 <= r["default"] < len(acts):
                        problems.append(f"{rid}: bad default, set to 0")
                        r["default"] = 0
                tok = r.get("tokens")
                if tok is not None and (not isinstance(tok, (int, float)) or tok < 0):
                    problems.append(f"{rid}: tokens must be a number or null, set to null")
                    r["tokens"] = None
    text = json.dumps(findings, ensure_ascii=False)
    for ch, name in BANNED:
        if ch in text:
            problems.append(f"{text.count(ch)} x {name} in findings")
    for m in set(BANNED_WORD.findall(text)):
        problems.append("banned word found (s-h-i-p" + m + ")")
    return problems


def target_key(r):
    """What the default action touches, so one skill or connector counts once."""
    acts = r.get("actions") or []
    i = r.get("default", 0)
    a = (acts[i] if 0 <= i < len(acts) else {}).get("apply", {})
    if a.get("kind") in ("edit_file", "create_file", "task_update", "none", None):
        return (a.get("kind"), r.get("id"))  # two edits to one file both count
    ref = a.get("path") or a.get("id") or a.get("name") or a.get("service") or r.get("id")
    if isinstance(ref, str) and ref.endswith("/SKILL.md"):
        ref = ref[: -len("/SKILL.md")]
    return (a.get("kind"), ref)


def savings(findings):
    """Context tokens saved per chat if every approve row takes its default.
    Rows that touch the same target count once (biggest number wins)."""
    best, est = {}, False
    for p in findings:
        for t in p.get("tables", []):
            for r in t.get("rows", []):
                if r.get("mode") == "approve" and r.get("tokens"):
                    k = (p.get("part"), target_key(r)[1])
                    best[k] = max(best.get(k, 0), r["tokens"])
                    est = est or bool(r.get("tokens_est"))
    by_part = {}
    for (part, _), v in best.items():
        by_part[part] = by_part.get(part, 0) + v
    return int(sum(best.values())), est, by_part


def context_categories(run_dir):
    """Category totals from the /context table, when the run has one."""
    out, path = {}, os.path.join(run_dir, "raw", "context_usage.txt")
    if not os.path.exists(path):
        return out
    for line in open(path):
        m = re.match(r"\|\s*([A-Za-z ()]+?)\s*\|\s*([\d.]+)(k?)\s*\|", line)
        if m:
            out[m.group(1)] = int(float(m.group(2)) * (1000 if m.group(3) else 1))
    return out


def clean_text(findings):
    """Swap dashes for commas so the page never shows them."""
    raw = json.dumps(findings, ensure_ascii=False)
    raw = raw.replace(" — ", ", ").replace("—", ", ").replace("–", "-")
    return json.loads(raw)


def inline(obj):
    return json.dumps(obj, ensure_ascii=False).replace("</", "<\\/")


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    run_dir = os.path.abspath(sys.argv[1])
    sample = "--sample" in sys.argv
    here = os.path.dirname(os.path.abspath(__file__))
    tpl = open(os.path.join(here, "..", "assets", "page.html")).read()

    findings, missing = load_findings(run_dir)
    problems = check(findings)
    findings = clean_text(findings)

    run = os.path.basename(run_dir)
    folders = sorted({r.get("folder") for p in findings for t in p.get("tables", [])
                      for r in t.get("rows", []) if r.get("folder")})
    tok, tok_est, by_part = savings(findings)
    # the page dedupes by this key too, so a skill in two tables counts once
    for p in findings:
        for t in p.get("tables", []):
            for r in t.get("rows", []):
                if r.get("mode") == "approve":
                    r["tkey"] = f'{p.get("part")}|{target_key(r)[1]}'
    n_rows = sum(len(t.get("rows", [])) for p in findings for t in p.get("tables", []))
    n_approve = sum(1 for p in findings for t in p.get("tables", []) for r in t.get("rows", []) if r.get("mode") == "approve")
    meta = {
        "run": run,
        "sample": sample,
        "subtitle": f"Run of {run}. {n_approve} changes to review, {n_rows} rows in all. Nothing changes until you tick it.",
        "folders": folders,
        "savings": tok,
        "savings_est": tok_est,
    }
    # ticks: {row id: {"action": <label>, "comment": <text>}}; comments: {row id: text} for unticked rows
    state = {"status": "draft", "ticks": {}, "comments": {}, "report": []}

    logo = open(os.path.join(here, "..", "assets", "logo.svg")).read()
    html = (tpl.replace("__LOGO__", logo)
               .replace("__FINDINGS__", inline(findings))
               .replace("__META__", inline(meta))
               .replace("__STATE__", inline(state)))

    out = os.path.join(run_dir, "page")
    os.makedirs(out, exist_ok=True)
    with open(os.path.join(out, "index.html"), "w") as f:
        f.write(html)
    with open(os.path.join(out, "state.json"), "w") as f:
        json.dump(state, f, indent=2)

    print(f"page: {os.path.join(out, 'index.html')}")
    print(f"parts: {len(findings)}  missing: {missing or 'none'}  rows: {n_rows}  approve: {n_approve}")
    print(f"approve all saves: {tok} tokens per chat{' (est.)' if tok_est else ''}  folders: {len(folders)}")
    measured = context_categories(run_dir)
    for part, v in sorted(by_part.items()):
        cap = measured.get({"skills": "Skills", "memory": "Memory files"}.get(part, ""), None)
        flag = "  OVER MEASURED, FIX" if cap is not None and v > cap else ""
        print(f"  {part}: {v} tokens" + (f" (measured {part} total: {cap})" if cap is not None else "") + flag)
    for p in problems:
        print("check:", p)


if __name__ == "__main__":
    main()

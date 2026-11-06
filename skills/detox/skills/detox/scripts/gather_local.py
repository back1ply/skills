#!/usr/bin/env python3
"""Read-only gather step for /detox.

Reads the Claude setup from disk and writes raw JSON files. It changes nothing.

Usage: python3 gather_local.py <out_dir> [--days 30] [--active "/path/a,/path/b"]

Writes into <out_dir>:
  sessions.json    Code-tab sessions (title, folder, last active, archived, model)
  folders.json     folders with session counts, to propose the active ones
  scheduled.json   scheduled tasks, last runs, failures, model per run
  mods.json        mods, what they do, on or off
  skills.json      every SKILL.md on the machine, with location, use count, last used
  connectors.json  MCP servers seen in chats, with call count and last used
  context.json     global CLAUDE.md, memory folders, and per active folder: route files,
                   sub-folders missing a CLAUDE.md or index, recent context files
"""
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import time
from collections import defaultdict
from pathlib import Path

HOME = Path.home()
APP = HOME / "Library/Application Support/Claude"
CODE_SESSIONS = APP / "claude-code-sessions"
COWORK_SESSIONS = APP / "local-agent-mode-sessions"
PROJECTS = HOME / ".claude/projects"
NOW = time.time()


def arg(name, default=None):
    if name in sys.argv:
        return sys.argv[sys.argv.index(name) + 1]
    return default


def days_ago(ts):
    if ts is None:
        return None
    return round((NOW - ts) / 86400, 1)


def iso_to_epoch(s):
    try:
        return time.mktime(time.strptime(s[:19], "%Y-%m-%dT%H:%M:%S")) - time.timezone
    except Exception:
        return None


def frontmatter(text):
    m = re.match(r"^---\s*\n(.*?)\n---", text, re.S)
    out = {}
    if not m:
        return out
    key = None
    for line in m.group(1).splitlines():
        km = re.match(r"^([A-Za-z0-9_-]+):\s*(.*)$", line)
        if km:
            key = km.group(1)
            out[key] = km.group(2).strip().strip('"').strip("'")
        elif key and line.startswith((" ", "\t")):
            out[key] = (out[key] + " " + line.strip()).strip()
    return out


# ---------- sessions ----------

def read_sessions(root):
    rows = []
    if root.exists():
        for f in root.glob("*/*/local_*.json"):
            try:
                d = json.loads(f.read_text())
            except Exception:
                continue
            last = (d.get("lastActivityAt") or d.get("createdAt") or 0) / 1000
            rows.append({
                "id": d.get("sessionId"),
                "title": d.get("title") or "",
                "cwd": d.get("cwd") or "",
                "created_days_ago": days_ago((d.get("createdAt") or 0) / 1000),
                "last_active_days_ago": days_ago(last),
                "archived": bool(d.get("isArchived")),
                "model": d.get("model"),
                "scheduled_task": d.get("scheduledTaskId"),
                "error": (d.get("error") or "")[:200],
                "_last": last,
            })
    rows.sort(key=lambda r: -r["_last"])
    return rows


def gather_sessions():
    rows = read_sessions(CODE_SESSIONS)
    cowork_count = len(list(COWORK_SESSIONS.glob("*/*/local_*"))) if COWORK_SESSIONS.exists() else 0
    return rows, cowork_count


def gather_folders(sessions, days):
    by = defaultdict(lambda: {"sessions": 0, "recent": 0, "last_active_days_ago": None})
    for s in sessions:
        if s["scheduled_task"]:
            continue
        b = by[s["cwd"]]
        b["sessions"] += 1
        if s["last_active_days_ago"] is not None and s["last_active_days_ago"] <= days:
            b["recent"] += 1
        if b["last_active_days_ago"] is None or s["last_active_days_ago"] < b["last_active_days_ago"]:
            b["last_active_days_ago"] = s["last_active_days_ago"]
    out = [{"folder": k, **v, "proposed_active": v["recent"] >= 2} for k, v in by.items() if k]
    out.sort(key=lambda r: (-r["recent"], -r["sessions"]))
    return out


# ---------- scheduled tasks ----------

def gather_scheduled(sessions):
    # Code tab tasks live in ~/.claude/scheduled-tasks, Cowork tasks in ~/Documents/Claude/Scheduled.
    # Cowork runs are Cowork sessions with a scheduledTaskId.
    runs = defaultdict(list)
    for s in sessions + read_sessions(COWORK_SESSIONS):
        if s["scheduled_task"]:
            runs[s["scheduled_task"]].append(s)
    tasks = []
    homes = [("code", HOME / ".claude/scheduled-tasks"), ("cowork", HOME / "Documents/Claude/Scheduled")]
    for where, base in homes:
        for d in sorted(base.glob("*/")) if base.exists() else []:
            sk = d / "SKILL.md"
            fm = frontmatter(sk.read_text()) if sk.exists() else {}
            r = sorted(runs.get(d.name, []), key=lambda x: -x["_last"])
            last10 = r[:10]
            tasks.append({
                "id": d.name,
                "where": where,
                "description": fm.get("description", ""),
                "runs_seen": len(r),
                "last_run_days_ago": last10[0]["last_active_days_ago"] if last10 else None,
                "failures_last_10": sum(1 for x in last10 if x["error"]),
                "last_error": next((x["error"] for x in last10 if x["error"]), ""),
                "models_last_10": sorted({x["model"] for x in last10 if x["model"]}),
                "path": str(sk),
            })
    return tasks


# ---------- mods ----------

def gather_mods():
    base = HOME / ".claude/mods"
    if not base.exists():
        return {"present": False, "mods": []}
    try:
        sw = json.loads((base / "switches.json").read_text())
    except Exception:
        sw = {}
    mods = []
    for d in sorted(p for p in base.iterdir() if p.is_dir()):
        pj = d / ".claude-plugin/plugin.json"
        desc = ""
        if pj.exists():
            try:
                desc = json.loads(pj.read_text()).get("description", "")
            except Exception:
                pass
        on = sw.get(d.name, True)
        mods.append({"name": d.name, "description": desc, "on": bool(on),
                     "hidden": bool(sw.get(d.name + ":hidden", False))})
    return {"present": True, "mods": mods}


# ---------- log scan (skill calls and MCP calls) ----------

TOOL_RE = r'"name":"(Skill|mcp__[^"]+)","input"'


def grep_lines(roots, include):
    """Yield lines that hold a Skill or MCP tool call. Uses ripgrep when it exists."""
    roots = [str(r) for r in roots if Path(r).exists()]
    if not roots:
        return
    rg = shutil.which("rg")
    cmd = None
    if rg:
        cmd = [rg, "--no-filename", "--no-messages", "-g", include, "-e", TOOL_RE] + roots
        exe = None
    else:
        claude = os.environ.get("CLAUDE_CODE_EXECPATH") or str(HOME / ".local/bin/claude")
        if os.access(claude, os.X_OK):
            cmd = ["rg", "--no-filename", "--no-messages", "-g", include, "-e", TOOL_RE] + roots
            exe = claude
    if cmd is None:
        cmd = ["grep", "-rhE", "--include", include, TOOL_RE] + roots
        exe = None
    p = subprocess.Popen(cmd, executable=exe, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
                         text=True, errors="replace")
    for line in p.stdout:
        yield line
    p.wait()


def scan_logs():
    skills = defaultdict(lambda: {"uses": 0, "last": 0, "where": set()})
    mcp = defaultdict(lambda: {"calls": 0, "last": 0, "tools": set()})
    sources = [(PROJECTS, "*.jsonl", "code"), (COWORK_SESSIONS, "audit.jsonl", "cowork")]
    for root, inc, where in sources:
        for line in grep_lines([root], inc):
            try:
                d = json.loads(line)
            except Exception:
                continue
            ts = iso_to_epoch(d.get("timestamp") or d.get("_audit_timestamp") or "") or 0
            m = d.get("message")
            content = m.get("content") if isinstance(m, dict) else None
            if not isinstance(content, list):
                continue
            for b in content:
                if not isinstance(b, dict) or b.get("type") != "tool_use":
                    continue
                name = b.get("name", "")
                if name == "Skill":
                    sk = (b.get("input") or {}).get("skill") or ""
                    if not sk:
                        continue
                    e = skills[sk]
                    e["uses"] += 1
                    e["last"] = max(e["last"], ts)
                    e["where"].add(where)
                elif name.startswith("mcp__"):
                    parts = name.split("__")
                    server = parts[1] if len(parts) > 2 else name
                    e = mcp[server]
                    e["calls"] += 1
                    e["last"] = max(e["last"], ts)
                    e["tools"].add(parts[-1])
    sk_out = {k: {"uses": v["uses"], "last_used_days_ago": days_ago(v["last"]) if v["last"] else None,
                  "where": sorted(v["where"])} for k, v in skills.items()}
    mcp_out = [{"server": k, "calls": v["calls"], "tools_used": len(v["tools"]),
                "last_used_days_ago": days_ago(v["last"]) if v["last"] else None}
               for k, v in mcp.items()]
    mcp_out.sort(key=lambda r: (r["last_used_days_ago"] is None, r["last_used_days_ago"] or 0))
    return sk_out, mcp_out


# ---------- skills on disk ----------

SKIP_DIRS = {"node_modules", ".git", "Caches", "Cache", ".Trash", ".npm", ".cache", "Library/Caches",
             "site-packages", ".venv", "venv", "dist", "build", ".next"}


def find_skill_files():
    roots = [HOME / ".claude", HOME / "Documents", HOME / "dev", HOME / "Desktop", HOME / "Projects",
             APP / "local-agent-mode-sessions/skills-plugin"]
    seen = set()
    for root in roots:
        if not root.exists():
            continue
        for dirpath, dirnames, filenames in os.walk(root):
            dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS and not d.startswith("._")]
            if "/.claude/projects" in dirpath or "/scheduled-tasks" in dirpath:
                dirnames[:] = []
                continue
            if "SKILL.md" in filenames:
                p = os.path.realpath(os.path.join(dirpath, "SKILL.md"))
                if p not in seen:
                    seen.add(p)
                    yield Path(dirpath) / "SKILL.md"


def enabled_plugins():
    try:
        d = json.loads((HOME / ".claude/settings.json").read_text())
        return {k.split("@")[0] for k, v in (d.get("enabledPlugins") or {}).items() if v}
    except Exception:
        return set()


ENABLED = enabled_plugins()


def location_of(path):
    s = str(path)
    if "/local-agent-mode-sessions/skills-plugin/" in s:
        return "desktop-harness"
    if s.startswith(str(HOME / ".claude/skills")):
        return "global"
    if s.startswith(str(HOME / ".claude/plugins")):
        # synced = org plugins pushed by the Claude app; cache = installed plugins.
        # marketplaces = catalog copies, never loaded.
        if "/plugins/synced/" in s:
            return "plugin"
        m = re.search(r"/plugins/cache/[^/]+/([^/]+)/", s)
        if m and m.group(1) in ENABLED:
            return "plugin"
        return "plugin-stored"
    if "/.claude/skills/" in s:
        return "folder"
    return "loose"  # a SKILL.md outside any skills folder: a copy or a source, not loaded


def plugin_prefix(path):
    m = re.search(r"/plugins/(?:cache|marketplaces|synced)/[^/]+/([^/]+)/", str(path))
    return m.group(1) if m else None


def gather_skills(usage):
    rows = []
    for p in find_skill_files():
        try:
            text = p.read_text(errors="replace")
        except Exception:
            continue
        fm = frontmatter(text)
        name = fm.get("name") or p.parent.name
        loc = location_of(p)
        desc = fm.get("description", "")
        rows.append({
            "name": name,
            "location": loc,
            "path": str(p),
            "description": desc[:400],
            "desc_tokens": max(1, len(desc) // 4),
            "body_lines": text.count("\n"),
            "manual_only": fm.get("disable-model-invocation", "").lower() == "true",
            "md5": hashlib.md5(text.encode()).hexdigest(),
        })
    # use counts: match plain name, or plugin:name
    for r in rows:
        u = usage.get(r["name"])
        if not u:
            for k, v in usage.items():
                if k.split(":")[-1] == r["name"]:
                    u = v
                    break
        r["uses"] = u["uses"] if u else 0
        r["last_used_days_ago"] = u["last_used_days_ago"] if u else None
        r["used_in"] = u["where"] if u else []
    by_name = defaultdict(list)
    for r in rows:
        by_name[r["name"]].append(r)
    for r in rows:
        r["copies"] = len(by_name[r["name"]])
        r["identical_copies"] = sum(1 for x in by_name[r["name"]] if x["md5"] == r["md5"])
    rows.sort(key=lambda r: (r["name"], r["location"]))
    return rows


# ---------- context files ----------

def gather_context(active, days=30):
    """Global layer plus one entry per active folder.

    Per folder: does it exist, its CLAUDE.md / index / map / readme files, its
    top-level sub-folders and whether each has its own CLAUDE.md or index, and
    the context files changed in the last `days` days (newest first).
    """
    out = {"global_claude_md": None, "memory_dirs": [], "projects": []}
    g = HOME / ".claude/CLAUDE.md"
    if g.exists():
        t = g.read_text(errors="replace")
        out["global_claude_md"] = {"path": str(g), "lines": t.count("\n"), "chars": len(t)}
    for m in PROJECTS.glob("*/memory") if PROJECTS.exists() else []:
        files = list(m.glob("*.md"))
        out["memory_dirs"].append({"path": str(m), "files": len(files),
                                   "chars": sum(f.stat().st_size for f in files)})
    route_names = ("index.md", "map.md", "readme.md")
    for folder in active:
        fp = Path(folder)
        proj = {"folder": folder, "exists": fp.exists(), "root_claude_md": None,
                "route_files": [], "top_dirs": [], "recent_context": [], "md_files": 0}
        out["projects"].append(proj)
        if not fp.exists():
            continue
        for name in ("CLAUDE.md", "AGENTS.md"):
            if (fp / name).exists():
                t = (fp / name).read_text(errors="replace")
                proj["root_claude_md"] = {"path": str(fp / name), "lines": t.count("\n")}
                break
        for d in sorted(x for x in fp.iterdir() if x.is_dir() and x.name not in SKIP_DIRS
                        and not x.name.startswith((".", "_"))):
            names = {f.name.lower() for f in d.iterdir() if f.is_file()} if d.exists() else set()
            proj["top_dirs"].append({"name": d.name, "has_claude_md": "claude.md" in names,
                                     "has_index": bool(names & set(route_names))})
        recent = []
        for dirpath, dirnames, filenames in os.walk(fp):
            dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS and not d.startswith(".")]
            for fn in filenames:
                if not fn.endswith(".md"):
                    continue
                proj["md_files"] += 1
                p = Path(dirpath) / fn
                try:
                    st = p.stat()
                except Exception:
                    continue
                row = {"path": str(p), "bytes": st.st_size, "modified_days_ago": days_ago(st.st_mtime)}
                if fn in ("CLAUDE.md", "AGENTS.md") or fn.lower() in route_names:
                    proj["route_files"].append(row)
                elif row["modified_days_ago"] is not None and row["modified_days_ago"] <= days:
                    recent.append(row)
        proj["recent_context"] = sorted(recent, key=lambda r: r["modified_days_ago"])[:40]
    return out


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    out = Path(sys.argv[1])
    out.mkdir(parents=True, exist_ok=True)
    days = int(arg("--days", "30"))
    t0 = time.time()

    sessions, cowork_count = gather_sessions()
    folders = gather_folders(sessions, days)
    active = [a for a in (arg("--active", "") or "").split(",") if a] or \
             [f["folder"] for f in folders if f["proposed_active"]]
    usage, mcp = scan_logs()
    files = {
        "sessions.json": {"code_sessions": [{k: v for k, v in s.items() if k != "_last"} for s in sessions],
                          "cowork_session_count": cowork_count},
        "folders.json": {"days": days, "folders": folders, "active_used": active},
        "scheduled.json": gather_scheduled(sessions),
        "mods.json": gather_mods(),
        "skills.json": {"skills": gather_skills(usage), "skill_calls_seen": usage},
        "connectors.json": {"servers_seen_in_chats": mcp},
        "context.json": gather_context(active, days),
    }
    for name, data in files.items():
        (out / name).write_text(json.dumps(data, indent=1, default=list))
    print(json.dumps({"out": str(out), "seconds": round(time.time() - t0, 1),
                      "code_sessions": len(sessions), "cowork_sessions": cowork_count,
                      "skills_on_disk": len(files["skills.json"]["skills"]),
                      "mcp_servers_seen": len(mcp), "active_folders": active}, indent=1))


if __name__ == "__main__":
    main()

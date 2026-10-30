# /// script
# requires-python = ">=3.12"
# dependencies = []
# ///
"""Scan a generated skill (or article sections) for planted instructions before anyone loads it.

Usage: uv run scan_skill.py <skill_dir_or_file> [--allow example.com,docs.foo.dev]

Web articles are untrusted text, so anything distilled from them can carry a prompt injection.
The source article's own domain is allowed automatically when the target holds info.md files
(from split_sections.py); for a finished skill, pass the source domains with --allow.
HIGH findings (hidden characters, injection phrases, download-and-run commands, encoded blobs)
exit 1: a human must review them before the skill is loaded or published.
MEDIUM findings (hidden HTML comments, links to unexpected domains) are printed for review.
"""

import argparse
import re
import sys
from pathlib import Path

ALLOWED_DOMAINS = {"github.com", "gitlab.com", "codeberg.org"}
INFO_URL = re.compile(r"^- URL: https?://([^/\s]+)", re.MULTILINE)

# Zero-width, bidi-override and control characters (built from code points so this file stays ASCII).
HIDDEN_CHARS = "".join(map(chr, [
    *range(0x200B, 0x2010), 0x2060, 0xFEFF, *range(0x202A, 0x202F), *range(0x2066, 0x206A),
    *range(0x09), 0x0B, 0x0C, *range(0x0E, 0x20), 0x7F,
]))

HIGH = [
    ("hidden character", re.compile("[" + re.escape(HIDDEN_CHARS) + "]")),
    ("injection phrase", re.compile(
        r"ignore (?:all |any |the )?(?:previous|prior|above|earlier) (?:instructions|rules|prompts?)"
        r"|disregard (?:all |any |the |your )?(?:previous|prior|above|earlier)? ?(?:instructions|rules)"
        r"|(?:do not|don't|never) (?:tell|inform|mention (?:this )?to|alert) the user"
        r"|without (?:telling|asking|informing) the user"
        r"|you are now (?:a|an|in) "
        r"|new (?:system )?instructions:"
        r"|<\s*/?\s*(?:system|assistant|im_start|im_end)\s*>",
        re.IGNORECASE)),
    ("download-and-run", re.compile(
        r"(?:curl|wget|iwr|invoke-webrequest)\b[^\n|]*\|\s*(?:sh|bash|zsh|python3?|iex|pwsh|powershell)\b"
        r"|\binvoke-expression\b|\biex\s*\(|powershell[^\n]*-e(?:nc|ncodedcommand)?\s+[A-Za-z0-9+/=]{20,}",
        re.IGNORECASE)),
    ("encoded blob", re.compile(r"(?<![\w/+=])[A-Za-z0-9+/]{100,}={0,2}(?![\w/+=])")),
]
HTML_COMMENT = re.compile(r"<!--")
URL = re.compile(r"https?://([^/\s)\]>\"'`]+)", re.IGNORECASE)


def domain_allowed(host: str, allowed: set[str]) -> bool:
    host = host.lower().split(":")[0]
    return any(host == d or host.endswith(f".{d}") for d in allowed)


def line_findings(line: str, is_markdown: bool, allowed: set[str]) -> list[tuple[str, str, str]]:
    """(severity, label, detail) for one line."""
    found = [("HIGH", label, repr(m.group(0))[:80]) for label, pattern in HIGH if (m := pattern.search(line))]
    if is_markdown and HTML_COMMENT.search(line):
        found.append(("MEDIUM", "html comment (hidden when rendered)", line.strip()[:80]))
    found += [("MEDIUM", "unexpected domain", host) for host in URL.findall(line) if not domain_allowed(host, allowed)]
    return found


def scan_file(path: Path, allowed: set[str]) -> list[tuple[str, str, int, str]]:
    text = path.read_text(encoding="utf-8", errors="replace")
    is_md = path.suffix == ".md"
    return [
        (severity, label, lineno, detail)
        for lineno, line in enumerate(text.splitlines(), 1)
        for severity, label, detail in line_findings(line, is_md, allowed)
    ]


SCANNED_SUFFIXES = {".md", ".txt", ".json", ".py", ".sh", ".yaml", ".yml"}


def files_to_scan(target: Path) -> list[Path]:
    if target.is_file():
        return [target]
    return sorted(p for p in target.rglob("*") if p.is_file() and p.suffix in SCANNED_SUFFIXES)


def parse_allow(extra: str) -> set[str]:
    return ALLOWED_DOMAINS | {d.strip().lower() for d in extra.split(",") if d.strip()}


def source_domains(target: Path) -> set[str]:
    """Domains of the articles being scanned, read from split_sections.py info.md files."""
    infos = [target] if target.name == "info.md" else (target.rglob("info.md") if target.is_dir() else [])
    return {h.lower().removeprefix("www.") for f in infos for h in INFO_URL.findall(f.read_text(encoding="utf-8"))}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("target")
    parser.add_argument("--allow", default="", help="extra allowed domains, comma-separated")
    args = parser.parse_args()

    target = Path(args.target)
    if not target.exists():
        sys.exit(f"error: {target} not found")
    allowed = parse_allow(args.allow) | source_domains(target)
    files = files_to_scan(target)

    findings = [(f, *item) for f in files for item in scan_file(f, allowed)]
    for f, severity, label, lineno, detail in findings:
        print(f"{severity:6} {f}:{lineno}  {label}: {detail}")

    high = sum(1 for _, severity, *_ in findings if severity == "HIGH")
    medium = len(findings) - high
    if high:
        sys.exit(f"FAIL {target}: {high} high, {medium} medium findings across {len(files)} files. Review before loading.")
    print(f"ok {target}: 0 high, {medium} medium findings across {len(files)} files")


if __name__ == "__main__":
    main()

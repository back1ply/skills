#!/usr/bin/env bash
# Refresh the CC BY parts of the skill (rules + primer) from the live site.
# Usage: tools/refresh.sh            (run from the repo root)
# Downloads into _source/ (gitignored), regenerates references/rules.md and
# references/primer.md, and prints a diff summary. Other reference files are
# hand-written notes: review the site's changes and edit them by hand.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
REF="$ROOT/skills/impatient-programming/references"
SRC="$ROOT/_source"
DATE="$(date +%Y-%m-%d)"
mkdir -p "$SRC"

curl -fsSL https://impatientprogramming.org/rules/ -o "$SRC/rules.html"
curl -fsSL https://impatientprogramming.org/primer.md -o "$SRC/primer.md"
curl -fsSL https://impatientprogramming.org/sitemap.xml -o "$SRC/sitemap.xml"

uv run -q --with beautifulsoup4 --with markdownify python -I \
  "$ROOT/tools/extract_rules.py" "$SRC/rules.html" "$REF/rules.md" "$DATE"

{ printf '%s\n\n' "<!-- Source: https://impatientprogramming.org/primer.md by Obie Fernandez, licensed CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/). Unchanged copy. Snapshot: $DATE. -->"
  cat "$SRC/primer.md"; } > "$REF/primer.md"

echo "refreshed rules.md and primer.md ($DATE); pages changed per sitemap lastmod:"
grep -o '<lastmod>[^<]*' "$SRC/sitemap.xml" | sort | uniq -c | sed 's/<lastmod>//'
git -C "$ROOT" diff --stat -- "$REF" || true

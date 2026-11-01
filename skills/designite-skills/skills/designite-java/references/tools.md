# Tools for the Java skill

All commands are bash (Git Bash works on Windows). `SKILL` is this skill's folder, `SRC` the
source root to analyze, `OUT` the output folder.

```bash
TOOLS="${DESIGNITE_TOOLS:-$HOME/.designite-tools}"
OUT="$SRC/.designite"; mkdir -p "$OUT"
```

## One-time setup (needs Java 17+, curl, Python for unzip)

```bash
mkdir -p "$TOOLS" && cd "$TOOLS"
[ -f ck-0.7.0.jar ] || curl -fsSL -o ck-0.7.0.jar \
  https://repo1.maven.org/maven2/com/github/mauricioaniche/ck/0.7.0/ck-0.7.0-jar-with-dependencies.jar
[ -d pmd-bin-7.28.0 ] || { curl -fsSL -o pmd.zip \
  https://github.com/pmd/pmd/releases/download/pmd_releases%2F7.28.0/pmd-dist-7.28.0-bin.zip \
  && { python3 -m zipfile -e pmd.zip . || python -m zipfile -e pmd.zip .; } && rm pmd.zip; }
[ -f TestSmellDetector.jar ] || curl -fsSL -o TestSmellDetector.jar \
  https://github.com/TestSmells/TestSmellDetector/releases/download/v2.2/TestSmellDetector.jar
```

Licenses: CK Apache-2.0, PMD BSD-style, TSDetect GPL-3.0. Nothing is copied into the analyzed repo
except the `.designite/` output folder (add it to `.git/info/exclude`).

## Run

```bash
# 1. CK metrics -> class.csv, method.csv  (args: dir, use jars, files per partition, var metrics, out/)
java -jar "$TOOLS/ck-0.7.0.jar" "$SRC" false 0 false "$OUT/"

# 2. PMD with the Designite ruleset (call via java: pmd.bat breaks on paths with spaces)
java -cp "$TOOLS/pmd-bin-7.28.0/lib/*" net.sourceforge.pmd.cli.PmdCli check --no-progress --no-cache \
  -d "$SRC" -R "$SKILL/assets/pmd-designite.xml" -f json -r "$OUT/pmd.json"

# 3. Package graph from imports
rg --no-heading --no-line-number --field-match-separator '|' -o -r '$1|$3' \
  '^\s*(package|import)\s+(static\s+)?([\w.]+)' -g '*.java' "$SRC" > "$OUT/imports.psv"

# 4. Test smells. Input: one row per test file: app,testFile,productionFile.
#    The production file (found by class name outside test folders) enables Eager Test; blank is allowed.
cd "$OUT" && rg --files -g '*Test.java' -g '*Tests.java' "$SRC" | while read -r t; do
  n=$(basename "$t"); n="${n%Tests.java}"; n="${n%Test.java}"; n="${n%.java}.java"
  p=$(rg --files -g "$n" -g '!**/test/**' -g '!**/tests/**' "$SRC" | head -1)
  echo "app,$t,$p"; done > tsd-input.csv
java -jar "$TOOLS/TestSmellDetector.jar" tsd-input.csv     # writes Output_TestSmellDetection_*.csv here
```

TSDetect aborts the whole run if a production path does not exist, so never guess paths; leave them blank.
Mixed `/` and `\` in paths are fine.

## Read the results

```bash
cd "$OUT"
duckdb -c ".read '$SKILL/assets/design.sql'"                                  # design smells, extremes, package sizes
duckdb -c ".read '$SKILL/assets/graph.sql'" -c ".read '$SKILL/assets/arch.sql'"  # Dense Structure, Unstable Dependency, Cyclic Dependency
jq -r '.files[] | .filename as $f | .violations[] | "\(.rule)\t\($f):\(.beginline)\t\(.description)"' pmd.json | sort | head -200
jq -r '[.files[].violations[].rule] | group_by(.) | map("\(.[0]) \(length)") | .[]' pmd.json   # counts per rule
```

TSDetect CSV: one row per test class; columns are smell names with a count (0 = absent, empty =
not computed). Only these eight are Designite smells:

```bash
duckdb -c "SELECT TestClass, \"Assertion Roulette\" AS assertion_roulette, \"Conditional Test Logic\" AS conditional,
  \"Constructor Initialization\" AS ctor_init, \"Eager Test\" AS eager, EmptyTest AS empty,
  \"Exception Catching Throwing\" AS exception_handling, IgnoredTest AS ignored, \"Unknown Test\" AS unknown
  FROM read_csv('Output_*.csv') ORDER BY TestClass"
```

Line-level checks PMD lacks:

```bash
rg -n --pcre2 '\bif\s*\((?:[^&|]*(?:&&|\|\|)){2}' -g '*.java' "$SRC"     # Complex Conditional (>= 2 operators)
rg -n --pcre2 '^\s*(\S.{120,})$' -g '*.java' "$SRC"                      # Long Statement (> 120 chars)
rg -n 'instanceof' -g '*.java' "$SRC"                                    # Unexploited / Missing Hierarchy candidates
rg -n --pcre2 '(?<![\w."$])(?:[2-9]|\d{2,})(?:\.\d+)?[lLfFdD]?\b' -g '*.java' "$SRC" \
  | rg -v 'static final|^\S+:\d+:\s*(//|\*|import|package|@)'           # Magic Number candidates
```

## Where the tools differ from Designite

| Item | Designite | Tool | Effect |
|---|---|---|---|
| CC | if, case, loops +1; no `&&`/`||` | PMD and CK `wmc` count `&&`/`||` | PMD reports more Complex Methods; check borderline ones |
| LOC | every line of the body | CK `loc` is source lines without blanks/comments | Long Method / God Component report fewer |
| DIT | project ancestors only | CK counts `Object` | use `dit > 7` for DIT > 6 |
| LCOM | Designite's graph LCOM (-1 when not applicable) | CK `lcom*` (Henderson-Sellers) | Multifaceted is an approximation |
| Fan-in | static field reads count | CK may miss static-only use (e.g. constants classes) | confirm Unutilized Abstraction |
| Missing default | any `switch` statement without default | PMD skips exhaustive enum switches | fewer findings |
| Package graph | resolved type references | `import` lines (same-package and fully qualified uses missed) | approximate edges |

# Tools for the C# skill

All commands are bash (Git Bash works on Windows). `SKILL` is this skill's folder, `SRC` the repo
root, `CODE` the source folder(s) to analyze relative to `SRC` (e.g. `src`). Run everything from `$SRC`
so paths stay relative. Needs `uv` (for lizard), `duckdb`, `jq`, `rg`; the .NET SDK for step 2; Java 17+ for step 4.

```bash
cd "$SRC"; OUT="$SRC/.designite"; mkdir -p "$OUT/sarif"     # add .designite to .git/info/exclude
TOOLS="${DESIGNITE_TOOLS:-$HOME/.designite-tools}"
```

## Run

```bash
# 1. Method metrics without building: CC, length, parameters (lizard; names are Class::Method)
uvx lizard -l csharp --csv "$CODE" > "$OUT/lizard.csv"

# 2. .NET analyzer rules (needs a successful build). Injected from outside: no repo file changes,
#    but the build writes bin/ and obj/ as usual. --no-incremental is required or analyzers do not run.
#    Pass the .sln/.slnx or a .csproj. AnalysisMode=All must be on the command line.
dotnet build <solution-or-project> --no-incremental -nologo -v q -p:AnalysisMode=All \
  "-p:CustomAfterMicrosoftCommonTargets=$SKILL/assets/designite.targets" "-p:DesigniteOut=$OUT/sarif"

# 3. Namespace graph, type declarations, file lengths
rg --no-heading --no-line-number --field-match-separator '|' -o -r '$1|$2' \
  '^\s*(?:global\s+)?(namespace|using)\s+(?:static\s+)?([\w.]+)\s*[;{]?\s*$' -g '*.cs' "$CODE" > "$OUT/usings.psv"
rg --no-heading --no-line-number --field-match-separator '|' -o -r '$1|$2' --pcre2 \
  '^\s*(?:(?:public|internal|private|protected|static|sealed|abstract|partial|readonly|file|unsafe|new)\s+)*(class|struct|interface|record|enum)\s+(\w+)' \
  -g '*.cs' "$CODE" > "$OUT/types.psv"
rg -c '' -g '*.cs' "$CODE" > "$OUT/lines.txt"

# 4. Duplicate code (PMD CPD; setup below)
java -cp "$TOOLS/pmd-bin-7.28.0/lib/*" net.sourceforge.pmd.cli.PmdCli cpd --minimum-tokens 70 \
  -d "$CODE" --language cs -f csv > "$OUT/cpd.csv" 2>/dev/null
```

If the build fails (missing SDK/workload, private feeds), skip step 2, say so in the report, and
cover Deficient Encapsulation, Global State and constructor calls with the rg checks below.

PMD setup (once; also used by the Java skill):

```bash
mkdir -p "$TOOLS" && cd "$TOOLS" && [ -d pmd-bin-7.28.0 ] || { curl -fsSL -o pmd.zip \
  https://github.com/pmd/pmd/releases/download/pmd_releases%2F7.28.0/pmd-dist-7.28.0-bin.zip \
  && { python3 -m zipfile -e pmd.zip . || python -m zipfile -e pmd.zip .; } && rm pmd.zip; }; cd "$SRC"
```

## Read the results

```bash
cd "$OUT"
duckdb -c ".read '$SKILL/assets/design.sql'"                                     # Insufficient Modularization, Complex/Long Method, Long Parameter List, namespace sizes, Duplicate Abstraction
duckdb -c ".read '$SKILL/assets/graph.sql'" -c ".read '$SKILL/assets/arch.sql'"   # Dense Structure, Unstable Dependency, Cyclic Dependency
jq -r '.runs[].results[] | select(.ruleId | IN("CA1051","CA2211","CA2214","CA1031")) | "\(.ruleId)\t\(.locations[0].physicalLocation.artifactLocation.uri):\(.locations[0].physicalLocation.region.startLine)\t\(.message.text)"' sarif/*.sarif | sort -u
head -20 cpd.csv      # each row: lines,tokens,occurrences, then line,file pairs for every copy
cd "$SRC"
```

Always filter SARIF to the four rule IDs: other rules can leak through `AnalysisMode=All`.
Multi-targeted projects write one SARIF per target framework; `sort -u` removes the repeats.

Pattern checks (run from `$SRC`):

```bash
rg -nU --pcre2 'catch\b[^{]*\{\s*(?://[^\n]*\s*)*\}' -g '*.cs' "$CODE"                              # Empty Catch Clause
rg -n --pcre2 '\bif\s*\((?:[^&|]*(?:&&|\|\|)){2}' -g '*.cs' "$CODE"                                 # Complex Conditional
rg -n --pcre2 '^\s*(\S.{120,})$' -g '*.cs' "$CODE"                                                  # Long Statement
rg -n -o --pcre2 '\b[a-z_]\w{29,}\b' -g '*.cs' "$CODE" | sort -u                                    # Long Identifier candidates
rg -n --pcre2 '(?<![\w."$])(?:[2-9]|\d{2,})(?:\.\d+)?[mMfFdDlLuU]?\b' -g '*.cs' "$CODE" \
  | rg -v 'const |^\S+:\d+:\s*(//|\*|using|namespace|\[)'                                          # Magic Number candidates
rg -n '\bswitch\s*\(' -g '*.cs' "$CODE"                                                             # switch statements: check for default
rg -nU --pcre2 'override\s+[^({;]+\([^)]*\)\s*(?:\{\s*\}|\{\s*throw\b[^;]*;\s*\}|=>\s*throw\b)' -g '*.cs' "$CODE"   # Rebellious Hierarchy
rg -N --no-filename -o --pcre2 '\b(?:class|record)\s+\w+(?:<[^>]*>)?\s*:\s*([A-Z]\w*)' -r '$1' -g '*.cs' "$CODE" | sort | uniq -c | sort -rn | head   # Wide Hierarchy (NC > 10)
rg -n '\bis [A-Z]\w+|\bas [A-Z]\w+' -g '*.cs' "$CODE"                                               # Unexploited / Missing Hierarchy candidates
rg -n --pcre2 '\bnew [A-Z]\w+(?:<[^>]*>)?\(' -g '*.cs' "$CODE"                                       # Hard-wired Dependency candidates
rg -n --pcre2 '\bstatic\s+(?!readonly|class|void|async|partial|extern|implicit|explicit|operator)(?:[\w<>\[\],?]+\s+)\w+\s*(?:[;=]|\{\s*get)' -g '*.cs' "$CODE"   # Global State candidates
rg -n 'Skip\s*=|\[Ignore' -g '*.cs' .                                                                # Ignored Test
```

## Where the tools differ from Designite

| Item | Designite | Here | Effect |
|---|---|---|---|
| CC | if/case/loops; no `&&`/`||` | lizard counts `&&`/`||` | more Complex Methods; recount borderline |
| NOPM, NOF, fan-in/out, DIT, LCOM | computed from a semantic model | no working metrics tool for .NET 10 here (Microsoft.CodeAnalysis.Metrics failed, CA1502 never fires) | read code for the classes the queries flag |
| Namespace graph | resolved type references | `using` lines; code in `A.B` sees `A` without a `using`, so those edges are missed | approximate; cycles found are real, some may be missing |
| Deficient Encapsulation | public fields | CA1051 (instance) + CA2211 (static) | public `const` not flagged (Designite flags it) |
| Empty Catch | empty block | rg pattern; CA1031 flags catching `Exception` | read both |

# Tools for the Python skill

All commands are bash (Git Bash works on Windows). `SKILL` is this skill's folder, `SRC` the repo
root, `PKG` the package folder(s) to analyze, relative to `SRC` (e.g. `src/mypkg`).
Every tool runs through `uvx`, so nothing is installed into the project. Needs `uv`, `ruff`,
`duckdb`, `jq`, `rg`.

```bash
cd "$SRC"; OUT="$SRC/.designite"; mkdir -p "$OUT"     # add .designite to .git/info/exclude
```

## Run

```bash
# 1. Complexity per function/method (radon) -> CSV: file,class,name,line,end_line,cc
uvx radon cc -j "$PKG" > "$OUT/radon-cc.json"
jq -r 'to_entries[] | select(.value|type=="array") | .key as $f | .value[] | if .type=="class" then (.name as $c | .methods[] | [$f,$c,.name,.lineno,.endline,.complexity]) else [$f,"",.name,.lineno,.endline,.complexity] end | @csv' "$OUT/radon-cc.json" > "$OUT/radon-cc.csv"

# 2. Lines per module -> CSV: file,loc,sloc
uvx radon raw -j "$PKG" | jq -r 'to_entries[] | select(.value.loc) | [.key, .value.loc, .value.sloc] | @csv' > "$OUT/radon-raw.csv"

# 3. Function size, CC, parameters (lizard; CSV has no header, columns are listed in design.sql)
uvx lizard -l python --csv "$PKG" > "$OUT/lizard.csv"

# 4. Module import graph, project modules only (PKG's import name, e.g. mypkg)
uvx pydeps "$PKG" --show-deps --no-output --max-bacon 0 --only "$(basename "$PKG")" > "$OUT/pydeps.json"
jq -r '. as $all | to_entries[] | .key as $m | (.value.imports // [null])[] as $d | [$m, $d, ($all[$m].path // "" | endswith("__init__.py")), (if $d then ($all[$d].path // "" | endswith("__init__.py")) else false end)] | @csv' "$OUT/pydeps.json" > "$OUT/pydeps-edges.csv"

# 5. Rule checks with DPy thresholds
ruff check --isolated --line-length 80 --select E501,S110,PLR2004,SLF001,PD011,PLW0177 --output-format json "$PKG" > "$OUT/ruff.json"
uvx pylint --disable=all --enable=too-many-ancestors,too-many-public-methods,too-many-boolean-expressions,cyclic-import \
  --max-parents=6 --max-public-methods=20 --max-bool-expr=3 --output-format=json "$PKG" > "$OUT/pylint.json" 2>/dev/null

# 6. ML smells (only if the code imports pandas/numpy/torch). dslinter needs Python 3.10 and old pins;
#    it prints errors on stdout, so write JSON straight to a file.
uvx --python 3.10 --from dslinter --with "pylint<2.13" --with "setuptools<70" pylint --load-plugins=dslinter \
  --disable=all --enable=unnecessary-iteration-pandas,nan-numpy,chain-indexing-pandas,merge-parameter-pandas,dataframe-conversion-pandas,forward-pytorch \
  "--output-format=json:$OUT/dslinter.json" "$PKG" >/dev/null 2>&1
```

Do not install pandas into dslinter's environment: in testing it then found fewer smells.

## Read the results

```bash
cd "$OUT"
duckdb -c ".read '$SKILL/assets/design.sql'"                                     # Insufficient Modularization, Multifaceted candidates, God Component, Complex/Long Method, Long Parameter List
duckdb -c ".read '$SKILL/assets/graph.sql'" -c ".read '$SKILL/assets/arch.sql'"   # Hub-like (modules), Dense Structure, Unstable Dependency, cycles
jq -r 'group_by(.code) | map("\(.[0].code) \(length)") | .[]' ruff.json          # counts per ruff rule
jq -r '.[] | "\(.code)\t\(.filename):\(.location.row)\t\(.message)"' ruff.json | head -100
jq -r '.[] | "\(.symbol)\t\(.path):\(.line)\t\(.message)"' pylint.json
[ -f dslinter.json ] && jq -r '.[] | "\(.symbol)\t\(.path):\(.line)\t\(.message)"' dslinter.json
```

Mapping: E501 Long Statement, S110 Empty Catch, PLR2004 Magic Number, SLF001 Deficient Encapsulation,
PD011 Type Blind Conversion, PLW0177 Broken NaN Check; pylint too-many-ancestors Deep Hierarchy,
too-many-public-methods Insufficient Modularization, too-many-boolean-expressions Complex Conditional.
The `cyclic-import` hits are extra information (DPy has no cyclic-dependency smell).

Pattern checks for smells without a tool (run from `$SRC`):

```bash
rg -n --pcre2 '^\s*(?:def|class)\s+\w{21,}|^\s*\w{21,}\s*(?::[^=]+)?=(?!=)' -g '*.py' "$PKG"     # Long Identifier (> 20)
rg -n --pcre2 'lambda\b.{75,}' -g '*.py' "$PKG"                                                  # Long Lambda candidates (> 80)
rg -n --pcre2 '\w\([^()]*\)\.\w+\([^()]*\)\.\w+\(' -g '*.py' "$PKG"                               # Long Message Chain (3+ calls)
rg -n '^\s*match\s.+:\s*$' -g '*.py' "$PKG"                                                      # match statements: check for case _
rg -nU --pcre2 '^\s+def (\w+)\((?:self|cls)\b[^)]*\)[^:]*:\s*\n(?:\s*("""|\x27\x27\x27)[\s\S]*?\2\s*\n)?\s*(pass|raise\b|return\s*$|\.\.\.)' -g '*.py' "$PKG"   # Rebellious candidates
rg -nU --pcre2 'except\b[^:]*:\s*\n\s*return\s*$' -g '*.py' "$PKG"                                # Empty Catch with return
rg -N --no-filename -o --pcre2 '^\s*class\s+\w+\(\s*([\w.]+)' -r '$1' -g '*.py' "$PKG" | sort | uniq -c | sort -rn | head   # Wide Hierarchy (NC > 5)
rg -n --pcre2 '\w\[["\x27][^\]]+["\x27]\]\[' -g '*.py' "$PKG"                                     # Chain Indexing
rg -n --pcre2 '\.merge\((?![^)]*\bon\s*=)' -g '*.py' "$PKG"                                        # Ambiguous Merge Key
rg -n 'iterrows|itertuples|\.forward\(' -g '*.py' "$PKG"                                          # Unnecessary Iteration / Forward Bypass
```

## Where the tools differ from DPy

| Item | DPy | Tool | Effect |
|---|---|---|---|
| CC | McCabe | lizard/radon McCabe (both count `and`/`or`) | close; recount borderline (8-9) |
| Parameters | probably without self | lizard counts self | design.sql subtracts self/cls |
| Long Statement | statement length | ruff E501 per physical line | multi-line statements under-reported |
| LCOM | DPy custom graph LCOM | none | Multifaceted is judged |
| Fan-in/out | class and module dependencies | pydeps: module imports only | class-level Hub-like is judged |
| DIT | project ancestors | pylint counts library ancestors too | confirm Deep Hierarchy |
| Magic Number | any unnamed literal | ruff PLR2004: comparisons only | judge others in hotspots |

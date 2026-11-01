-- DPy design and implementation smells from radon (cc + raw) and lizard. Thresholds: DPy paper (MSR 2025).
CREATE OR REPLACE TABLE f AS SELECT * FROM read_csv('radon-cc.csv', header=false,
  columns={'file':'VARCHAR','class':'VARCHAR','name':'VARCHAR','line':'INT','end_line':'INT','cc':'INT'});
CREATE OR REPLACE TABLE raw AS SELECT * FROM read_csv('radon-raw.csv', header=false,
  columns={'file':'VARCHAR','loc':'INT','sloc':'INT'});
CREATE OR REPLACE TABLE lz AS SELECT * FROM read_csv('lizard.csv', header=false, columns={'nloc':'INT','ccn':'INT',
  'tokens':'INT','params':'INT','length':'INT','location':'VARCHAR','file':'VARCHAR','function':'VARCHAR',
  'long_name':'VARCHAR','line':'INT','end_line':'INT'});
-- abstraction = class, or module (its top-level functions are its methods)
CREATE OR REPLACE TABLE abst AS
SELECT coalesce(nullif(class, ''), '(module)') AS class, file, count(*) AS nom,
       count(*) FILTER (WHERE NOT starts_with(name, '_') OR (starts_with(name, '__') AND ends_with(name, '__'))) AS nopm,
       sum(cc) AS wmc
FROM f GROUP BY ALL;
.print == Insufficient Modularization: NOPM > 20 or NOM > 30 or WMC > 100
SELECT file, class, nom, nopm, wmc FROM abst WHERE nopm > 20 OR nom > 30 OR wmc > 100 ORDER BY wmc DESC;
.print == Multifaceted Abstraction candidates: NOM > 3 (judge LCOM >= 0.8 by reading field use)
SELECT file, class, nom, wmc FROM abst WHERE nom > 3 AND class <> '(module)' ORDER BY nom DESC LIMIT 25;
.print == God Component: > 30 modules or > 27000 LOC per package (folder)
SELECT regexp_replace(replace(file, '\', '/'), '/[^/]+$', '') AS package, count(*) AS modules, sum(loc) AS loc
FROM raw GROUP BY package HAVING count(*) > 30 OR sum(loc) > 27000;
.print == Implementation smells (lizard): Complex Method CC > 7, Long Method > 67 lines, Long Parameter List > 4 (self/cls not counted)
SELECT file, function, line, ccn AS cc, length AS lines,
       params - CASE WHEN regexp_matches(long_name, '\(\s*(self|cls)\b') THEN 1 ELSE 0 END AS params,
       concat_ws(', ', CASE WHEN ccn > 7 THEN 'Complex Method' END, CASE WHEN length > 67 THEN 'Long Method' END,
         CASE WHEN params - CASE WHEN regexp_matches(long_name, '\(\s*(self|cls)\b') THEN 1 ELSE 0 END > 4 THEN 'Long Parameter List' END) AS smells
FROM lz WHERE ccn > 7 OR length > 67 OR params - CASE WHEN regexp_matches(long_name, '\(\s*(self|cls)\b') THEN 1 ELSE 0 END > 4
ORDER BY ccn DESC;

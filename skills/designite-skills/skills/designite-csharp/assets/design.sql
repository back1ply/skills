-- Designite design and implementation smells from lizard (methods) and rg (types, lines).
-- Thresholds: DesigniteJava defaults (Designite C# does not publish its values). lizard counts &&/|| in CC.
CREATE OR REPLACE TABLE lz AS SELECT * FROM read_csv('lizard.csv', header=false, columns={'nloc':'INT','ccn':'INT',
  'tokens':'INT','params':'INT','length':'INT','location':'VARCHAR','file':'VARCHAR','function':'VARCHAR',
  'long_name':'VARCHAR','line':'INT','end_line':'INT'});
CREATE OR REPLACE TABLE types AS SELECT * FROM read_csv('types.psv', delim='|', header=false, quote='',
  columns={'file':'VARCHAR','kind':'VARCHAR','name':'VARCHAR'});
CREATE OR REPLACE TABLE lines AS SELECT * FROM read_csv('lines.txt', delim=':', header=false, quote='',
  columns={'file':'VARCHAR','loc':'INT'});
CREATE OR REPLACE TABLE ns AS SELECT * FROM read_csv('usings.psv', delim='|', header=false, quote='',
  columns={'file':'VARCHAR','kind':'VARCHAR','name':'VARCHAR'}) WHERE kind = 'namespace';
-- lizard names methods Class::Method (nested: Outer::Inner::Method); the class is everything before the last ::
CREATE OR REPLACE TABLE m AS SELECT *, CASE WHEN function LIKE '%::%' THEN regexp_replace(function, '::[^:]+$', '') ELSE '(none)' END AS class FROM lz
  WHERE function <> '*global*';  -- lizard's whole-file pseudo-function
.print == Insufficient Modularization: NOM >= 30 or WMC >= 100 (NOPM: check by reading)
SELECT file, class, count(*) AS nom, sum(ccn) AS wmc FROM m GROUP BY ALL HAVING count(*) >= 30 OR sum(ccn) >= 100 ORDER BY wmc DESC;
.print == Implementation: Complex Method CC >= 8, Long Method >= 100 lines, Long Parameter List >= 5
SELECT file, function, line, ccn AS cc, length AS lines, params,
       concat_ws(', ', CASE WHEN ccn >= 8 THEN 'Complex Method' END, CASE WHEN length >= 100 THEN 'Long Method' END,
                       CASE WHEN params >= 5 THEN 'Long Parameter List' END) AS smells
FROM m WHERE ccn >= 8 OR length >= 100 OR params >= 5 ORDER BY ccn DESC;
.print == Namespace size: God Component (> 30 types or > 27000 LOC)
SELECT n.name AS namespace, count(DISTINCT t.name) AS types, (SELECT sum(l.loc) FROM lines l WHERE l.file IN (SELECT file FROM ns WHERE name = n.name)) AS loc
FROM ns n JOIN types t USING (file) GROUP BY n.name ORDER BY types DESC LIMIT 15;
.print == Duplicate Abstraction candidates: same type name in different namespaces
SELECT t.name, string_agg(DISTINCT n.name, ', ') AS namespaces FROM types t JOIN ns n USING (file)
GROUP BY t.name HAVING count(DISTINCT n.name) > 1;
.print == Metric extremes
SELECT class, count(*) AS nom, sum(ccn) AS wmc, max(ccn) AS max_cc FROM m GROUP BY class ORDER BY wmc DESC LIMIT 10;

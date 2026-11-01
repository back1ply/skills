-- Designite design smells from CK output. Run from the output folder that holds class.csv and method.csv.
-- Thresholds: DesigniteJava defaults (ThresholdsDTO.java). CK dit counts java.lang.Object, so DIT > 6 is dit > 7.
CREATE OR REPLACE TABLE c AS SELECT * FROM read_csv('class.csv', header=true) WHERE type IN ('class', 'interface', 'enum', 'record');
CREATE OR REPLACE TABLE m AS SELECT * FROM read_csv('method.csv', header=true);
CREATE OR REPLACE TABLE smells AS
SELECT class, 'Insufficient Modularization' AS smell,
       concat_ws(', ', CASE WHEN publicMethodsQty >= 20 THEN 'NOPM ' || publicMethodsQty END,
                       CASE WHEN totalMethodsQty >= 30 THEN 'NOM ' || totalMethodsQty END,
                       CASE WHEN wmc >= 100 THEN 'WMC ' || wmc END) AS cause
  FROM c WHERE publicMethodsQty >= 20 OR totalMethodsQty >= 30 OR wmc >= 100
UNION ALL SELECT class, 'Hub-like Modularization', 'fan-in ' || fanin || ', fan-out ' || fanout FROM c WHERE fanin >= 20 AND fanout >= 20
UNION ALL SELECT class, 'Multifaceted Abstraction (approx: lcom*)', 'lcom* ' || "lcom*" || ', NOF ' || totalFieldsQty || ', NOM ' || totalMethodsQty
  FROM c WHERE "lcom*" >= 0.8 AND totalFieldsQty >= 7 AND totalMethodsQty >= 7
UNION ALL SELECT class, 'Broken Modularization', 'NOF ' || totalFieldsQty || ', no methods' FROM c WHERE totalMethodsQty = 0 AND totalFieldsQty >= 5
UNION ALL SELECT class, 'Unnecessary Abstraction', 'NOF ' || totalFieldsQty || ', no methods' FROM c WHERE totalMethodsQty = 0 AND totalFieldsQty <= 5
UNION ALL SELECT class, 'Deficient Encapsulation', publicFieldsQty || ' public field(s)' FROM c WHERE publicFieldsQty > 0
UNION ALL SELECT class, 'Unutilized Abstraction (confirm)', 'fan-in 0' FROM c WHERE fanin = 0 AND class NOT LIKE '%Test%'
UNION ALL SELECT class, 'Wide Hierarchy', 'NC ' || noc FROM c WHERE noc > 10
UNION ALL SELECT class, 'Deep Hierarchy', 'DIT ' || (dit - 1) FROM c WHERE dit > 7
UNION ALL SELECT c.class, 'Imperative Abstraction', 'only public method ' || m.method || ' has ' || m.loc || ' LOC'
  FROM c JOIN m ON m.class = c.class AND m.modifiers & 1 = 1 AND NOT m.constructor
  WHERE c.publicMethodsQty = 1 AND m.loc > 50;
SELECT smell, count(*) AS n FROM smells GROUP BY smell ORDER BY n DESC;
.print == details (first 60)
SELECT smell, class, cause FROM smells ORDER BY smell, class LIMIT 60;
.print == metric extremes
SELECT class, wmc, totalMethodsQty AS nom, loc, "lcom*", fanin, fanout FROM c ORDER BY wmc DESC LIMIT 10;
SELECT class, method, wmc AS cc, loc, parametersQty AS pc FROM m ORDER BY wmc DESC LIMIT 10;
.print == package size (God Component: > 30 classes or > 27000 LOC; Ambiguous Interface: >= 5 classes, 1 public method)
SELECT regexp_replace(class, '\.[^.]+$', '') AS package, count(*) AS classes, sum(loc) AS loc, sum(publicMethodsQty) AS public_methods,
       CASE WHEN count(*) > 30 OR sum(loc) > 27000 THEN 'God Component' WHEN count(*) >= 5 AND sum(publicMethodsQty) = 1 THEN 'Ambiguous Interface?' END AS smell
FROM c WHERE class NOT LIKE '%$%' GROUP BY package ORDER BY classes DESC;

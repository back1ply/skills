-- Namespace dependency graph from namespace/using lines. Input: usings.psv (file|kind|name) made by rg.
-- C# `using X;` imports a namespace, so an edge goes to project namespace X when it exists.
CREATE OR REPLACE TABLE raw AS SELECT * FROM read_csv('usings.psv', delim='|', header=false, quote='',
  columns={'file':'VARCHAR','kind':'VARCHAR','name':'VARCHAR'});
CREATE OR REPLACE TABLE ns AS SELECT DISTINCT file, name AS package FROM raw WHERE kind = 'namespace';
CREATE OR REPLACE TABLE packages AS SELECT DISTINCT package FROM ns;
CREATE OR REPLACE TABLE edges AS
SELECT DISTINCT n.package AS src, u.name AS dst
FROM raw u JOIN ns n USING (file) WHERE u.kind = 'using' AND u.name IN (SELECT package FROM packages);
DELETE FROM edges WHERE dst = src;
.print == Dense Structure: average degree 2E/V >= 5
SELECT count(*) AS namespaces, (SELECT count(*) FROM edges) AS edges,
       round(2.0 * (SELECT count(*) FROM edges) / count(*), 2) AS avg_degree FROM packages;

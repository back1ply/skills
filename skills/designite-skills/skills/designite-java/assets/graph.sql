-- Package dependency graph from import statements. Input: imports.psv (file|kind|name) made by rg.
-- An import a.b.C (or a.b.* captured as "a.b.") maps to the longest project package that prefixes it.
CREATE OR REPLACE TABLE raw AS SELECT * FROM read_csv('imports.psv', delim='|', header=false, quote='',
  columns={'file':'VARCHAR','kind':'VARCHAR','name':'VARCHAR'});
CREATE OR REPLACE TABLE pkg AS SELECT file, name AS package FROM raw WHERE kind = 'package';
CREATE OR REPLACE TABLE packages AS SELECT DISTINCT package FROM pkg;
CREATE OR REPLACE TABLE edges AS
SELECT DISTINCT p.package AS src,
       (SELECT max_by(q.package, length(q.package)) FROM packages q
         WHERE rtrim(i.name, '.') = q.package OR starts_with(i.name, q.package || '.')) AS dst
FROM raw i JOIN pkg p USING (file) WHERE i.kind = 'import';
DELETE FROM edges WHERE dst IS NULL OR dst = src;
.print == Dense Structure: average degree 2E/V >= 5
SELECT count(*) AS packages, (SELECT count(*) FROM edges) AS edges,
       round(2.0 * (SELECT count(*) FROM edges) / count(*), 2) AS avg_degree FROM packages;

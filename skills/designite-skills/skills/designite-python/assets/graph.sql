-- Python module and package graph from pydeps-edges.csv (src,dst,src_is_pkg,dst_is_pkg).
-- A module's package is its parent; a package __init__ is its own package.
CREATE OR REPLACE TABLE me AS SELECT * FROM read_csv('pydeps-edges.csv', header=false,
  columns={'src':'VARCHAR','dst':'VARCHAR','src_is_pkg':'BOOLEAN','dst_is_pkg':'BOOLEAN'});
CREATE OR REPLACE MACRO pkg_of(m, is_pkg) AS CASE WHEN is_pkg THEN m WHEN m LIKE '%.%' THEN regexp_replace(m, '\.[^.]+$', '') ELSE '(root)' END;
CREATE OR REPLACE TABLE packages AS
  SELECT DISTINCT pkg_of(src, src_is_pkg) AS package FROM me UNION SELECT DISTINCT pkg_of(dst, dst_is_pkg) FROM me;
CREATE OR REPLACE TABLE edges AS
  SELECT DISTINCT pkg_of(src, src_is_pkg) AS src, pkg_of(dst, dst_is_pkg) AS dst FROM me WHERE dst IS NOT NULL;
DELETE FROM edges WHERE src = dst;
.print == Hub-like Modularization (module level): fan-in > 7 and fan-out > 7
SELECT m AS module, fan_in, fan_out FROM (
  SELECT m, (SELECT count(DISTINCT src) FROM me WHERE dst = m) AS fan_in, (SELECT count(DISTINCT dst) FROM me WHERE src = m) AS fan_out
  FROM (SELECT src AS m FROM me UNION SELECT dst FROM me WHERE dst IS NOT NULL))
WHERE fan_in > 7 AND fan_out > 7 ORDER BY fan_in + fan_out DESC;
.print == Dense Structure: average degree 2E/V >= 5
SELECT count(*) AS packages, (SELECT count(*) FROM edges) AS edges,
       round(2.0 * (SELECT count(*) FROM edges) / count(*), 2) AS avg_degree FROM packages;

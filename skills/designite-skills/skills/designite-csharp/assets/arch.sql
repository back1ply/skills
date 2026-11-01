-- needs tables packages(package), edges(src,dst)
CREATE OR REPLACE TABLE stability AS
SELECT package, ca, ce, CASE WHEN ca + ce = 0 THEN NULL ELSE round(ce / (ca + ce), 3) END AS instability
FROM (SELECT p.package,
             (SELECT count(*) FROM edges WHERE dst = p.package) AS ca,
             (SELECT count(*) FROM edges WHERE src = p.package) AS ce
      FROM packages p);
.print == Unstable Dependency: src depends on a less stable dst
SELECT e.src, s1.instability AS src_I, e.dst, s2.instability AS dst_I
FROM edges e JOIN stability s1 ON s1.package = e.src JOIN stability s2 ON s2.package = e.dst
WHERE s2.instability > s1.instability ORDER BY e.src;
.print == Cyclic Dependency: each row is one cycle
CREATE OR REPLACE TABLE reach AS
WITH RECURSIVE r(src, dst) AS (
  SELECT src, dst FROM edges UNION SELECT r.src, e.dst FROM r JOIN edges e ON r.dst = e.src)
SELECT * FROM r;
SELECT string_agg(src, ', ' ORDER BY src) AS cycle, count(*) AS size
FROM (SELECT a.src, min(a.dst) FILTER (WHERE EXISTS (SELECT 1 FROM reach b WHERE b.src = a.dst AND b.dst = a.src)) AS rep
      FROM reach a GROUP BY a.src)
WHERE rep IS NOT NULL GROUP BY rep HAVING count(*) > 1;

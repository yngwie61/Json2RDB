DELETE FROM dummy;
DROP TABLE DUMMY;
CREATE TABLE dummy (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    key1 TEXT,
    key2 TEXT,
    key3 INTEGER
);

WITH RECURSIVE cnt(x) AS (
  SELECT 1
  UNION ALL
  SELECT x + 1 FROM cnt WHERE x < 10000
)
INSERT INTO dummy (key1, key2, key3)
SELECT 'value' || x, 'value' || (x + 1), x + 122
FROM cnt;

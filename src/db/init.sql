DELETE FROM dummy;
DROP TABLE DUMMY;
CREATE TABLE dummy (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    key1 TEXT,
    key2 TEXT,
    key3 INTEGER
);
INSERT INTO dummy (key1, key2, key3) VALUES ("value1", "value2", 3);
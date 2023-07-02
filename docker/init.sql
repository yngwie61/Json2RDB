DROP DATABASE IF EXISTS store;
CREATE DATABASE IF NOT EXISTS store;
USE store;

DROP TABLE IF EXISTS dummy;
CREATE TABLE dummy (
    id INTEGER PRIMARY KEY AUTO_INCREMENT,
    key1 TEXT,
    key2 TEXT,
    key3 INTEGER
);

INSERT INTO dummy (key1, key2, key3) VALUES
('value1', 'value2', 123),
('value3', 'value4', 456),
('value5', 'value6', 789);

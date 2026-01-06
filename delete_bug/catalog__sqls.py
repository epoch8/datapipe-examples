SQL__LIST_OF_TABLES = '''
SELECT
    name
FROM
    sqlite_master
WHERE
    type = 'table'
'''


SQL__SELECT_ALL_DATA_FROM_TABLE = '''
SELECT
    *
FROM
    {table}
'''


SQL__DROP_TABLE = '''
DROP TABLE {table}
'''


SQL__CREATE_TABLE = '''
CREATE TABLE {table} (
    input_id INTEGER PRIMARY KEY,
    input_text INTEGER
);
'''


SQL__INSERT_INTO__INPUT = '''
INSERT INTO input
(input_text)
VALUES (?)
'''


SQL__DELETE_FROM__INPUT = '''
DELETE FROM input
WHERE {where}
'''


SQL__INSERT_INTO__PATTERN = '''
INSERT INTO pattern
(find, replace)
VALUES (?, ?)
'''

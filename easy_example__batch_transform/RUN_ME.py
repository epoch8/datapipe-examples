import subprocess
import sqlite3
import pandas as pd

from catalog__sqls import SQL__LIST_OF_TABLES
from catalog__sqls import SQL__SELECT_ALL_DATA_FROM_TABLE
from catalog__sqls import SQL__DROP_TABLE
from catalog__sqls import SQL__INSERT_INTO__INPUT
from catalog__sqls import SQL__INSERT_INTO__PATTERN


PATH__DATA = r'data.sqlite'
PATH__METADATA = r'db.sqlite'


def drop_table(connection, table):
    connection.execute(
        SQL__DROP_TABLE.format(table=table)
    )


def create_table(connection, query):
    connection.execute(query)


def insert__input(connection, values):
    connection.execute(SQL__INSERT_INTO__INPUT, values)
    connection.commit()


def insert__pattern(connection, values):
    connection.execute(SQL__INSERT_INTO__PATTERN, values)
    connection.commit()


def show_db(connection):
    df__list_of_tables = pd.read_sql_query(SQL__LIST_OF_TABLES, connection)
    print(f'\n === LIST OF TABLES === \n')
    print(df__list_of_tables)

    for table in df__list_of_tables['name']:
        print(f'\n\n === {table} === \n')
        print(
            pd.read_sql_query(
                SQL__SELECT_ALL_DATA_FROM_TABLE.format(table=table),
                connection
            )
        )
    print()


if __name__ == '__main__':
    connection__data = sqlite3.connect(PATH__DATA)
    connection__metadata = sqlite3.connect(PATH__METADATA)

    input('''
====================================================================================================
>
>            Hello!
>
>            Let's look how datapipe is working.
>
>            Press Enter to perform command "datapipe db create-all".
>            This command will create all necessary SQLite DBs.
>
====================================================================================================
''')
    
    subprocess.call('datapipe db create-all', shell=True)

    input('''
====================================================================================================
>
>            New DBs should have been created:
>
>            data.sqlite - this one is for Human data;
>            db.sqlite - this one is for Datapipe metadata.
>
>            Let's investigate them.
>            Press Enter to show tables of Human-readable data.
>
====================================================================================================
''')

    connection__data = sqlite3.connect(PATH__DATA)
    connection__metadata = sqlite3.connect(PATH__METADATA)

    show_db(connection__data)
    input('''
====================================================================================================
>
>            Here you can see only two empty tables:
>
>            input - here will be data to process;
>            output - and here will be a result.
>
>            Press Enter to show tables of Datapipe data.
>
====================================================================================================
''')
    
    show_db(connection__metadata)

    input('''
====================================================================================================
>
>            You can see many empty tables.
>            Here will be stored metadata - somewhat like statuses of information.
>
>            Press Enter to populate table "input" with some data and check it.
>
====================================================================================================
''')

    insert__input(connection__data, ('Hello World!',))
    show_db(connection__data)

    input('''
====================================================================================================
>
>            Now you may notice table "input" with new data inside.
>
>            Let's process the data with transformation making 'World' -> 'Kitty' replacement.
>            Press Enter to run Datapipe with command "datapipe run".
>
====================================================================================================
''')
    
    subprocess.call('datapipe run', shell=True)

    input('''
====================================================================================================
>
>            Let's see the result.
>
>            Press Enter to show tables of Human-readable data.
>
====================================================================================================          
''')
    
    show_db(connection__data)

    input('''
====================================================================================================
>
>        Table 'output' now has new record with processed data.
>
>        Press Enter to show tables of Datapipe data.
>
====================================================================================================
''')

    show_db(connection__metadata)

    print('''
====================================================================================================
>
>            Now you can see metadata.
>            Datapipe is aware about rows to process or not.
>
>            Thank you for participation!
>
====================================================================================================
''')

    connection__data.close()
    connection__metadata.close()

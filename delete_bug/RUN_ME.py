import os
import subprocess
import sqlite3
import pandas as pd

from catalog__sqls import SQL__LIST_OF_TABLES
from catalog__sqls import SQL__SELECT_ALL_DATA_FROM_TABLE
from catalog__sqls import SQL__INSERT_INTO__INPUT
from catalog__sqls import SQL__DELETE_FROM__INPUT
from catalog__sqls import SQL__CREATE_TABLE


pd.options.display.float_format = '{:.10f}'.format
pd.set_option('display.width', None)
pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.max_colwidth', None)


PATH__DATA = r"data.sqlite"
PATH__METADATA = r"datapipe.sqlite"


def insert__input(connection, values):
    connection.execute(SQL__INSERT_INTO__INPUT, values)
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


def delete_from_db(connection):
    connection.execute(SQL__DELETE_FROM__INPUT.format(where="input_text = 'Hello World! - 2'"))
    connection.commit()


def create_table(connection, table):
    connection.execute(SQL__CREATE_TABLE.format(table=table))
    connection.commit()


if __name__ == '__main__':
    connection__data = sqlite3.connect(PATH__DATA)
    connection__metadata = sqlite3.connect(PATH__METADATA)

    subprocess.call('datapipe db create-all', shell=True)

    # create_table(connection__data, "input")
    # create_table(connection__data, "output")
    insert__input(connection__data, ('Hello World! - 1',))
    insert__input(connection__data, ('Hello World! - 2',))
    insert__input(connection__data, ('Hello World! - 3',))
    
    subprocess.call('datapipe run', shell=True)
    
    show_db(connection__data)
    show_db(connection__metadata)

    print("""


#################################################################################
###                                                                           ###
###                             DELETE BUG                                    ###
###                                                                           ###
#################################################################################

Record "Hello World! - 2" is going to be removed from table "input".
All "output_meta" records will be deleted cause of empty index of transformation.

#################################################################################
#################################################################################


""")
    delete_from_db(connection__data)

    subprocess.call('datapipe run', shell=True)

    show_db(connection__data)
    show_db(connection__metadata)

    connection__data.close()
    connection__metadata.close()

    os.remove(PATH__DATA)
    os.remove(PATH__METADATA)

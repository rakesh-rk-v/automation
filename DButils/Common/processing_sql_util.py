import logging
from contextlib import contextmanager
import pyodbc
import sys


class SqlUtil:
    def __init__(self, driver=None, server=None, database=None, username=None, password=None):
        self.__connection = "DRIVER=" + driver + ";SERVER=" + server + \
               ";DATABASE=" + database + ";UID=" + username + ";PWD=" + password

    @contextmanager
    def __open_db_connection(self, commit=False):
        connection = pyodbc.connect(self.__connection)
        cursor = connection.cursor()
        try:
            yield cursor
        except pyodbc.DatabaseError as err:
            error, = err.args
            sys.stderr.write(error.message)
            cursor.execute("ROLLBACK")
            raise err
        else:
            if commit:
                cursor.execute("COMMIT")
            else:
                cursor.execute("ROLLBACK")
        finally:
            connection.close()

    def execute_select_query(self, query):
        with self.__open_db_connection() as cursor:
            results = []
            logging.debug("Executing query: " + query)
            cursor.execute(query)
            columns = [column[0] for column in cursor.description]
            for row in cursor.fetchall():
                results.append(dict(zip(columns, row)))
            return results

    def execute_insert_query(self, query):
        with self.__open_db_connection() as cursor:
            logging.debug("Executing query: " + query)
            count = cursor.execute(query).rowcount
            cursor.commit()
            assert count > 0
            return count

    def execute_delete_query(self, query):
        with self.__open_db_connection() as cursor:
            logging.debug("Executing query: " + query)
            count = cursor.execute(query).rowcount
            cursor.commit()
            assert count > 0
            return count

    def execute_update_query(self, query):
        with self.__open_db_connection() as cursor:
            logging.debug("Executing query: " + query)
            cursor.execute(query)
            cursor.commit()
import logging
import sys
from contextlib import contextmanager

import mysql.connector as mysql
import pyodbc

from Utils.config_manager import ConfigManager


class MySqlUtil:
    def __init__(self,app=None):
        self.__host =ConfigManager.get_config().get_value('db_server')
        self.__db = ConfigManager.get_schema(app=app)
        self.__username = ConfigManager.get_config().get_value('db_username')
        self.__password = ConfigManager.get_config().get_value('db_password')
        self.__connection = None
        self._tenant_id= ConfigManager.get_config().get_value('db_tenant_id')

    @contextmanager
    def __open_db_connection(self, commit=False):
        self.__connection = mysql.connect(host=self.__host, database=self.__db, user=self.__username, password=self.__password)
        cursor = self.__connection.cursor()
        try:
            yield cursor
        except pyodbc.DatabaseError as err:
            error, = err.args
            sys.stderr.write(error.message)
            cursor.execute("ROLLBACK")
            raise err
        finally:
            self.__connection.close()

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
            cursor.execute(query)
            assert cursor.rowcount > 0
            self.__connection.commit()
            return cursor.rowcount

    def execute_delete_query(self, query):
        with self.__open_db_connection() as cursor:
            logging.debug("Executing query: " + query)
            cursor.execute(query)
            assert cursor.rowcount > 0
            self.__connection.commit()
            return cursor.rowcount

    def execute_update_query(self, query):
        with self.__open_db_connection() as cursor:
            logging.debug("Executing query: " + query)
            cursor.execute(query)
            # assert cursor.rowcount > 0
            self.__connection.commit()
            return cursor.rowcount

    def execute_call_query(self, query):
        with self.__open_db_connection() as cursor:
            logging.debug("Executing query: " + query)
            cursor.execute(query)
            self.__connection.commit()
            return True

    def execute_script(self, script):
        with self.__open_db_connection() as cursor:
            results = []
            for statement in script.split(';'):
                statement = statement.strip()
                if statement:
                    cursor.execute(statement)
                    # Fetch all results for statements that return rows
                    if cursor.with_rows:
                        rows = cursor.fetchall()
                        results.append(rows)
                    # Consume any additional result sets (rare for simple statements)
                    while cursor.nextset():
                        if cursor.with_rows:
                            cursor.fetchall()
            self.__connection.commit()

            # Return the last result set that actually has data, if any
            for result in reversed(results):
                if result:
                    return result
            return None

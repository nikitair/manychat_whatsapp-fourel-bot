import sys
import psycopg2
from config.logging_config import logger


class PostgresHandler:

    def __init__(self, database: str, user: str, password: str, host: str, port: int):
        self.database = database
        self.user = user
        self.password = password
        self.host = host
        self.port = port

        self.connection = None
        logger.debug(f"({self.__class__.__name__}) - CLASS INITIALIZED")

    def __str__(self) -> str:
        return f"{self.__class__.__name__} ({self.database})"

    def __repr__(self) -> str:
        return f"{self.__class__.__name__} ({self.database})"

    def connect(self):
        try:
            self.connection = psycopg2.connect(
                    dbname=self.database,
                    user=self.user,
                    password=self.password,
                    host=self.host,
                    port=self.port
                )
            logger.info(f"({self.__class__.__name__}) - CONNECTED TO Postgres DATABASE")
        except Exception as ex:
            logger.exception(f"({self.__class__.__name__}) - !!! FAILED CONNECTING TO Postgres DATABASE - {ex}")

    def disconnect(self):
        if self.connection:
            self.connection.close()
            logger.info(f"({self.__class__.__name__}) - CLOSED Postgres DATABASE CONNECTION")

    def execute_with_connection(self, func, *args, **kwargs):
        try:
            self.connect()
            result = func(*args, **kwargs)
            return result
        finally:
            self.disconnect()

    def select_executor(self, query: str, params: list = []):
        logger.debug(
            f"({self.__class__.__name__}) - EXECUTING SELECT QUERY: {query} - PARAMS: {params}")

        data = None

        try:
            cursor = self.connection.cursor()
            cursor.execute(query, tuple(params))
            data = cursor.fetchall()
            logger.debug(f"({self.__class__.__name__}) - SQL RESULT: {data}")

        except Exception as ex:
            logger.exception(
                f"({self.__class__.__name__}) - !!! FAILED EXECUTING SQL QUERY - {ex}")

        finally:
            return data

    def insert_executor(self, query: str, params: list[tuple]):
        logger.debug(
            f"({self.__class__.__name__}) - EXECUTING INSERT QUERY: {query} - INSERT PARAMS: {params}")

        cursor = None
        try:
            cursor = self.connection.cursor()
            cursor.executemany(query, params)
            self.connection.commit()
            logger.info(f"({self.__class__.__name__}) - INSERT SUCCESSFUL")

        except Exception as ex:
            self.connection.rollback()
            logger.exception(
                f"({self.__class__.__name__}) - !!! FAILED INSERTION - {ex}")
        else:
            return True
        finally:
            if cursor:
                cursor.close()

    def delete_executor(self, query: str, params: list, safe: bool = True):
        logger.warning(
            f"({self.__class__.__name__}) - EXECUTING DELETE QUERY: {query} - PARAMS: {params}")

        user_answer = 'y'

        if safe:
            user_answer = input("! Confirm Deletion [y / n] >> ")

        if user_answer.strip().lower() == 'y':
            cursor = None
            try:
                cursor = self.connection.cursor()
                cursor.execute(query, params)
                self.connection.commit()
                logger.info(f"({self.__class__.__name__}) - DELETE SUCCESSFUL")

            except Exception as ex:
                self.connection.rollback()
                logger.exception(
                    f"({self.__class__.__name__}) - !!! FAILED DELETION - {ex}")

            finally:
                cursor.close()
        else:
            sys.stdout.write("Aborted Deletion")

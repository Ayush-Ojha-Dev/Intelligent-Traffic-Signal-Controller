"""
database/oracle.py

Oracle Database connection for the
Intelligent Traffic Signal Controller.

Oracle runs in Docker and exposes FREEPDB1
on localhost:1521.
"""

import os

import oracledb
from dotenv import load_dotenv

load_dotenv()

ORACLE_USER = os.getenv("ORACLE_USER")
ORACLE_PASSWORD = os.getenv("ORACLE_PASSWORD")
ORACLE_DSN = os.getenv("ORACLE_DSN")


class OracleConnection:
    def __init__(self):
        self.user = ORACLE_USER
        self.password = ORACLE_PASSWORD
        self.dsn = ORACLE_DSN

        if not self.user:
            raise ValueError("ORACLE_USER is not configured")

        if not self.password:
            raise ValueError("ORACLE_PASSWORD is not configured")

        if not self.dsn:
            raise ValueError("ORACLE_DSN is not configured")

    def get_connection(self):
        return oracledb.connect(
            user=self.user,
            password=self.password,
            dsn=self.dsn,
        )

    def fetch_all(self, query: str, params: dict | None = None):
        connection = self.get_connection()

        try:
            with connection.cursor() as cursor:
                cursor.execute(query, params or {})

                columns = [
                    column[0].lower()
                    for column in cursor.description
                ]

                return [
                    dict(zip(columns, row))
                    for row in cursor.fetchall()
                ]

        finally:
            connection.close()

    def execute(self, query: str, params: dict | None = None):
        connection = self.get_connection()

        try:
            with connection.cursor() as cursor:
                cursor.execute(query, params or {})
                connection.commit()

        finally:
            connection.close()

    def execute_plsql(
        self,
        statement: str,
        params: dict | None = None
    ):
        connection = self.get_connection()

        try:
            with connection.cursor() as cursor:
                cursor.execute(statement, params or {})
                connection.commit()

        finally:
            connection.close()

    def close(self):
        pass


oracle_conn = OracleConnection()

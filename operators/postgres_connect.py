"""
Connects to the Postgres database
"""

from secrets import dbname, host, pg_password, pg_user, port

import psycopg2


class ConnectPostgres:
    def __init__(self):
        self.host = host
        self.port = port
        self.dbname = dbname
        self.pg_user = pg_user
        self.pg_password = pg_password

    def postgres_connector(self):
        conn = psycopg2.connect(
            f"host='{self.host}' port='{self.port}' dbname='{self.dbname}' user='{self.pg_user}' password='{self.pg_password}'"
        )
        return conn


if __name__ == "__main__":
    conn = ConnectPostgres()
    conn.postgres_connector()

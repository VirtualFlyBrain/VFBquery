"""Shared FlyBase Chado database connection helper."""
import psycopg


FLYBASE_DB = {
    "host": "chado.flybase.org",
    "dbname": "flybase",
    "user": "flybase",
    "password": "flybase",
    "connect_timeout": 10,
}


def get_connection(statement_timeout_ms=60000):
    """Get a connection to FlyBase Chado with statement timeout.

    :param statement_timeout_ms: SQL statement timeout in milliseconds (default 60s)
    :return: psycopg connection
    """
    return psycopg.connect(
        **FLYBASE_DB,
        options=f"-c statement_timeout={statement_timeout_ms}",
    )

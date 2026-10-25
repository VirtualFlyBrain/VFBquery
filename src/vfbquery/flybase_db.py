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

    The timeout is applied with ``set_config`` after connecting. Passing it as a
    startup option (``options="-c statement_timeout=..."``) has no effect on
    chado.flybase.org: sessions keep the ``chado_public`` role's 120s default,
    so every caller's requested timeout was silently ignored (2026-10). The
    setting is committed straight away so a later rollback can't revert it.

    :param statement_timeout_ms: SQL statement timeout in milliseconds (default 60s)
    :return: psycopg connection
    """
    conn = psycopg.connect(**FLYBASE_DB)
    try:
        conn.execute("SELECT set_config('statement_timeout', %s, false)",
                     (str(int(statement_timeout_ms)),))
        conn.commit()
    except BaseException:
        conn.close()
        raise
    return conn


def is_connection_error(exc):
    """True if ``exc`` means Chado was unreachable, not that a query failed.

    Callers that degrade gracefully to an empty result on error must still let an
    outage propagate — an outage silently degraded to "no data" masquerades as a
    genuine empty result (and, in tests, as a real defect rather than the skip an
    outage should be). ``psycopg`` raises ``OperationalError`` (and its
    ``ConnectionTimeout`` subclass) for connect failures; the test shim raises a
    builtin ``ConnectionError``.
    """
    if isinstance(exc, ConnectionError):
        return True
    try:
        if isinstance(exc, psycopg.OperationalError):
            return True
    except Exception:
        pass
    if type(exc).__name__ in {"ConnectionTimeout", "OperationalError",
                              "InterfaceError"}:
        return True
    msg = str(exc).lower()
    return any(m in msg for m in (
        "connection timeout expired", "could not connect to server",
        "connection to server at", "server closed the connection",
        "connection refused", "connection reset", "chado unreachable",
    ))

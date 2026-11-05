"""Shared FlyBase Chado database connection helper."""
import os
import warnings

import psycopg


FLYBASE_DB = {
    "host": "chado.flybase.org",
    "dbname": "flybase",
    "user": "flybase",
    "password": "flybase",
    "connect_timeout": 10,
}

# VFB's own copy of FlyBase Chado, public on 443 (Postgres 17 direct SSL; needs libpq >= 17, which psycopg[binary]
# bundles), then FlyBase's server. FB_CHADO_HOST overrides the list (comma-separated host or host:port).
DEFAULT_CHADO_HOSTS = "chado.flybase.virtualflybrain.org:443,chado.flybase.org"


def chado_hosts():
    hosts = os.environ.get("FB_CHADO_HOST", "") or DEFAULT_CHADO_HOSTS
    return [h.strip() for h in hosts.split(",") if h.strip()]


def _conn_args(entry):
    host, _, port = entry.partition(":")
    args = dict(FLYBASE_DB, host=host)
    if port:
        args["port"] = int(port)
    if port == "443":   # SNI-routed TLS on 443: TLS straight away, no Postgres SSLRequest round trip
        args.update(sslmode="require", sslnegotiation="direct")
    return args


def _connect():
    """Connect to the first server in chado_hosts() that accepts the connection."""
    hosts = chado_hosts()
    for i, entry in enumerate(hosts):
        try:
            return psycopg.connect(**_conn_args(entry))
        except psycopg.Error as e:
            if i == len(hosts) - 1:
                raise
            warnings.warn("Chado at %s unavailable (%s); trying %s"
                          % (entry, str(e).strip().splitlines()[0] if str(e).strip() else type(e).__name__, hosts[i + 1]))


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
    conn = _connect()
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

"""Shared pytest setup for the test suite.

The Neo4j fail-fast defaults these tests need live in ``src/test/__init__.py``
rather than here, because not every job runs pytest — the conda workflow drives
the suite through ``unittest``, which imports ``src.test.<module>`` and never
reads a conftest. Importing the package is the one thing both runners do.

This file re-applies them anyway, so the settings do not depend on pytest having
imported the parent package first. It is a no-op when it has, because the
underlying call uses ``os.environ.setdefault``.
"""
try:
    from . import apply_test_neo4j_defaults
except ImportError:  # collected without the package, e.g. rootdir-relative
    import os

    def apply_test_neo4j_defaults():
        for name, value in {
            "VFBQUERY_NEO4J_CONNECT_TIMEOUT_S": "10",
            "VFBQUERY_NEO4J_READ_TIMEOUT_S": "45",
            "VFBQUERY_NEO4J_MAX_RETRIES": "1",
            "VFBQUERY_NEO4J_RETRY_BACKOFF_S": "2",
            "VFBQUERY_NEO4J_CONNECTION_TEST_TIMEOUT_S": "10",
        }.items():
            os.environ.setdefault(name, value)


apply_test_neo4j_defaults()

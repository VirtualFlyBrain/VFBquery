"""Test package for VFBquery.

This file exists to hold one piece of setup: the Neo4j client's fail-fast
settings for tests. It lives here rather than in ``conftest.py`` because
``conftest.py`` is a pytest mechanism, and not every job runs pytest — the
conda workflow runs the suite through ``unittest``, which imports
``src.test.<module>`` and never looks at a conftest. When these defaults were
in conftest only, that job kept the library's REPL-tuned patience and a single
statement against a stalled upstream cost 120s x 4 attempts; one test measured
582s against its own 120s threshold for that reason alone. Importing the
package is the one thing both runners are guaranteed to do.

The settings are read at import time by ``vfbquery.neo4j_client``, and this
module is imported before any test module in the package, so they are in place
before the client's module-level constants are evaluated.
"""
import os

#: Fail-fast Neo4j settings for tests. Deliberately much tighter than the
#: library defaults (120s read, 3 retries): a healthy query against production
#: returns in a couple of seconds, so 45s is already far beyond normal, and one
#: retry is enough to ride out a dropped connection without turning a dead
#: upstream into minutes of waiting per statement.
#:
#: ``setdefault``, not assignment — a workflow or a developer that has set one
#: of these deliberately keeps it.
TEST_NEO4J_DEFAULTS = {
    "VFBQUERY_NEO4J_CONNECT_TIMEOUT_S": "10",
    "VFBQUERY_NEO4J_READ_TIMEOUT_S": "45",
    "VFBQUERY_NEO4J_MAX_RETRIES": "1",
    "VFBQUERY_NEO4J_RETRY_BACKOFF_S": "2",
    "VFBQUERY_NEO4J_CONNECTION_TEST_TIMEOUT_S": "10",
}


def apply_test_neo4j_defaults():
    """Set the fail-fast Neo4j environment defaults, leaving any already set."""
    for name, value in TEST_NEO4J_DEFAULTS.items():
        os.environ.setdefault(name, value)


apply_test_neo4j_defaults()

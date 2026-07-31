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

#: Fail-fast Neo4j settings for tests. Tighter than the library defaults
#: (120s read, 3 retries), because one retry is enough to ride out a dropped
#: connection without turning a dead upstream into minutes of waiting per
#: statement.
#:
#: The read timeout is 180s rather than the 45s first used here. 45s was
#: chosen on the assumption that a healthy query returns in a couple of
#: seconds, which is true of most of them and not true of the class-level
#: connectivity queries: ``get_downstream_class_connectivity('FBbt_00001482')``
#: is measured at 106s against a healthy production server, returning 9,095
#: rows. Those tests pass ``force_refresh=True`` and run with the cache
#: disabled, so every one of them pays that in full — under 45s they did not
#: time out so much as report an empty table, and nine of them failed on
#: assertions about rows that had simply never arrived. The tight value was
#: also invisible until recently: the client used to freeze its constants at
#: import, so this file's settings never reached the queries at all.
#:
#: A stalled server is still bounded — 180s x 2 attempts, and the client now
#: sends ``max-execution-time`` so the server abandons the work as well.
#:
#: ``setdefault``, not assignment — a workflow or a developer that has set one
#: of these deliberately keeps it.
TEST_NEO4J_DEFAULTS = {
    "VFBQUERY_NEO4J_CONNECT_TIMEOUT_S": "10",
    "VFBQUERY_NEO4J_READ_TIMEOUT_S": "180",
    "VFBQUERY_NEO4J_MAX_RETRIES": "1",
    "VFBQUERY_NEO4J_RETRY_BACKOFF_S": "2",
    "VFBQUERY_NEO4J_CONNECTION_TEST_TIMEOUT_S": "10",
}


def apply_test_neo4j_defaults():
    """Set the fail-fast Neo4j environment defaults, leaving any already set."""
    for name, value in TEST_NEO4J_DEFAULTS.items():
        os.environ.setdefault(name, value)


apply_test_neo4j_defaults()

"""Shared setup for the integration test suite.

The one job here is to make the Neo4j client fail fast under test. The library's
defaults are tuned for a person at a REPL, who would rather wait than be told to
try again; a CI job wants the opposite. The upstream at
pdb.virtualflybrain.org intermittently stops answering for minutes at a time,
and with the library defaults a single statement caught in that can spend
several minutes retrying before it gives up — multiplied across the connectivity
suite, that is the difference between a job that fails in a readable way and one
the runner kills at its own ceiling with nothing to show for it.

These are read at import time by ``vfbquery.neo4j_client``, so they are set
here — conftest is imported before any test module — and only when not already
set, so a workflow or a developer can still override them from the environment.
"""
import os

#: Fail-fast Neo4j settings for tests. Deliberately much tighter than the
#: library defaults (120s read, 3 retries): a healthy connectivity query against
#: production returns in a couple of seconds, so 45s is already far beyond
#: normal, and one retry is enough to ride out a dropped connection without
#: turning a dead upstream into minutes of waiting per statement.
_TEST_NEO4J_DEFAULTS = {
    "VFBQUERY_NEO4J_CONNECT_TIMEOUT_S": "10",
    "VFBQUERY_NEO4J_READ_TIMEOUT_S": "45",
    "VFBQUERY_NEO4J_MAX_RETRIES": "1",
    "VFBQUERY_NEO4J_RETRY_BACKOFF_S": "2",
    "VFBQUERY_NEO4J_CONNECTION_TEST_TIMEOUT_S": "10",
}

for _name, _value in _TEST_NEO4J_DEFAULTS.items():
    os.environ.setdefault(_name, _value)

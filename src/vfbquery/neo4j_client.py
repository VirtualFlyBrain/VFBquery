"""
Lightweight Neo4j REST client.

This module provides a minimal Neo4j client extracted from vfb_connect
to avoid loading heavy GUI dependencies (navis, vispy, matplotlib, etc.)
that come with the full vfb_connect package.

Based on vfb_connect.neo.neo4j_tools.Neo4jConnect
"""

import os
import requests
import json
import time


def _env_float(name, default):
    """Read a float from the environment, ignoring anything unparseable."""
    try:
        return float(os.environ.get(name, "") or default)
    except (TypeError, ValueError):
        return default


#: Every setting below is a *fallback*, used only when the corresponding
#: environment variable is unset. They are resolved in :meth:`Neo4jConnect.__init__`,
#: not at import time, and that distinction matters: ``src/__init__.py`` does
#: ``from vfbquery import *``, so importing anything under ``src.test`` imports
#: this module first. Frozen-at-import constants meant a test package could not
#: set its own timeouts — the values were already read — and the conda job kept
#: the REPL-tuned defaults no matter what the suite asked for. Reading at
#: construction also makes the settings genuinely live: change the environment
#: and the next connection picks it up.

#: Seconds to wait for the TCP connect. Short: an unreachable host should fail
#: immediately rather than sit in the pool.
CONNECT_TIMEOUT_S = 10.0

#: Seconds to wait for the *first byte* of a response. This is the number that
#: keeps a stalled server from hanging a caller forever.
#:
#: ``requests`` defaults to no timeout at all, which means a socket that is open
#: but silent blocks the calling thread indefinitely. pdb.virtualflybrain.org
#: does exactly that under load — it accepts the connection and then returns
#: nothing for minutes — so without this a single blip turns a seven-minute CI
#: job into one that is still running when the runner's two-hour ceiling kills
#: it. Raise it with ``VFBQUERY_NEO4J_READ_TIMEOUT_S`` for a genuinely long
#: analytical query; lower it in CI to fail fast.
READ_TIMEOUT_S = 120.0

#: How many times a request is retried after a connection-level failure.
#:
#: This used to be unbounded: the exception handler slept ten seconds and
#: re-entered ``commit_list`` recursively, so a server that was down stayed in
#: that loop until something else killed the process (and grew the Python stack
#: one frame per attempt while it did). Retrying is still right — the endpoint
#: does drop the occasional connection — but it has to end.
MAX_RETRIES = 3

#: Seconds to wait before the first retry; doubled for each subsequent one.
RETRY_BACKOFF_S = 2.0

#: Ceiling for the connection test run during construction. It only decides
#: which transaction API the server speaks, so it must not inherit the query
#: path's patience — see :meth:`Neo4jConnect._probe`.
CONNECTION_TEST_TIMEOUT_S = 15.0

#: Transaction endpoints, newest first. VFB production speaks the first.
V4_COMMIT_PATH = "/db/neo4j/tx/commit"
V4_HEADERS = {'Content-type': 'application/json'}
V3_COMMIT_PATH = "/db/data/transaction/commit"
V3_HEADERS = {}


def dict_cursor(results):
    """
    Takes JSON results from a neo4j query and turns them into a list of dicts.
    
    :param results: neo4j query results
    :return: list of dicts
    """
    dc = []
    if not results or not hasattr(results, '__iter__'):
        return dc
    for n in results:
        # Add conditional to skip any failures
        if n:
            for d in n['data']:
                dc.append(dict(zip(n['columns'], d['row'])))
    return dc


class Neo4jConnect:
    """
    Thin layer over Neo4j REST API to handle connections and queries.
    
    :param endpoint: Neo4j REST endpoint (default: VFB production server)
    :param usr: username for authentication
    :param pwd: password for authentication
    """
    
    def __init__(self,
                 endpoint: str = "http://pdb.virtualflybrain.org",
                 usr: str = "neo4j",
                 pwd: str = "vfb",
                 connect_timeout: float = None,
                 read_timeout: float = None):
        self.base_uri = endpoint
        self.usr = usr
        self.pwd = pwd
        # Resolved here, not at import time — see the note above the constants.
        # An explicit argument still wins over the environment.
        self.connect_timeout = (
            _env_float("VFBQUERY_NEO4J_CONNECT_TIMEOUT_S", CONNECT_TIMEOUT_S)
            if connect_timeout is None else connect_timeout
        )
        self.read_timeout = (
            _env_float("VFBQUERY_NEO4J_READ_TIMEOUT_S", READ_TIMEOUT_S)
            if read_timeout is None else read_timeout
        )
        self.max_retries = int(_env_float("VFBQUERY_NEO4J_MAX_RETRIES", MAX_RETRIES))
        self.retry_backoff = _env_float("VFBQUERY_NEO4J_RETRY_BACKOFF_S", RETRY_BACKOFF_S)
        self.connection_test_timeout = _env_float(
            "VFBQUERY_NEO4J_CONNECTION_TEST_TIMEOUT_S", CONNECTION_TEST_TIMEOUT_S
        )
        self.commit = V4_COMMIT_PATH
        self.headers = dict(V4_HEADERS)

        # Work out which transaction API this server speaks. Only a definitive
        # negative answer — the server replied, and said no — is grounds for
        # falling back to v3. A timeout is not an answer: the server being slow
        # says nothing about which API it speaks, and treating it as a "no" used
        # to send construction down the v3 path and then raise, so a transient
        # stall failed the caller outright instead of letting the query's own
        # bounded retry ride it out.
        status = self._probe(V4_COMMIT_PATH, V4_HEADERS)
        if status == "wrong-api":
            print("Falling back to Neo4j v3 connection")
            if self._probe(V3_COMMIT_PATH, V3_HEADERS) == "ok":
                self.commit = V3_COMMIT_PATH
                self.headers = dict(V3_HEADERS)
            else:
                raise Exception("Failed to connect to Neo4j.")
        elif status == "unreachable":
            print(
                f"\033[33mWarning:\033[0m {self.base_uri} did not answer within "
                f"{min(self.connect_timeout, self.connection_test_timeout):.0f}s; "
                "assuming the Neo4j 4+ transaction API and continuing."
            )
    
    def commit_list(self, statements, return_graphs=False):
        """
        Commit a list of Cypher statements to Neo4j via REST API.
        
        :param statements: A list of Cypher statements
        :param return_graphs: If True, returns graphs under 'graph' key
        :return: List of results or False if errors encountered
        """
        cstatements = []
        if return_graphs:
            for s in statements:
                cstatements.append({'statement': s, "resultDataContents": ["row", "graph"]})
        else:
            for s in statements:
                cstatements.append({'statement': s})
        
        payload = {'statements': cstatements}

        max_retries = getattr(self, "max_retries", MAX_RETRIES)
        delay = getattr(self, "retry_backoff", RETRY_BACKOFF_S)
        for attempt in range(max_retries + 1):
            try:
                response = requests.post(
                    url=f"{self.base_uri}{self.commit}",
                    auth=(self.usr, self.pwd),
                    data=json.dumps(payload),
                    headers=self.headers,
                    timeout=(self.connect_timeout, self.read_timeout),
                )
            except requests.exceptions.RequestException as e:
                if attempt >= max_retries:
                    print(f"\033[31mConnection Error:\033[0m {e}")
                    print(
                        f"Giving up after {max_retries + 1} attempt(s) "
                        f"(read timeout {self.read_timeout}s)."
                    )
                    return False
                print(f"\033[31mConnection Error:\033[0m {e}")
                print(
                    f"Retrying in {delay:.0f}s "
                    f"(attempt {attempt + 2} of {max_retries + 1})..."
                )
                time.sleep(delay)
                delay *= 2
                continue

            if self.rest_return_check(response):
                return response.json()['results']
            return False

        return False
    
    def rest_return_check(self, response):
        """
        Check status response and report errors.
        
        :param response: requests.Response object
        :return: True if OK and no errors, False otherwise
        """
        if response.status_code != 200:
            print(f"\033[31mConnection Error:\033[0m {response.status_code} ({response.reason})")
            return False
        else:
            j = response.json()
            if j['errors']:
                for e in j['errors']:
                    print(f"\033[31mQuery Error:\033[0m {e}")
                return False
            else:
                return True
    
    def _probe(self, commit_path, headers):
        """Ask one transaction endpoint whether it is there and speaks Cypher.

        Returns ``"ok"``, ``"wrong-api"`` (the server answered, and the answer
        was no) or ``"unreachable"`` (it did not answer in time). Keeping those
        two failures apart is the whole point: only the first is a reason to
        try a different endpoint.

        This runs on every construction, so it must not inherit the query
        path's patience or its retries — with those, a stalled server would
        cost minutes here, twice, before the caller saw a real query. It also
        no longer scans for a node (``MATCH (n) RETURN n LIMIT 1``); ``RETURN
        1`` answers the only question being asked.
        """
        cap = getattr(self, "connection_test_timeout", CONNECTION_TEST_TIMEOUT_S)
        timeout = (min(self.connect_timeout, cap), min(self.read_timeout, cap))
        try:
            response = requests.post(
                url=f"{self.base_uri}{commit_path}",
                auth=(self.usr, self.pwd),
                data=json.dumps({'statements': [{'statement': 'RETURN 1'}]}),
                headers=headers,
                timeout=timeout,
            )
        except requests.exceptions.RequestException as e:
            print(f"\033[31mConnection Error:\033[0m {e}")
            return "unreachable"

        if response.status_code != 200:
            print(f"\033[31mConnection Error:\033[0m "
                  f"{response.status_code} ({response.reason})")
            return "wrong-api"
        try:
            return "wrong-api" if response.json().get('errors') else "ok"
        except ValueError:
            return "wrong-api"

    def test_connection(self):
        """True if the endpoint this instance is bound to answers ``RETURN 1``."""
        return self._probe(self.commit, self.headers) == "ok"

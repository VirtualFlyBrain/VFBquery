"""
Lightweight Neo4j REST client.

This module provides a minimal Neo4j client extracted from vfb_connect
to avoid loading heavy GUI dependencies (navis, vispy, matplotlib, etc.)
that come with the full vfb_connect package.

Based on vfb_connect.neo.neo4j_tools.Neo4jConnect
"""

import requests
import json
import time


def dict_cursor(results):
    """
    Takes JSON results from a neo4j query and turns them into a list of dicts.
    
    :param results: neo4j query results
    :return: list of dicts
    """
    dc = []
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
                 pwd: str = "vfb"):
        self.base_uri = endpoint
        self.usr = usr
        self.pwd = pwd
        self.commit = "/db/neo4j/tx/commit"
        self.headers = {'Content-type': 'application/json'}
        
        # Test connection and fall back to v3 API if needed
        if not self.test_connection():
            print("Falling back to Neo4j v3 connection")
            self.commit = "/db/data/transaction/commit"
            self.headers = {}
            if not self.test_connection():
                raise Exception("Failed to connect to Neo4j.")
    
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
        
        try:
            response = requests.post(
                url=f"{self.base_uri}{self.commit}",
                auth=(self.usr, self.pwd),
                data=json.dumps(payload),
                headers=self.headers
            )
        except requests.exceptions.RequestException as e:
            print(f"\033[31mConnection Error:\033[0m {e}")
            print("Retrying in 10 seconds...")
            time.sleep(10)
            return self.commit_list(statements)
        
        if self.rest_return_check(response):
            return response.json()['results']
        else:
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
    
    def test_connection(self):
        """Test neo4j endpoint connection"""
        statements = ["MATCH (n) RETURN n LIMIT 1"]
        if self.commit_list(statements):
            return True
        else:
            return False

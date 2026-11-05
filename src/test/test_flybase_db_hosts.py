import os
import unittest
from unittest import mock

import psycopg

from vfbquery import flybase_db


class TestChadoHosts(unittest.TestCase):

    def test_default_is_vfb_then_flybase(self):
        with mock.patch.dict(os.environ, {}, clear=True):
            self.assertEqual(["chado.flybase.virtualflybrain.org:443", "chado.flybase.org"], flybase_db.chado_hosts())

    def test_port_443_uses_direct_ssl(self):
        a = flybase_db._conn_args("chado.flybase.virtualflybrain.org:443")
        self.assertEqual(("chado.flybase.virtualflybrain.org", 443, "require", "direct"),
                         (a["host"], a["port"], a["sslmode"], a["sslnegotiation"]))
        self.assertNotIn("sslmode", flybase_db._conn_args("chado.flybase.org"))

    def test_falls_back_to_next_host(self):
        calls = []

        def connect(**kw):
            calls.append(kw["host"])
            if kw["host"] != "chado.flybase.org":
                raise psycopg.OperationalError("connection refused")
            return "conn"

        with mock.patch.dict(os.environ, {}, clear=True), mock.patch.object(flybase_db.psycopg, "connect", side_effect=connect):
            self.assertEqual("conn", flybase_db._connect())
        self.assertEqual(["chado.flybase.virtualflybrain.org", "chado.flybase.org"], calls)


if __name__ == "__main__":
    unittest.main()

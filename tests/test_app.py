import pathlib
import unittest
from pathlib import PosixPath

import hishel

from mightstone import Mightstone


class TestAppClass(unittest.TestCase):
    def test_singleton_on_two_distinct_app(self):
        m = Mightstone({"storage": {"implementation": "fake"}})
        self.assertEqual(m.config.http.cache.directory, None)
        self.assertIsInstance(m.cache_transport, hishel.AsyncCacheTransport)
        self.assertIsInstance(m.cache_transport._storage._base_path, pathlib.Path)
        self.assertIn("Mightstone/http", str(m.cache_transport._storage._base_path))

        m2 = Mightstone(
            {
                "storage": {"implementation": "fake"},
                "http": {"cache": {"directory": pathlib.Path("/tmp/tata")}},
            }
        )
        self.assertIsInstance(m2.config.http.cache.directory, PosixPath)
        self.assertEqual(m2.config.http.cache.directory, PosixPath("/tmp/tata"))

        self.assertEqual(m2.cache_transport._storage._base_path, PosixPath("/tmp/tata"))

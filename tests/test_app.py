import pathlib
import unittest
from pathlib import PosixPath
from unittest.mock import patch

import httpx_cache
from mongomock_motor import AsyncMongoMockClient

from mightstone import Mightstone
from mightstone.config import MainSettings


class TestAppClass(unittest.TestCase):
    def test_singleton_on_two_distinct_app(self):
        m = Mightstone({"storage": {"implementation": "fake"}})
        self.assertEqual(m.config.http.cache.directory, None)
        self.assertIsInstance(m.cache_transport, httpx_cache.AsyncCacheControlTransport)
        self.assertIsInstance(m.cache_transport.cache.cache_dir, pathlib.Path)
        self.assertIn("Mightstone/http", str(m.cache_transport.cache.cache_dir))

        m2 = Mightstone(
            {
                "storage": {"implementation": "fake"},
                "http": {"cache": {"directory": pathlib.Path("/tmp/tata")}},
            }
        )
        self.assertIsInstance(m2.config.http.cache.directory, PosixPath)
        self.assertEqual(m2.config.http.cache.directory, PosixPath("/tmp/tata"))

        self.assertEqual(m2.cache_transport.cache.cache_dir, PosixPath("/tmp/tata"))

import pathlib
import unittest
from pathlib import PosixPath

import httpx_cache

from mightstone import Mightstone
from mightstone.config import MainSettings


class TestAppClass(unittest.TestCase):
    def test_singleton_on_two_distinct_app(self):
        m = Mightstone()
        self.assertEqual(m.app.config.get("http.cache.directory"), None)
        self.assertIsInstance(
            m.app.httpx.cache_transport(), httpx_cache.AsyncCacheControlTransport
        )
        self.assertIsInstance(
            m.app.httpx.cache_transport().cache.cache_dir, pathlib.Path
        )
        self.assertIn(
            "Mightstone/http", str(m.app.httpx.cache_transport().cache.cache_dir)
        )

        m2 = Mightstone(
            config=MainSettings.model_validate(
                {"http": {"cache": {"directory": pathlib.Path("/tmp/tata")}}}
            )
        )
        self.assertIsInstance(m2.app.config.get("http.cache.directory"), PosixPath)
        self.assertEqual(
            m2.app.config.get("http.cache.directory"), PosixPath("/tmp/tata")
        )

        self.assertEqual(
            m2.app.httpx.cache_transport().cache.cache_dir, PosixPath("/tmp/tata")
        )

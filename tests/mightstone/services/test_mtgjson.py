import datetime
import unittest

import pytest
from packaging import version

from mightstone.services.mtgjson import MtgJson, MtgJsonCompression


class MtgJsonTest(unittest.TestCase):
    def test_no_compression(self):
        m = MtgJson(compression=MtgJsonCompression.NONE, cache=None)

        self.assertEqual(m.compression, MtgJsonCompression.NONE)

    def test_zip_compression(self):
        m = MtgJson(compression=MtgJsonCompression.ZIP, cache=None)

        self.assertEqual(m.compression, MtgJsonCompression.ZIP)


@pytest.mark.asyncio
class TestMtgJsonRealTest(unittest.IsolatedAsyncioTestCase):
    async def test_meta_uncompressed_no_cache(self):
        m = MtgJson(compression=MtgJsonCompression.NONE, cache=None)
        meta = await m.meta()

        self.assertIsInstance(meta.date, datetime.date)
        self.assertIsInstance(meta.version, str)
        self.assertGreater(version.parse(meta.version), version.Version("5.2.1"))

    async def test_meta_gzip_compressed_no_cache(self):
        m = MtgJson(compression=MtgJsonCompression.GZIP, cache=None)
        meta = await m.meta()

        self.assertIsInstance(meta.date, datetime.date)
        self.assertIsInstance(meta.version, str)
        self.assertGreater(version.parse(meta.version), version.Version("5.2.1"))

    async def test_meta_xz_compressed_no_cache(self):
        m = MtgJson(compression=MtgJsonCompression.XZ, cache=None)
        meta = await m.meta()

        self.assertIsInstance(meta.date, datetime.date)
        self.assertIsInstance(meta.version, str)
        self.assertGreater(version.parse(meta.version), version.Version("5.2.1"))

    async def test_meta_bz2_compressed_no_cache(self):
        m = MtgJson(compression=MtgJsonCompression.BZ2, cache=None)
        meta = await m.meta()

        self.assertIsInstance(meta.date, datetime.date)
        self.assertIsInstance(meta.version, str)
        self.assertGreater(version.parse(meta.version), version.Version("5.2.1"))

    async def test_meta_zip_compressed_no_cache(self):
        m = MtgJson(compression=MtgJsonCompression.ZIP, cache=None)

        with self.assertRaises(ValueError):
            await m.meta()

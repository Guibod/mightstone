import datetime
import unittest

import pytest
from packaging import version

from mightstone.ass import stream_as_list
from mightstone.services.mtgjson import (
    Card,
    CardAtomic,
    CardAtomicGroup,
    CardPrices,
    CardTypes,
    Deck,
    DeckList,
    Keywords,
    MtgJson,
    MtgJsonCompression,
    Set,
    SetList,
)

from . import skip_remote_api  # noqa: F401


class MtgJsonTest(unittest.TestCase):
    def test_no_compression(self):
        m = MtgJson(compression=MtgJsonCompression.NONE, cache=None)

        self.assertEqual(m.compression, MtgJsonCompression.NONE)

    def test_zip_compression(self):
        m = MtgJson(compression=MtgJsonCompression.ZIP, cache=None)

        self.assertEqual(m.compression, MtgJsonCompression.ZIP)


@pytest.mark.asyncio
@pytest.mark.skip_remote_api
class TestMtgJsonRealCompressionTest(unittest.IsolatedAsyncioTestCase):
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


@pytest.mark.skip_remote_api
@pytest.mark.asyncio
class TestMtgJsonRealAllEndpointsTest(unittest.IsolatedAsyncioTestCase):
    async def test_all_printings(self):
        client = MtgJson(cache=None)
        r = stream_as_list(client.all_printings(), 5)

        self.assertEqual(len(r), 5)
        self.assertIsInstance(r[0], Set)
        self.assertIsInstance(r[4], Set)

    async def test_all_identifiers(self):
        client = MtgJson(cache=None)
        r = stream_as_list(client.all_identifiers(), 5)

        self.assertEqual(len(r), 5)
        self.assertIsInstance(r[0], Card)
        self.assertIsInstance(r[4], Card)

    async def test_all_prices(self):
        client = MtgJson(cache=None)
        r = stream_as_list(client.all_prices(), 5)

        self.assertEqual(len(r), 5)
        self.assertIsInstance(r[0], CardPrices)
        self.assertIsInstance(r[4], CardPrices)

    async def test_atomic_cards(self):
        client = MtgJson(cache=None)
        r = stream_as_list(client.atomic_cards(), 5)

        self.assertEqual(len(r), 5)
        self.assertIsInstance(r[0], CardAtomicGroup)
        self.assertIsInstance(r[0].prints[0], CardAtomic)
        self.assertIsInstance(r[4], CardAtomicGroup)

    async def test_card_types(self):
        client = MtgJson(cache=None)
        r: CardTypes = await client.card_types()

        self.assertIsInstance(r, CardTypes)
        self.assertGreater(len(r.artifact.sub_types), 1)
        self.assertGreater(len(r.artifact.super_types), 1)

    async def test_compiled_list(self):
        client = MtgJson(cache=None)
        r = await client.compiled_list()

        self.assertIsInstance(r, list)
        self.assertGreater(len(r), 1)

    async def test_deck_list(self):
        client = MtgJson(cache=None)
        r = stream_as_list(client.deck_list(), 5)

        self.assertEqual(len(r), 5)
        self.assertIsInstance(r[0], DeckList)
        self.assertIsInstance(r[4], DeckList)

    async def test_deck(self):
        client = MtgJson(cache=None)
        r = await client.deck("CorruptingInfluence_ONC")

        self.assertIsInstance(r, Deck)
        self.assertEqual(r.name, "Corrupting Influence")
        self.assertEqual(r.code, "ONC")

    async def test_enum_values(self):
        client = MtgJson(cache=None)
        r = await client.enum_values()

        self.assertIsInstance(r, dict)
        self.assertIn(
            "card",
            r,
        )
        self.assertIn("availability", r["card"])
        self.assertIn("arena", r["card"]["availability"])
        self.assertIn("colors", r["card"])
        self.assertIn("B", r["card"]["colors"])
        self.assertIn("frameVersion", r["card"])

    async def test_keywords(self):
        client = MtgJson(cache=None)
        r = await client.keywords()

        self.assertIsInstance(r, Keywords)
        self.assertIn("Reach", r.keyword_abilities)
        self.assertIn("Landfall", r.ability_words)
        self.assertIn("Learn", r.keyword_actions)

    async def test_legacy(self):
        client = MtgJson(cache=None)
        r = stream_as_list(client.legacy(), 5)

        self.assertEqual(len(r), 5)
        self.assertIsInstance(r[0], Set)
        self.assertIsInstance(r[4], Set)

    async def test_legacy_atomic(self):
        client = MtgJson(cache=None)
        r = stream_as_list(client.legacy_atomic(), 5)

        self.assertEqual(len(r), 5)
        self.assertIsInstance(r[0], CardAtomicGroup)
        self.assertIsInstance(r[0].prints[0], CardAtomic)
        self.assertIsInstance(r[4], CardAtomicGroup)

    async def test_modern(self):
        client = MtgJson(cache=None)
        r = stream_as_list(client.modern(), 5)

        self.assertEqual(len(r), 5)
        self.assertIsInstance(r[0], Set)
        self.assertIsInstance(r[4], Set)

    async def test_modern_atomic(self):
        client = MtgJson(cache=None)
        r = stream_as_list(client.modern_atomic(), 5)

        self.assertEqual(len(r), 5)
        self.assertIsInstance(r[0], CardAtomicGroup)
        self.assertIsInstance(r[0].prints[0], CardAtomic)
        self.assertIsInstance(r[4], CardAtomicGroup)

    async def test_pauper_atomic(self):
        client = MtgJson(cache=None)
        r = stream_as_list(client.pauper_atomic(), 5)

        self.assertEqual(len(r), 5)
        self.assertIsInstance(r[0], CardAtomicGroup)
        self.assertIsInstance(r[0].prints[0], CardAtomic)
        self.assertIsInstance(r[4], CardAtomicGroup)

    async def test_pioneer(self):
        client = MtgJson(cache=None)
        r = stream_as_list(client.pioneer(), 5)

        self.assertEqual(len(r), 5)
        self.assertIsInstance(r[0], Set)
        self.assertIsInstance(r[4], Set)

    async def test_pioneer_atomic(self):
        client = MtgJson(cache=None)
        r = stream_as_list(client.pioneer_atomic(), 5)

        self.assertEqual(len(r), 5)
        self.assertIsInstance(r[0], CardAtomicGroup)
        self.assertIsInstance(r[0].prints[0], CardAtomic)
        self.assertIsInstance(r[4], CardAtomicGroup)

    async def test_set_list(self):
        client = MtgJson(cache=None)
        r = stream_as_list(client.set_list(), 5)

        self.assertEqual(len(r), 5)
        self.assertIsInstance(r[0], SetList)
        self.assertIsInstance(r[4], SetList)

    async def test_set(self):
        client = MtgJson(cache=None)
        result = await client.set("AFR")
        self.assertIsInstance(result, SetList)
        self.assertEqual(result.name, "Adventures in the Forgotten Realms")
        self.assertEqual(result.code, "AFR")
        self.assertEqual(
            result.translations.french,
            "Forgotten Realms: Aventures dans les Royaumes Oubliés",
        )

    async def test_standard(self):
        client = MtgJson(cache=None)
        r = stream_as_list(client.standard(), 5)

        self.assertEqual(len(r), 5)
        self.assertIsInstance(r[0], Set)
        self.assertIsInstance(r[4], Set)

    async def test_standard_atomic(self):
        client = MtgJson(cache=None)
        r = stream_as_list(client.standard_atomic(), 5)

        self.assertEqual(len(r), 5)
        self.assertIsInstance(r[0], CardAtomicGroup)
        self.assertIsInstance(r[0].prints[0], CardAtomic)
        self.assertIsInstance(r[4], CardAtomicGroup)

    async def test_vintage(self):
        client = MtgJson(cache=None)
        r = stream_as_list(client.vintage(), 5)

        self.assertEqual(len(r), 5)
        self.assertIsInstance(r[0], Set)
        self.assertIsInstance(r[4], Set)

    async def test_vintage_atomic(self):
        client = MtgJson(cache=None)
        r = stream_as_list(client.vintage_atomic(), 5)

        self.assertEqual(len(r), 5)
        self.assertIsInstance(r[0], CardAtomicGroup)
        self.assertIsInstance(r[0].prints[0], CardAtomic)
        self.assertIsInstance(r[4], CardAtomicGroup)

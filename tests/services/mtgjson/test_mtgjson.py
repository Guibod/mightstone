import datetime
import os
import unittest

import asyncstdlib
import pytest
from packaging import version

from mightstone.services.mtgjson.api import MtgJson, MtgJsonCompression
from mightstone.services.mtgjson.models import (
    Card,
    CardAtomic,
    CardFace,
    CardPrices,
    CardTypes,
    Deck,
    DeckList,
    Keywords,
    Set,
    SetList,
    TcgPlayerSKUs,
)

from ...testcase import TestBeanie
from .. import skip_remote_api  # noqa: F401


class MtgJsonTest(unittest.TestCase):
    def test_no_compression(self):
        m = MtgJson(
            compression=MtgJsonCompression.NONE,
        )

        self.assertEqual(m.compression, MtgJsonCompression.NONE)

    def test_zip_compression(self):
        m = MtgJson(
            compression=MtgJsonCompression.ZIP,
        )

        self.assertEqual(m.compression, MtgJsonCompression.ZIP)


class MtgJsonData(TestBeanie):
    def test_prices(self):
        card = CardPrices.parse_file(
            os.path.dirname(__file__) + "/samples/cardprices.json"
        )

        buylist = card.paper["cardkingdom"].buylist["foil"]

        self.assertTrue(all([isinstance(k, str) for k in buylist.keys()]))
        self.assertIsInstance(card.json(), str)


@pytest.mark.asyncio
@pytest.mark.skip_remote_api
class TestMtgJsonRealCompressionTest(TestBeanie):
    async def test_meta_uncompressed_no_cache(self):
        m = MtgJson(
            compression=MtgJsonCompression.NONE,
        )
        meta = await m.meta_async()

        self.assertIsInstance(meta.date, datetime.date)
        self.assertIsInstance(meta.version, str)
        self.assertGreater(version.parse(meta.version), version.Version("5.2.1"))

    async def test_meta_gzip_compressed_no_cache(self):
        m = MtgJson(
            compression=MtgJsonCompression.GZIP,
        )
        meta = await m.meta_async()

        self.assertIsInstance(meta.date, datetime.date)
        self.assertIsInstance(meta.version, str)
        self.assertGreater(version.parse(meta.version), version.Version("5.2.1"))

    async def test_meta_xz_compressed_no_cache(self):
        m = MtgJson(
            compression=MtgJsonCompression.XZ,
        )
        meta = await m.meta_async()

        self.assertIsInstance(meta.date, datetime.date)
        self.assertIsInstance(meta.version, str)
        self.assertGreater(version.parse(meta.version), version.Version("5.2.1"))

    async def test_meta_bz2_compressed_no_cache(self):
        m = MtgJson(
            compression=MtgJsonCompression.BZ2,
        )
        meta = await m.meta_async()

        self.assertIsInstance(meta.date, datetime.date)
        self.assertIsInstance(meta.version, str)
        self.assertGreater(version.parse(meta.version), version.Version("5.2.1"))

    async def test_meta_zip_compressed_no_cache(self):
        m = MtgJson(
            compression=MtgJsonCompression.ZIP,
        )

        with self.assertRaises(ValueError):
            await m.meta_async()


@pytest.mark.skip_remote_api
@pytest.mark.asyncio
class TestMtgJsonRealAllEndpointsTest(TestBeanie):
    async def test_all_printings(self):
        client = MtgJson()
        r = [item async for item in asyncstdlib.islice(client.all_printings_async(), 5)]

        self.assertEqual(len(r), 5)
        self.assertIsInstance(r[0], Set)
        self.assertIsInstance(r[4], Set)

    async def test_all_identifiers(self):
        client = MtgJson()
        r = [
            item async for item in asyncstdlib.islice(client.all_identifiers_async(), 5)
        ]

        self.assertEqual(len(r), 5)
        self.assertIsInstance(r[0], Card)
        self.assertIsInstance(r[4], Card)

    async def test_all_prices(self):
        client = MtgJson()
        r = [item async for item in asyncstdlib.islice(client.all_prices_async(), 5)]

        self.assertEqual(len(r), 5)
        self.assertIsInstance(r[0], CardPrices)
        self.assertIsInstance(r[4], CardPrices)

    async def test_atomic_cards(self):
        client = MtgJson()
        r = [item async for item in asyncstdlib.islice(client.atomic_cards_async(), 5)]

        self.assertEqual(len(r), 5)
        self.assertIsInstance(r[0], CardAtomic)
        self.assertIsInstance(r[0].faces[0], CardFace)
        self.assertIsInstance(r[4], CardAtomic)

    async def test_card_types(self):
        client = MtgJson()
        r: CardTypes = await client.card_types_async()

        self.assertIsInstance(r, CardTypes)
        self.assertGreater(len(r.artifact.sub_types), 1)
        self.assertGreater(len(r.artifact.super_types), 1)

    async def test_compiled_list(self):
        client = MtgJson()
        r = await client.compiled_list_async()

        self.assertIsInstance(r, list)
        self.assertGreater(len(r), 1)

    async def test_deck_list(self):
        client = MtgJson()
        r = [item async for item in asyncstdlib.islice(client.deck_list_async(), 5)]

        self.assertEqual(len(r), 5)
        self.assertIsInstance(r[0], DeckList)
        self.assertIsInstance(r[4], DeckList)

    async def test_deck(self):
        client = MtgJson()
        r = await client.deck_async("CorruptingInfluence_ONC")

        self.assertIsInstance(r, Deck)
        self.assertEqual(r.name, "Corrupting Influence")
        self.assertEqual(r.code, "ONC")

    async def test_enum_values(self):
        client = MtgJson()
        r = await client.enum_values_async()

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
        client = MtgJson()
        r = await client.keywords_async()

        self.assertIsInstance(r, Keywords)
        self.assertIn("Reach", r.keyword_abilities)
        self.assertIn("Landfall", r.ability_words)
        self.assertIn("Learn", r.keyword_actions)

    async def test_legacy(self):
        client = MtgJson()
        r = [item async for item in asyncstdlib.islice(client.legacy_async(), 5)]

        self.assertEqual(len(r), 5)
        self.assertIsInstance(r[0], Set)
        self.assertIsInstance(r[4], Set)

    async def test_legacy_atomic(self):
        client = MtgJson()
        r = [item async for item in asyncstdlib.islice(client.legacy_atomic_async(), 5)]

        self.assertEqual(len(r), 5)
        self.assertIsInstance(r[0], CardAtomic)
        self.assertIsInstance(r[0].faces[0], CardFace)
        self.assertIsInstance(r[4], CardAtomic)

    async def test_modern(self):
        client = MtgJson()
        r = [item async for item in asyncstdlib.islice(client.modern_async(), 5)]

        self.assertEqual(len(r), 5)
        self.assertIsInstance(r[0], Set)
        self.assertIsInstance(r[4], Set)

    async def test_modern_atomic(self):
        client = MtgJson()
        r = [item async for item in asyncstdlib.islice(client.modern_atomic_async(), 5)]

        self.assertEqual(len(r), 5)
        self.assertIsInstance(r[0], CardAtomic)
        self.assertIsInstance(r[0].faces[0], CardFace)
        self.assertIsInstance(r[4], CardAtomic)

    async def test_pauper_atomic(self):
        client = MtgJson()
        r = [item async for item in asyncstdlib.islice(client.pauper_atomic_async(), 5)]

        self.assertEqual(len(r), 5)
        self.assertIsInstance(r[0], CardAtomic)
        self.assertIsInstance(r[0].faces[0], CardFace)
        self.assertIsInstance(r[4], CardAtomic)

    async def test_pioneer(self):
        client = MtgJson()
        r = [item async for item in asyncstdlib.islice(client.pioneer_async(), 5)]

        self.assertEqual(len(r), 5)
        self.assertIsInstance(r[0], Set)
        self.assertIsInstance(r[4], Set)

    async def test_pioneer_atomic(self):
        client = MtgJson()
        r = [
            item async for item in asyncstdlib.islice(client.pioneer_atomic_async(), 5)
        ]

        self.assertEqual(len(r), 5)
        self.assertIsInstance(r[0], CardAtomic)
        self.assertIsInstance(r[0].faces[0], CardFace)
        self.assertIsInstance(r[4], CardAtomic)

    async def test_set_list(self):
        client = MtgJson()
        r = [item async for item in asyncstdlib.islice(client.set_list_async(), 5)]

        self.assertEqual(len(r), 5)
        self.assertIsInstance(r[0], SetList)
        self.assertIsInstance(r[4], SetList)

    async def test_set(self):
        client = MtgJson()
        result = await client.set_async("AFR")
        self.assertIsInstance(result, SetList)
        self.assertEqual(result.name, "Adventures in the Forgotten Realms")
        self.assertEqual(result.code, "AFR")

    async def test_standard(self):
        client = MtgJson()
        r = [item async for item in asyncstdlib.islice(client.standard_async(), 5)]

        self.assertEqual(len(r), 5)
        self.assertIsInstance(r[0], Set)
        self.assertIsInstance(r[4], Set)

    async def test_standard_atomic(self):
        client = MtgJson()
        r = [
            item async for item in asyncstdlib.islice(client.standard_atomic_async(), 5)
        ]

        self.assertEqual(len(r), 5)
        self.assertIsInstance(r[0], CardAtomic)
        self.assertIsInstance(r[0].faces[0], CardFace)
        self.assertIsInstance(r[4], CardAtomic)

    async def test_vintage(self):
        client = MtgJson()
        r = [item async for item in asyncstdlib.islice(client.vintage_async(), 5)]

        self.assertEqual(len(r), 5)
        self.assertIsInstance(r[0], Set)
        self.assertIsInstance(r[4], Set)

    async def test_vintage_atomic(self):
        client = MtgJson()
        r = [
            item async for item in asyncstdlib.islice(client.vintage_atomic_async(), 5)
        ]

        self.assertEqual(len(r), 5)
        self.assertIsInstance(r[0], CardAtomic)
        self.assertIsInstance(r[0].faces[0], CardFace)
        self.assertIsInstance(r[4], CardAtomic)

    async def test_tcg_player_skus(self):
        client = MtgJson()
        r = [
            item async for item in asyncstdlib.islice(client.tcg_player_skus_async(), 5)
        ]

        self.assertEqual(len(r), 5)
        self.assertIsInstance(r[0], TcgPlayerSKUs)
        self.assertIsInstance(r[0].skus[0].condition, str)
        self.assertIsInstance(r[4], TcgPlayerSKUs)

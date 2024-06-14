import datetime
import pathlib
import unittest

import asyncstdlib
import pytest
from assertpy import assert_that
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

from .. import skip_remote_api  # noqa: F401


class MtgJsonTest(unittest.TestCase):
    def test_no_compression(self):
        m = MtgJson(
            compression=MtgJsonCompression.NONE,
        )

        assert_that(m.compression).is_equal_to(MtgJsonCompression.NONE)

    def test_zip_compression(self):
        m = MtgJson(
            compression=MtgJsonCompression.ZIP,
        )

        assert_that(m.compression).is_equal_to(MtgJsonCompression.ZIP)


class TestMtgJsonData:
    def test_prices(self):
        f = pathlib.Path(__file__).parent.joinpath("samples/cardprices.json")
        card = CardPrices.model_validate_json(f.read_bytes())

        buylist = card.paper["cardkingdom"].buylist["foil"]

        assert_that(all([isinstance(k, str) for k in buylist.keys()])).is_true()
        assert_that(card.model_dump_json()).is_instance_of(str)


@pytest.mark.asyncio
@pytest.mark.skip_remote_api
class TestMtgJsonRealCompressionTest:
    async def test_meta_uncompressed_no_cache(self):
        m = MtgJson(
            compression=MtgJsonCompression.NONE,
        )
        meta = await m.meta_async()

        assert_that(meta.date).is_instance_of(datetime.date)
        assert_that(meta.version).is_instance_of(str)
        assert_that(version.parse(meta.version) > version.Version("5.2.1")).is_true()

    async def test_meta_gzip_compressed_no_cache(self):
        m = MtgJson(
            compression=MtgJsonCompression.GZIP,
        )
        meta = await m.meta_async()

        assert_that(meta.date).is_instance_of(datetime.date)
        assert_that(meta.version).is_instance_of(str)
        assert_that(version.parse(meta.version) > version.Version("5.2.1")).is_true()

    async def test_meta_xz_compressed_no_cache(self):
        m = MtgJson(
            compression=MtgJsonCompression.XZ,
        )
        meta = await m.meta_async()

        assert_that(meta.date).is_instance_of(datetime.date)
        assert_that(meta.version).is_instance_of(str)
        assert_that(version.parse(meta.version) > version.Version("5.2.1")).is_true()

    async def test_meta_bz2_compressed_no_cache(self):
        m = MtgJson(
            compression=MtgJsonCompression.BZ2,
        )
        meta = await m.meta_async()

        assert_that(meta.date).is_instance_of(datetime.date)
        assert_that(meta.version).is_instance_of(str)
        assert_that(version.parse(meta.version) > version.Version("5.2.1")).is_true()

    async def test_meta_zip_compressed_no_cache(self):
        m = MtgJson(
            compression=MtgJsonCompression.ZIP,
        )

        with pytest.raises(ValueError):
            await m.meta_async()


@pytest.mark.skip_remote_api
@pytest.mark.asyncio
class TestMtgJsonRealAllEndpointsTest:
    async def test_all_printings(self):
        client = MtgJson()
        r = [item async for item in asyncstdlib.islice(client.all_printings_async(), 5)]

        assert_that(len(r)).is_equal_to(5)
        assert_that(r[0]).is_instance_of(Set)
        assert_that(r[4]).is_instance_of(Set)

    async def test_all_identifiers(self):
        client = MtgJson()
        r = [
            item async for item in asyncstdlib.islice(client.all_identifiers_async(), 5)
        ]

        assert_that(len(r)).is_equal_to(5)
        assert_that(r[0]).is_instance_of(Card)
        assert_that(r[4]).is_instance_of(Card)

    async def test_all_prices(self):
        client = MtgJson()
        r = [item async for item in asyncstdlib.islice(client.all_prices_async(), 5)]

        assert_that(len(r)).is_equal_to(5)
        assert_that(r[0]).is_instance_of(CardPrices)
        assert_that(r[4]).is_instance_of(CardPrices)

    async def test_atomic_cards(self):
        client = MtgJson()
        r = [item async for item in asyncstdlib.islice(client.atomic_cards_async(), 5)]

        assert_that(len(r)).is_equal_to(5)
        assert_that(r[0]).is_instance_of(CardAtomic)
        assert_that(r[0].faces[0]).is_instance_of(CardFace)
        assert_that(r[4]).is_instance_of(CardAtomic)

    async def test_card_types(self):
        client = MtgJson()
        r = await client.card_types_async()

        assert_that(r).is_instance_of(CardTypes)
        assert_that(len(r.artifact.sub_types)).is_greater_than(1)
        assert_that(len(r.artifact.super_types)).is_equal_to(5)

    async def test_compiled_list(self):
        client = MtgJson()
        r = await client.compiled_list_async()

        assert_that(r).is_instance_of(list)
        assert_that(len(r)).is_greater_than(1)

    async def test_deck_list(self):
        client = MtgJson()
        r = [item async for item in asyncstdlib.islice(client.deck_list_async(), 5)]

        assert_that(len(r)).is_equal_to(5)
        assert_that(r[0]).is_instance_of(DeckList)
        assert_that(r[4]).is_instance_of(DeckList)

    async def test_deck(self):
        client = MtgJson()
        r = await client.deck_async("CorruptingInfluence_ONC")

        assert_that(r).is_instance_of(Deck)
        assert_that(r.name).is_equal_to("Corrupting Influence")
        assert_that(r.code).is_equal_to("ONC")

    async def test_enum_values(self):
        client = MtgJson()
        r = await client.enum_values_async()

        assert_that(r).is_instance_of(dict)
        assert_that(r).contains("card")
        assert_that(r["card"]).contains("availability")
        assert_that(r["card"]["availability"]).contains("arena")
        assert_that(r["card"]).contains("colors")
        assert_that(r["card"]["colors"]).contains("B")
        assert_that(r["card"]).contains("frameVersion")

    async def test_keywords(self):
        client = MtgJson()
        r = await client.keywords_async()

        assert_that(r).is_instance_of(Keywords)
        assert_that(r.keyword_abilities).contains("Reach")
        assert_that(r.ability_words).contains("Landfall")
        assert_that(r.keyword_actions).contains("Learn")

    async def test_legacy(self):
        client = MtgJson()
        r = [item async for item in asyncstdlib.islice(client.legacy_async(), 5)]

        assert_that(len(r)).is_equal_to(5)
        assert_that(r[0]).is_instance_of(Set)
        assert_that(r[4]).is_instance_of(Set)

    async def test_legacy_atomic(self):
        client = MtgJson()
        r = [item async for item in asyncstdlib.islice(client.legacy_atomic_async(), 5)]

        assert_that(len(r)).is_equal_to(5)
        assert_that(r[0]).is_instance_of(CardAtomic)
        assert_that(r[0].faces[0]).is_instance_of(CardFace)
        assert_that(r[4]).is_instance_of(CardAtomic)

    async def test_modern(self):
        client = MtgJson()
        r = [item async for item in asyncstdlib.islice(client.modern_async(), 5)]

        assert_that(len(r)).is_equal_to(5)
        assert_that(r[0]).is_instance_of(Set)
        assert_that(r[4]).is_instance_of(Set)

    async def test_modern_atomic(self):
        client = MtgJson()
        r = [item async for item in asyncstdlib.islice(client.modern_atomic_async(), 5)]

        assert_that(len(r)).is_equal_to(5)
        assert_that(r[0]).is_instance_of(CardAtomic)
        assert_that(r[0].faces[0]).is_instance_of(CardFace)
        assert_that(r[4]).is_instance_of(CardAtomic)

    async def test_pauper_atomic(self):
        client = MtgJson()
        r = [item async for item in asyncstdlib.islice(client.pauper_atomic_async(), 5)]

        assert_that(len(r)).is_equal_to(5)
        assert_that(r[0]).is_instance_of(CardAtomic)
        assert_that(r[0].faces[0]).is_instance_of(CardFace)
        assert_that(r[4]).is_instance_of(CardAtomic)

    async def test_pioneer(self):
        client = MtgJson()
        r = [item async for item in asyncstdlib.islice(client.pioneer_async(), 5)]

        assert_that(len(r)).is_equal_to(5)
        assert_that(r[0]).is_instance_of(Set)
        assert_that(r[4]).is_instance_of(Set)

    async def test_pioneer_atomic(self):
        client = MtgJson()
        r = [
            item async for item in asyncstdlib.islice(client.pioneer_atomic_async(), 5)
        ]

        assert_that(len(r)).is_equal_to(5)
        assert_that(r[0]).is_instance_of(CardAtomic)
        assert_that(r[0].faces[0]).is_instance_of(CardFace)
        assert_that(r[4]).is_instance_of(CardAtomic)

    async def test_set_list(self):
        client = MtgJson()
        r = [item async for item in asyncstdlib.islice(client.set_list_async(), 5)]

        assert_that(len(r)).is_equal_to(5)
        assert_that(r[0]).is_instance_of(SetList)
        assert_that(r[4]).is_instance_of(SetList)

    async def test_set(self):
        client = MtgJson()
        result = await client.set_async("AFR")
        assert_that(result).is_instance_of(SetList)
        assert_that(result.name).is_equal_to("Adventures in the Forgotten Realms")
        assert_that(result.code).is_equal_to("AFR")

    async def test_standard(self):
        client = MtgJson()
        r = [item async for item in asyncstdlib.islice(client.standard_async(), 5)]

        assert_that(len(r)).is_equal_to(5)
        assert_that(r[0]).is_instance_of(Set)
        assert_that(r[4]).is_instance_of(Set)

    async def test_standard_atomic(self):
        client = MtgJson()
        r = [
            item async for item in asyncstdlib.islice(client.standard_atomic_async(), 5)
        ]

        assert_that(len(r)).is_equal_to(5)
        assert_that(r[0]).is_instance_of(CardAtomic)
        assert_that(r[0].faces[0]).is_instance_of(CardFace)
        assert_that(r[4]).is_instance_of(CardAtomic)

    async def test_vintage(self):
        client = MtgJson()
        r = [item async for item in asyncstdlib.islice(client.vintage_async(), 5)]

        assert_that(len(r)).is_equal_to(5)
        assert_that(r[0]).is_instance_of(Set)
        assert_that(r[4]).is_instance_of(Set)

    async def test_vintage_atomic(self):
        client = MtgJson()
        r = [
            item async for item in asyncstdlib.islice(client.vintage_atomic_async(), 5)
        ]

        assert_that(len(r)).is_equal_to(5)
        assert_that(r[0]).is_instance_of(CardAtomic)
        assert_that(r[0].faces[0]).is_instance_of(CardFace)
        assert_that(r[4]).is_instance_of(CardAtomic)

    async def test_tcg_player_skus(self):
        client = MtgJson()
        r = [
            item async for item in asyncstdlib.islice(client.tcg_player_skus_async(), 5)
        ]

        assert_that(len(r)).is_equal_to(5)
        assert_that(r[0]).is_instance_of(TcgPlayerSKUs)
        assert_that(r[0].skus[0].condition).is_instance_of(str)
        assert_that(r[4]).is_instance_of(TcgPlayerSKUs)

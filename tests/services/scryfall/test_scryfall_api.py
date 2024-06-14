from decimal import Decimal

import asyncstdlib
import pytest
from assertpy import assert_that
from pydantic_core._pydantic_core import Url

from mightstone.services import ServiceError
from mightstone.services.scryfall.api import Scryfall
from mightstone.services.scryfall.models import (
    BulkTagType,
    CardIdentifierPath,
    CatalogType,
    Error,
    SortStrategy,
    UniqueStrategy,
)

from .. import skip_remote_api  # noqa: F401


@pytest.mark.skip_remote_api
@pytest.mark.asyncio(scope="session")
class TestScryfallIntegration:
    async def test_request_set_ikoria(self):
        s = Scryfall()
        model = await s.set_async("IKO")

        assert_that(model.name).is_equal_to("Ikoria: Lair of Behemoths")
        assert_that(model.block_code).is_equal_to(None)
        assert_that(model.uri).is_equal_to(
            Url("https://api.scryfall.com/sets/19feda43-15ab-427e-a0e4-148a4bf2b03a"),
        )

    async def test_request_search_boseiju(self):
        s = Scryfall()
        results = [
            item async for item in s.search_async("boseiju", order=SortStrategy.EUR)
        ]

        assert_that(results[0].name, "Boseiju).is_equal_to( Who Endures")

        assert_that(len(results)).is_equal_to(5)

    async def test_request_search_carpet_unique_art(self):
        s = Scryfall()
        results = [
            item
            async for item in s.search_async(
                "al-abaras-carpet", order=SortStrategy.EUR, unique=UniqueStrategy.ART
            )
        ]

        assert_that(results[0].name).is_equal_to("Al-abara's Carpet")

        assert_that(len(results)).is_equal_to(1)

    async def test_request_failure_card(self):
        s = Scryfall()
        with pytest.raises(ServiceError) as cm:
            await s.card_async(
                "2135ac5a-187b-4dc9-8f82-34e8d1603416", type=CardIdentifierPath.SCRYFALL
            )

        assert_that(
            "https://api.scryfall.com/cards/None/2135ac5a-187b-4dc9-8f82-34e8d1603416"
        ).is_equal_to(
            cm.value.url,
        )
        assert_that(cm.value.method).is_equal_to("GET")
        assert_that(cm.value.data).is_instance_of(Error)
        assert_that(cm.value.data.status).is_equal_to(404)
        assert_that(cm.value.data.details).is_equal_to(
            "No card found with the given ID or set code and collector number.",
        )

    async def test_request_card_by_arena_id(self):
        s = Scryfall()
        card = await s.card_async("79707", type=CardIdentifierPath.ARENA)

        assert_that(card.name).is_equal_to("Dismal Backwater")

    async def test_request_card_by_mtgo_id(self):
        s = Scryfall()
        card = await s.card_async("79708", type=CardIdentifierPath.MTGO)

        assert_that(card.name).is_equal_to("Earthshaker Giant")

    async def test_request_named(self):
        s = Scryfall()
        card = await s.named_async("fIREbAlL", exact=True)

        assert_that(card.name).is_equal_to("Fireball")

    async def test_request_named_fuzzy_not_found(self):
        s = Scryfall()

        with pytest.raises(ServiceError) as cm:
            await s.named_async("ZZZZZNOTFOUND", exact=False)

        assert_that(cm.value.message).contains(
            "No cards found matching “ZZZZZNOTFOUND”"
        )

    async def test_request_named_fuzzy_ambiguous(self):
        s = Scryfall()

        with pytest.raises(ServiceError) as cm:
            await s.named_async("jace", exact=False)

        assert_that(cm.value.message).is_equal_to(
            (
                "Too many cards match ambiguous name “jace”. Add more words to refine"
                " your search."
            ),
        )

    async def test_request_symbols(self):
        s = Scryfall()

        symbols = [item async for item in s.symbols_async(3)]

        assert_that(len(symbols)).is_equal_to(3)
        assert_that(symbols[0].symbol).is_equal_to("{T}")
        assert_that(symbols[0].english).is_equal_to("tap this permanent")
        assert_that(symbols[0].svg_uri).is_equal_to(
            Url("https://svgs.scryfall.io/card-symbols/T.svg")
        )

    async def test_request_parse_mana(self):
        s = Scryfall()

        parsed = await s.parse_mana_async("{3}{R}{R/P}")

        assert_that(parsed.cmc).is_equal_to(Decimal(5.0))
        assert_that(parsed.colors).is_equal_to(["R"])
        assert_that(parsed.multicolored).is_equal_to(False)

    async def test_request_collection(self):
        s = Scryfall()

        cards = [
            item
            async for item in s.collection_async(
                [
                    {"id": "2135ac5a-187b-4dc9-8f82-34e8d1603416"},
                    {"oracle_id": "7edb3d15-4f70-4ebe-8c5e-caf6a225076d"},
                    {"multiverse_id": 2132},
                    {"id": "dce4027d-b6f0-42ab-b2f4-4fbbcedb4851"},  # unknown
                ]
            )
        ]

        assert_that(len(cards)).is_equal_to(3)
        assert_that([str(card.id) for card in cards]).contains(
            "2135ac5a-187b-4dc9-8f82-34e8d1603416",
        )
        assert_that([str(card.oracle_id) for card in cards]).contains(
            "7edb3d15-4f70-4ebe-8c5e-caf6a225076d",
        )
        assert_that([str(card.id) for card in cards]).does_not_contain(
            "dce4027d-b6f0-42ab-b2f4-4fbbcedb4851",
        )
        assert_that([id for card in cards for id in card.multiverse_ids]).contains(2132)

    async def test_sets(self):
        s = Scryfall()
        sets = [item async for item in s.sets_async(3)]

        assert_that(len(sets)).is_equal_to(3)

    async def test_bulk_cards(self):
        s = Scryfall()
        cards = [
            item
            async for item in asyncstdlib.islice(
                s.get_bulk_data_async("oracle_cards"), 120
            )
        ]

        assert_that(len(cards)).is_equal_to(120)

    async def test_bulk_tags(self):
        s = Scryfall()
        tags = [
            item
            async for item in asyncstdlib.islice(
                s.get_bulk_tags_async(BulkTagType.ORACLE), 13
            )
        ]

        assert_that(len(tags)).is_equal_to(13)

    async def test_catalog(self):
        s = Scryfall()
        keywords = await s.catalog_async(CatalogType.KEYWORD_ABILITIES)

        assert_that(keywords.data).contains("Retrace")
        assert_that(keywords.data).contains("Improvise")
        assert_that(keywords.uri).is_equal_to(
            Url("https://api.scryfall.com/catalog/keyword-abilities")
        )
        assert_that(keywords.total_values).is_greater_than(150)

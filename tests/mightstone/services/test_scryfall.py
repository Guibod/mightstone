import unittest
from decimal import Decimal

import pytest

from mightstone.ass import stream_as_list
from mightstone.services import ServiceError
from mightstone.services.scryfall import (
    BulkTagType,
    CardIdentifierPath,
    CatalogType,
    Error,
    Scryfall,
    SortStrategy,
    UniqueStrategy,
)


@pytest.mark.asyncio
@pytest.mark.skip_remote_api
class ScryfallTest(unittest.IsolatedAsyncioTestCase):
    async def test_request_set_ikoria(self):
        s = Scryfall()
        model = await s.set("IKO")

        self.assertEqual(model.name, "Ikoria: Lair of Behemoths")
        self.assertEqual(model.block_code, None)
        self.assertEqual(
            model.uri,
            "https://api.scryfall.com/sets/19feda43-15ab-427e-a0e4-148a4bf2b03a",
        )

    async def test_request_search_boseiju(self):
        s = Scryfall()
        results = stream_as_list(s.search("boseiju", order=SortStrategy.EUR))

        self.assertEqual(results[0].name, "Boseiju, Who Endures")
        self.assertEqual(results[0].set_name, "Kamigawa: Neon Dynasty Promos")
        self.assertEqual(results[0].set_code, "pneo")

        self.assertEqual(len(results), 5)

    async def test_request_search_boseiju_unique_art(self):
        s = Scryfall()
        results = stream_as_list(
            s.search("boseiju", order=SortStrategy.EUR, unique=UniqueStrategy.ART)
        )

        self.assertEqual(results[0].name, "Boseiju, Who Endures")

        self.assertEqual(len(results), 7)

    async def test_request_failure_card(self):
        s = Scryfall()
        with self.assertRaises(ServiceError) as cm:
            await s.card(
                "2135ac5a-187b-4dc9-8f82-34e8d1603416", type=CardIdentifierPath.SCRYFALL
            )

        self.assertEqual(
            cm.exception.url,
            "https://api.scryfall.com/cards/None/2135ac5a-187b-4dc9-8f82-34e8d1603416",
        )
        self.assertEqual(cm.exception.method, "GET")
        self.assertIsInstance(cm.exception.data, Error)
        self.assertEqual(cm.exception.data.status, 404)
        self.assertEqual(
            cm.exception.data.details,
            "No card found with the given ID or set code and collector number.",
        )

    async def test_request_card_by_arena_id(self):
        s = Scryfall()
        card = await s.card("79707", type=CardIdentifierPath.ARENA)

        self.assertEqual(card.name, "Dismal Backwater")

    async def test_request_card_by_mtgo_id(self):
        s = Scryfall()
        card = await s.card("79708", type=CardIdentifierPath.MTGO)

        self.assertEqual(card.name, "Earthshaker Giant")

    async def test_request_named(self):
        s = Scryfall()
        card = await s.named("fIREbAlL", exact=True)

        self.assertEqual(card.name, "Fireball")

    async def test_request_named_fuzzy_not_found(self):
        s = Scryfall()

        with self.assertRaises(ServiceError) as cm:
            await s.named("ZZZZZNOTFOUND", exact=False)

        self.assertEqual(
            cm.exception.message, "No cards found matching “ZZZZZNOTFOUND”"
        )

    async def test_request_named_fuzzy_ambiguous(self):
        s = Scryfall()

        with self.assertRaises(ServiceError) as cm:
            await s.named("jace", exact=False)

        self.assertEqual(
            cm.exception.message,
            (
                "Too many cards match ambiguous name “jace”. Add more words to refine"
                " your search."
            ),
        )

    async def test_request_symbols(self):
        s = Scryfall()

        symbols = stream_as_list(s.symbols(3))

        self.assertEqual(len(symbols), 3)
        self.assertEqual(symbols[0].symbol, "{T}")
        self.assertEqual(symbols[0].english, "tap this permanent")
        self.assertEqual(
            symbols[0].svg_uri, "https://svgs.scryfall.io/card-symbols/T.svg"
        )

    async def test_request_parse_mana(self):
        s = Scryfall()

        parsed = await s.parse_mana("{3}{R}{R/P}")

        self.assertEqual(parsed.cmc, Decimal(5.0))
        self.assertEqual(parsed.colors, ["R"])
        self.assertEqual(parsed.multicolored, True)

    async def test_request_collection(self):
        s = Scryfall()

        cards = stream_as_list(
            s.collection(
                [
                    {"id": "2135ac5a-187b-4dc9-8f82-34e8d1603416"},
                    {"oracle_id": "7edb3d15-4f70-4ebe-8c5e-caf6a225076d"},
                    {"multiverse_id": 2132},
                    {"id": "dce4027d-b6f0-42ab-b2f4-4fbbcedb4851"},  # unknown
                ]
            )
        )

        self.assertEqual(len(cards), 3)
        self.assertIn(
            "2135ac5a-187b-4dc9-8f82-34e8d1603416", [str(card.id) for card in cards]
        )
        self.assertIn(
            "7edb3d15-4f70-4ebe-8c5e-caf6a225076d",
            [str(card.oracle_id) for card in cards],
        )
        self.assertNotIn(
            "dce4027d-b6f0-42ab-b2f4-4fbbcedb4851", [str(card.id) for card in cards]
        )
        self.assertIn(2132, [id for card in cards for id in card.multiverse_ids])

    async def test_sets(self):
        s = Scryfall()
        sets = stream_as_list(s.sets(3))

        self.assertEqual(len(sets), 3)

    async def test_bulk_cards(self):
        s = Scryfall()
        cards = stream_as_list(s.get_bulk_data("oracle_cards"), limit=120)

        self.assertEqual(len(cards), 120)

    async def test_bulk_tags(self):
        s = Scryfall()
        cards = stream_as_list(s.get_bulk_tags(BulkTagType.ORACLE), limit=13)

        self.assertEqual(len(cards), 13)

    async def test_catalog(self):
        s = Scryfall()
        keywords = await s.catalog(CatalogType.KEYWORD_ABILITIES)

        self.assertIn("Retrace", keywords.data)
        self.assertIn("Improvise", keywords.data)
        self.assertEqual(
            "https://api.scryfall.com/catalog/keyword-abilities", keywords.uri
        )
        self.assertGreater(keywords.total_values, 150)

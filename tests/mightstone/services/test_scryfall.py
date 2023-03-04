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

from . import skip_remote_api  # noqa: F401
from mightstone.services.scryfall.query import Query, Term, Keyword, tokenize


class ScryfallTerm(unittest.TestCase):
    def test_f(self):
        t = Term("t", "zombie")

        self.assertEqual(t.explain(), "the card types include “zombie”")

class ParserTest(unittest.TestCase):
    tests = {
        "help": {1, 2, 4, 5},
        "help or hulp": {1, 2, 3, 4, 5},
        "help and hulp": {2},
        "help hulp": {2},
        "help and hulp or hilp": {2, 3, 4},
        "help or hulp and hilp": {1, 2, 3, 4, 5},
        "help or hulp or hilp or halp": {1, 2, 3, 4, 5, 6},
        "(help or hulp) and (hilp or halp)": {3, 4, 5},
        "help and (hilp or halp)": {4, 5},
        "(help and (hilp or halp)) or hulp": {2, 3, 4, 5},
        "not help": {3, 6, 7, 8},
        "not hulp and halp": {5, 6},
        "not (help and halp)": {1, 2, 3, 4, 6, 7, 8},
        '"help me please"': {2},
        '"help me please" or hulp': {2, 3},
        '"help me please" or (hulp and halp)': {2},
        "help*": {1, 2, 4, 5, 8},
        "help or hulp*": {1, 2, 3, 4, 5},
        "help* and hulp": {2},
        "help and hulp* or hilp": {2, 3, 4},
        "help* or hulp or hilp or halp": {1, 2, 3, 4, 5, 6, 8},
        "(help or hulp*) and (hilp* or halp)": {3, 4, 5},
        "help* and (hilp* or halp*)": {4, 5},
        "(help and (hilp* or halp)) or hulp*": {2, 3, 4, 5},
        "not help* and halp": {6},
        "not (help* and helpe*)": {1, 2, 3, 4, 5, 6, 7},
        '"help* me please"': {2},
        '"help* me* please" or hulp*': {2, 3},
        '"help me please*" or (hulp and halp)': {2},
        '"help me please" not (hulp and halp)': {2},
        '"help me please" hulp': {2},
        "help and hilp and not holp": {4},
        "help hilp not holp": {4},
        "help hilp and not holp": {4},
    }

    docs = {
        1: "help",
        2: "help me please hulp",
        3: "hulp hilp",
        4: "help hilp",
        5: "halp thinks he needs help",
        6: "he needs halp",
        7: "nothing",
        8: "helper",
    }

    index = {
        "help": {1, 2, 4, 5},
        "me": {2},
        "please": {2},
        "hulp": {2, 3},
        "hilp": {3, 4},
        "halp": {5, 6},
        "thinks": {5},
        "he": {5, 6},
        "needs": {5, 6},
        "nothing": {7},
        "helper": {8},
    }

    def GetWord(self, word):
        if word in self.index:
            return self.index[word]
        else:
            return set()

    def GetWordWildcard(self, word):
        result = set()
        for item in list(self.index.keys()):
            if word == item[0 : len(word)]:
                result = result.union(self.index[item])
        return result

    def GetQuotes(self, search_string, tmp_result):
        result = set()
        for item in tmp_result:
            if self.docs[item].count(search_string):
                result.add(item)
        return result

    def GetNot(self, not_set):
        all = set(list(self.docs.keys()))
        return all.difference(not_set)

    def Test(self):
        all_ok = True
        for item in list(self.tests.keys()):
            print(item)
            r = self.Parse(item)
            e = self.tests[item]
            print("Result: %s" % r)
            print("Expect: %s" % e)
            if e == r:
                print("Test OK")
            else:
                all_ok = False
                print(">>>>>>>>>>>>>>>>>>>>>>Test ERROR<<<<<<<<<<<<<<<<<<<<<")
            print("")
        return

class ScryfallTokenizer(unittest.TestCase):
    def test_tokenize(self):
        self.assertEqual(
                         ["dead", "r:rare", "t:zombie", "-ammit"],
            tokenize("dead r:rare t:zombie -ammit"))

    def test_tokenize_with_quote(self):
        self.assertEqual(
                         ["dead", "r:rare", "t:zombie", "-ammit"],
            tokenize("dead r:\"rare\" t:zombie -'ammit'"))

    def test_tokenize_with_quote_and_space(self):
        self.assertEqual(
                         ["dead", "r:rare", "t:zombie", "-ammit eternal"],
            tokenize("dead r:\"rare\" t:zombie -'ammit eternal'"))

    def test_tokenize_with_or_and_parenthesis_and_no_space(self):
        self.assertEqual(
                         ["dead", "(", "r:rare", "or", "t:zombie", ")", "-ammit eternal"],
            tokenize("dead (r:\"rare\" or t:zombie) -'ammit eternal'"))

    def test_tokenize_with_or_and_parenthesis_and_no_space(self):
        self.assertEqual([")", ")", "r:rare", "or", "t:zombie", ")", "-ammit eternal"],
                         tokenize("))\")\""))

    def test_tokenize_with_or_and_parenthesis_with_space(self):
        self.assertEqual(["dead", "(", "r:rare", "or", "t:zombie", ")", "-ammit eternal"],
                         tokenize("dead ( r:\"rare\" or t:zombie ) -'ammit eternal'"))

    def test_tokenize_with_parenthesis_in_quote(self):
        self.assertEqual(["!Hazmat suit (used)", "t:enchant"], tokenize("!\"Hazmat suit (used)\" t:enchant"))

    def test_tokenize_strictly_equal(self):
        self.assertEqual(["!fire"], tokenize("!fire"))

    def test_tokenize_strictly_equal_and_quote(self):
        self.assertEqual(["!soul ransom"], tokenize("!\"soul ransom\""))


class ScryfallQueryTokenize(unittest.TestCase):
    def test_simplify_already_simple(self):
        query = Query("id:c t:land")

    def test_simplify_long(self):
        query = Query("identifier:c type:land")

    def test_simplify_parenthesis(self):
        query = Query("(id:c t:land)")

    def test_simplify_nested_parenthesis(self):
        query = Query("((id:c) t:land)")

    def test_explain(self):
        query = Query("id:c t:land")
        self.assertEqual(query.explain(), "the cards have colorless identity and the card types include “land”")




@pytest.mark.asyncio
@pytest.mark.skip_remote_api
class ScryfallIntegrationTest(unittest.IsolatedAsyncioTestCase):
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
        self.assertEqual(parsed.multicolored, False)

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

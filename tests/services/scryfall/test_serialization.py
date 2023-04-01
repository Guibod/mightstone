import os.path
import uuid

from mightstone.services.scryfall import Card, Catalog, Ruling, Set, Symbol, Tag

from ...testcase import TestBeanie  # type: ignore


class TestSerialization(TestBeanie):
    async def test_card(self):
        self.assertEqual(Card.Settings.name, "scryfall_cards")

        card = Card.parse_file(os.path.dirname(__file__) + "/samples/card.json")
        await card.save()

        cards = await Card.find_many().to_list()
        self.assertEqual(len(cards), 1)
        self.assertEqual(cards[0].object, "card")
        self.assertEqual(cards[0].id, uuid.UUID("743f3cf5-f8aa-49d4-947d-76b91799547a"))

        card2 = Card.parse_file(os.path.dirname(__file__) + "/samples/card.json")
        card2.name = "altered name"
        await card2.save()

        cards = await Card.find_many().to_list()
        self.assertEqual(len(cards), 1)
        self.assertEqual(cards[0].id, uuid.UUID("743f3cf5-f8aa-49d4-947d-76b91799547a"))
        self.assertEqual(cards[0].name, "altered name")

    async def test_set(self):
        self.assertEqual(Set.Settings.name, "scryfall_sets")

        set = Set.parse_file(os.path.dirname(__file__) + "/samples/set.json")
        await set.save()

        sets = await Set.find_many().to_list()
        self.assertEqual(len(sets), 1)
        self.assertEqual(sets[0].object, "set")
        self.assertEqual(sets[0].id, uuid.UUID("cd05036f-2698-43e6-a48e-5c8d82f0a551"))

        set2 = Set.parse_file(os.path.dirname(__file__) + "/samples/set.json")
        set2.name = "altered name"
        await set2.save()

        sets = await Set.find_many().to_list()
        self.assertEqual(len(sets), 1)
        self.assertEqual(sets[0].id, uuid.UUID("cd05036f-2698-43e6-a48e-5c8d82f0a551"))
        self.assertEqual(sets[0].name, "altered name")

    async def test_symbol(self):
        self.assertEqual(Symbol.Settings.name, "scryfall_symbols")

        symbol = Symbol.parse_file(os.path.dirname(__file__) + "/samples/symbol.json")
        await symbol.save()

        symbols = await Symbol.find_many().to_list()
        self.assertEqual(len(symbols), 1)
        self.assertEqual(symbols[0].object, "card_symbol")
        self.assertEqual(symbols[0].symbol, "{T}")
        self.assertIsInstance(symbol.id, str)
        self.assertEqual(symbol.id, "{T}")

        symbol2 = Symbol.parse_file(os.path.dirname(__file__) + "/samples/symbol.json")
        symbol2.english = "altered name"
        await symbol2.save()

        symbols = await Symbol.find_many().to_list()
        self.assertEqual(len(symbols), 1)
        self.assertEqual(symbols[0].id, "{T}")
        self.assertEqual(symbols[0].english, "altered name")

    async def test_tag(self):
        self.assertEqual(Tag.Settings.name, "scryfall_tags")

        tag = Tag.parse_file(os.path.dirname(__file__) + "/samples/tag.json")
        await tag.save()

        tags = await Tag.find_many().to_list()
        self.assertEqual(len(tags), 1)
        self.assertEqual(tags[0].object, "tag")
        self.assertEqual(tags[0].id, uuid.UUID("1793f1ca-5551-4a85-89b5-fb39774dd22d"))

        tag2 = Tag.parse_file(os.path.dirname(__file__) + "/samples/tag.json")
        tag2.label = "altered name"
        await tag2.save()

        tags = await Tag.find_many().to_list()
        self.assertEqual(len(tags), 1)
        self.assertEqual(tags[0].id, uuid.UUID("1793f1ca-5551-4a85-89b5-fb39774dd22d"))
        self.assertEqual(tags[0].label, "altered name")

    async def test_ruling(self):
        self.assertEqual(Ruling.Settings.name, "scryfall_rulings")

        ruling = Ruling.parse_file(os.path.dirname(__file__) + "/samples/ruling.json")
        await ruling.save()

        rulings = await Ruling.find_many().to_list()
        self.assertEqual(len(rulings), 1)
        self.assertEqual(rulings[0].object, "ruling")
        self.assertEqual(
            rulings[0].oracle_id, uuid.UUID("afa49a09-146f-4439-850e-dd1938c93cef")
        )

        ruling2 = Ruling.parse_file(os.path.dirname(__file__) + "/samples/ruling.json")
        ruling2.comment = "altered name"
        await ruling2.save()

        # No enforcement of uniqueness
        rulings = await Ruling.find_many().to_list()
        self.assertEqual(len(rulings), 2)
        self.assertEqual(
            rulings[0].oracle_id, uuid.UUID("afa49a09-146f-4439-850e-dd1938c93cef")
        )
        self.assertEqual(
            rulings[1].oracle_id, uuid.UUID("afa49a09-146f-4439-850e-dd1938c93cef")
        )
        self.assertEqual(
            rulings[0].comment,
            (
                "Derevi, Empyrial Tactician is banned as a commander in Duel Commander "
                "format, but it may be part of your deck."
            ),
        )
        self.assertEqual(rulings[1].comment, "altered name")

    async def test_catalog(self):
        self.assertEqual(Catalog.Settings.name, "scryfall_catalogs")

        catalog = Catalog.parse_file(
            os.path.dirname(__file__) + "/samples/catalog.json"
        )
        await catalog.save()

        catalogs = await Catalog.find_many().to_list()
        self.assertEqual(len(catalogs), 1)
        self.assertEqual(catalogs[0].object, "catalog")
        self.assertEqual(catalogs[0].uri, "https://api.scryfall.com/catalog/land-types")

        catalog2 = Catalog.parse_file(
            os.path.dirname(__file__) + "/samples/catalog.json"
        )
        catalog2.data.append("altered name")
        await catalog2.save()

        catalogs = await Catalog.find_many().to_list()
        self.assertEqual(len(catalogs), 1)
        self.assertEqual(catalogs[0].uri, "https://api.scryfall.com/catalog/land-types")
        self.assertIn(
            "altered name",
            catalogs[0].data,
        )

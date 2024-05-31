import pathlib
import uuid

from pydantic_core._pydantic_core import Url

from mightstone.services.scryfall import Card, Catalog, Ruling, Set, Symbol, Tag

from ...testcase import TestBeanie  # type: ignore


class TestSerialization(TestBeanie):
    async def test_card(self):
        self.assertEqual(Card.Settings.name, "scryfall_cards")

        f = pathlib.Path(__file__).parent.joinpath("samples/card.json")
        card = Card.model_validate_json(f.read_bytes())

        await card.save()

        cards = await Card.find_many().to_list()
        self.assertEqual(len(cards), 1)
        self.assertEqual(cards[0].object, "card")
        self.assertEqual(cards[0].id, uuid.UUID("743f3cf5-f8aa-49d4-947d-76b91799547a"))

        f = pathlib.Path(__file__).parent.joinpath("samples/card.json")
        card2 = Card.model_validate_json(f.read_bytes())
        card2.name = "altered name"
        await card2.save()

        cards = await Card.find_many().to_list()
        self.assertEqual(len(cards), 1)
        self.assertEqual(cards[0].id, uuid.UUID("743f3cf5-f8aa-49d4-947d-76b91799547a"))
        self.assertEqual(cards[0].name, "altered name")

    async def test_set(self):
        self.assertEqual(Set.Settings.name, "scryfall_sets")

        f = pathlib.Path(__file__).parent.joinpath("samples/set.json")
        set = Set.model_validate_json(f.read_bytes())
        await set.save()

        sets = await Set.find_many().to_list()
        self.assertEqual(len(sets), 1)
        self.assertEqual(sets[0].object, "set")
        self.assertEqual(sets[0].id, uuid.UUID("cd05036f-2698-43e6-a48e-5c8d82f0a551"))

        f = pathlib.Path(__file__).parent.joinpath("samples/set.json")
        set2 = Set.model_validate_json(f.read_bytes())
        set2.name = "altered name"
        await set2.save()

        sets = await Set.find_many().to_list()
        self.assertEqual(len(sets), 1)
        self.assertEqual(sets[0].id, uuid.UUID("cd05036f-2698-43e6-a48e-5c8d82f0a551"))
        self.assertEqual(sets[0].name, "altered name")

    async def test_symbol(self):
        self.assertEqual(Symbol.Settings.name, "scryfall_symbols")

        f = pathlib.Path(__file__).parent.joinpath("samples/symbol.json")
        symbol = Symbol.model_validate_json(f.read_bytes())
        await symbol.save()

        symbols = await Symbol.find_many().to_list()
        self.assertEqual(len(symbols), 1)
        self.assertEqual(symbols[0].object, "card_symbol")
        self.assertEqual(symbols[0].symbol, "{T}")
        self.assertIsInstance(symbol.id, str)
        self.assertEqual(symbol.id, "{T}")

        f = pathlib.Path(__file__).parent.joinpath("samples/symbol.json")
        symbol2 = Symbol.model_validate_json(f.read_bytes())
        symbol2.english = "altered name"
        await symbol2.save()

        symbols = await Symbol.find_many().to_list()
        self.assertEqual(len(symbols), 1)
        self.assertEqual(symbols[0].id, "{T}")
        self.assertEqual(symbols[0].english, "altered name")

    async def test_tag(self):
        self.assertEqual(Tag.Settings.name, "scryfall_tags")

        f = pathlib.Path(__file__).parent.joinpath("samples/tag.json")
        tag = Tag.model_validate_json(f.read_bytes())
        await tag.save()

        tags = await Tag.find_many().to_list()
        self.assertEqual(len(tags), 1)
        self.assertEqual(tags[0].object, "tag")
        self.assertEqual(tags[0].id, uuid.UUID("1793f1ca-5551-4a85-89b5-fb39774dd22d"))

        f = pathlib.Path(__file__).parent.joinpath("samples/tag.json")
        tag2 = Tag.model_validate_json(f.read_bytes())
        tag2.label = "altered name"
        await tag2.save()

        tags = await Tag.find_many().to_list()
        self.assertEqual(len(tags), 1)
        self.assertEqual(tags[0].id, uuid.UUID("1793f1ca-5551-4a85-89b5-fb39774dd22d"))
        self.assertEqual(tags[0].label, "altered name")

    async def test_ruling(self):
        self.assertEqual(Ruling.Settings.name, "scryfall_rulings")

        f = pathlib.Path(__file__).parent.joinpath("samples/ruling.json")
        ruling = Ruling.model_validate_json(f.read_bytes())
        await ruling.save()

        rulings = await Ruling.find_many().to_list()
        self.assertEqual(len(rulings), 1)
        self.assertEqual(rulings[0].object, "ruling")
        self.assertEqual(
            rulings[0].oracle_id, uuid.UUID("afa49a09-146f-4439-850e-dd1938c93cef")
        )

        f = pathlib.Path(__file__).parent.joinpath("samples/ruling.json")
        ruling2 = Ruling.model_validate_json(f.read_bytes())
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

        f = pathlib.Path(__file__).parent.joinpath("samples/catalog.json")
        catalog = Catalog.model_validate_json(f.read_bytes())
        await catalog.save()

        catalogs = await Catalog.find_many().to_list()
        self.assertEqual(len(catalogs), 1)
        self.assertEqual(catalogs[0].object, "catalog")
        self.assertEqual(
            catalogs[0].uri, Url("https://api.scryfall.com/catalog/land-types")
        )

        f = pathlib.Path(__file__).parent.joinpath("samples/catalog.json")
        catalog2 = Catalog.model_validate_json(f.read_bytes())
        catalog2.data.append("altered name")
        await catalog2.save()

        catalogs = await Catalog.find_many().to_list()
        self.assertEqual(len(catalogs), 1)
        self.assertEqual(
            catalogs[0].uri, Url("https://api.scryfall.com/catalog/land-types")
        )
        self.assertIn(
            "altered name",
            catalogs[0].data,
        )

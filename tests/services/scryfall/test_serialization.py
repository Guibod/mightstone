import pathlib
import uuid

import pytest
from assertpy import assert_that
from pydantic_core._pydantic_core import Url

from mightstone.services.scryfall import (
    SerializableCard,
    SerializableCatalog,
    SerializableRuling,
    SerializableSet,
    SerializableSymbol,
    SerializableTag,
)


@pytest.mark.asyncio
@pytest.mark.usefixtures("init_beanie_fixture")
class TestSerialization:
    async def test_card(self):
        assert_that(SerializableCard.Settings.name).is_equal_to(
            "mightstone_scryfall_cards"
        )

        f = pathlib.Path(__file__).parent.joinpath("samples/card.json")
        card = SerializableCard.model_validate_json(f.read_bytes())

        await card.save()

        cards = await SerializableCard.find_many().to_list()
        assert_that(len(cards)).is_equal_to(1)
        assert_that(cards[0].object).is_equal_to("card")
        assert_that(cards[0].id).is_equal_to(
            uuid.UUID("743f3cf5-f8aa-49d4-947d-76b91799547a")
        )

        f = pathlib.Path(__file__).parent.joinpath("samples/card.json")
        card2 = SerializableCard.model_validate_json(f.read_bytes())
        card2.name = "altered name"
        await card2.save()

        cards = await SerializableCard.find_many().to_list()
        assert_that(len(cards)).is_equal_to(1)
        assert_that(cards[0].id).is_equal_to(
            uuid.UUID("743f3cf5-f8aa-49d4-947d-76b91799547a")
        )
        assert_that(cards[0].name).is_equal_to("altered name")

    async def test_set(self):
        assert_that(SerializableSet.Settings.name).is_equal_to(
            "mightstone_scryfall_sets"
        )

        f = pathlib.Path(__file__).parent.joinpath("samples/set.json")
        set = SerializableSet.model_validate_json(f.read_bytes())
        await set.save()

        sets = await SerializableSet.find_many().to_list()
        assert_that(len(sets)).is_equal_to(1)
        assert_that(sets[0].object).is_equal_to("set")
        assert_that(sets[0].id).is_equal_to(
            uuid.UUID("cd05036f-2698-43e6-a48e-5c8d82f0a551")
        )

        f = pathlib.Path(__file__).parent.joinpath("samples/set.json")
        set2 = SerializableSet.model_validate_json(f.read_bytes())
        set2.name = "altered name"
        await set2.save()

        sets = await SerializableSet.find_many().to_list()
        assert_that(len(sets)).is_equal_to(1)
        assert_that(sets[0].id).is_equal_to(
            uuid.UUID("cd05036f-2698-43e6-a48e-5c8d82f0a551")
        )
        assert_that(sets[0].name).is_equal_to("altered name")

    async def test_symbol(self):
        assert_that(SerializableSymbol.Settings.name).is_equal_to(
            "mightstone_scryfall_symbols"
        )

        f = pathlib.Path(__file__).parent.joinpath("samples/symbol.json")
        symbol = SerializableSymbol.model_validate_json(f.read_bytes())
        await symbol.save()

        symbols = await SerializableSymbol.find_many().to_list()
        assert_that(len(symbols)).is_equal_to(1)
        assert_that(symbols[0].object).is_equal_to("card_symbol")
        assert_that(symbols[0].symbol).is_equal_to("{T}")
        assert_that(symbol.id).is_instance_of(uuid.UUID)

        assert_that(symbols[0].id).is_equal_to(
            uuid.UUID("0cdb840e-941f-5360-87b4-89201ef2f8e6")
        )

        f = pathlib.Path(__file__).parent.joinpath("samples/symbol.json")
        symbol2 = SerializableSymbol.model_validate_json(f.read_bytes())
        symbol2.english = "altered name"
        await symbol2.save()

        symbols = await SerializableSymbol.find_many().to_list()
        assert_that(len(symbols)).is_equal_to(1)
        assert_that(symbols[0].id).is_equal_to(
            uuid.UUID("0cdb840e-941f-5360-87b4-89201ef2f8e6")
        )
        assert_that(symbols[0].english).is_equal_to("altered name")

    async def test_tag(self):
        assert_that(SerializableTag.Settings.name).is_equal_to(
            "mightstone_scryfall_tags"
        )

        f = pathlib.Path(__file__).parent.joinpath("samples/tag.json")
        tag = SerializableTag.model_validate_json(f.read_bytes())
        await tag.save()

        tags = await SerializableTag.find_many().to_list()
        assert_that(len(tags)).is_equal_to(1)
        assert_that(tags[0].object).is_equal_to("tag")
        assert_that(tags[0].id).is_equal_to(
            uuid.UUID("1793f1ca-5551-4a85-89b5-fb39774dd22d")
        )

        f = pathlib.Path(__file__).parent.joinpath("samples/tag.json")
        tag2 = SerializableTag.model_validate_json(f.read_bytes())
        tag2.label = "altered name"
        await tag2.save()

        tags = await SerializableTag.find_many().to_list()
        assert_that(len(tags)).is_equal_to(1)
        assert_that(tags[0].id).is_equal_to(
            uuid.UUID("1793f1ca-5551-4a85-89b5-fb39774dd22d")
        )
        assert_that(tags[0].label).is_equal_to("altered name")

    async def test_ruling(self):
        assert_that(SerializableRuling.Settings.name).is_equal_to(
            "mightstone_scryfall_rulings"
        )

        f = pathlib.Path(__file__).parent.joinpath("samples/ruling.json")
        ruling = SerializableRuling.model_validate_json(f.read_bytes())
        await ruling.save()

        rulings = await SerializableRuling.find_many().to_list()
        assert_that(len(rulings)).is_equal_to(1)
        assert_that(rulings[0].object).is_equal_to("ruling")
        assert_that(rulings[0].oracle_id).is_equal_to(
            uuid.UUID("afa49a09-146f-4439-850e-dd1938c93cef")
        )

        f = pathlib.Path(__file__).parent.joinpath("samples/ruling.json")
        ruling2 = SerializableRuling.model_validate_json(f.read_bytes())
        ruling2.comment = "altered name"
        await ruling2.save()

        # No enforcement of uniqueness
        rulings = await SerializableRuling.find_many().to_list()
        assert_that(len(rulings)).is_equal_to(2)
        assert_that(rulings[0].oracle_id).is_equal_to(
            uuid.UUID("afa49a09-146f-4439-850e-dd1938c93cef")
        )
        assert_that(rulings[1].oracle_id).is_equal_to(
            uuid.UUID("afa49a09-146f-4439-850e-dd1938c93cef")
        )
        assert_that(rulings[0].comment).is_equal_to(
            (
                "Derevi, Empyrial Tactician is banned as a commander in Duel Commander "
                "format, but it may be part of your deck."
            ),
        )
        assert_that(rulings[1].comment).is_equal_to("altered name")

    async def test_catalog(self):
        assert_that(SerializableCatalog.Settings.name).is_equal_to(
            "mightstone_scryfall_catalogs",
        )

        f = pathlib.Path(__file__).parent.joinpath("samples/catalog.json")
        catalog = SerializableCatalog.model_validate_json(f.read_bytes())
        await catalog.save()

        catalogs = await SerializableCatalog.find_many().to_list()
        assert_that(len(catalogs)).is_equal_to(1)
        assert_that(catalogs[0].object).is_equal_to("catalog")
        assert_that(catalogs[0].uri).is_equal_to(
            Url("https://api.scryfall.com/catalog/land-types")
        )

        f = pathlib.Path(__file__).parent.joinpath("samples/catalog.json")
        catalog2 = SerializableCatalog.model_validate_json(f.read_bytes())
        catalog2.data.append("altered name")
        await catalog2.save()

        catalogs = await SerializableCatalog.find_many().to_list()
        assert_that(len(catalogs)).is_equal_to(1)
        assert_that(catalogs[0].uri).is_equal_to(
            Url("https://api.scryfall.com/catalog/land-types")
        )
        assert_that(catalogs[0].data).contains("altered name")

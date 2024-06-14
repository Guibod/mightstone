import pathlib
import uuid

import pytest
from assertpy import assert_that

from mightstone.services.mtgjson.models import (
    SerializableCardAtomic,
    SerializableCardPrices,
    SerializableCardSet,
    SerializableDeck,
    SerializableSet,
    SerializableSetList,
    SerializableTcgPlayerSKUs,
)


@pytest.mark.asyncio(scope="session")
@pytest.mark.usefixtures("init_beanie_fixture")
class TestSerialization:
    async def test_cardset(self):
        assert_that(SerializableCardSet.get_settings().name).is_equal_to(
            "mightstone_mtgjson_cardsets"
        )

        f = pathlib.Path(__file__).parent.joinpath("samples/cardset.json")
        card = SerializableCardSet.model_validate_json(f.read_bytes())
        await card.save()

        cards = await SerializableCardSet.find_many().to_list()
        assert_that(len(cards)).is_equal_to(1)
        assert_that(cards[0].artist).is_equal_to("Lius Lasahido")
        assert_that(cards[0].id).is_equal_to(
            uuid.UUID("00010d56-fe38-5e35-8aed-518019aa36a5")
        )

        f = pathlib.Path(__file__).parent.joinpath("samples/cardset.json")
        card2 = SerializableCardSet.model_validate_json(f.read_bytes())
        card2.artist = "altered name"
        await card2.save()

        cards = await SerializableCardSet.find_many().to_list()
        assert_that(len(cards)).is_equal_to(1)
        assert_that(cards[0].id).is_equal_to(
            uuid.UUID("00010d56-fe38-5e35-8aed-518019aa36a5")
        )
        assert_that(cards[0].artist).is_equal_to("altered name")

    async def test_cardprice(self):
        assert_that(SerializableCardPrices.get_settings().name).is_equal_to(
            "mightstone_mtgjson_cardprices"
        )

        f = pathlib.Path(__file__).parent.joinpath("samples/cardprices.json")
        card = SerializableCardPrices.model_validate_json(f.read_bytes())
        assert_that(
            card.paper["cardkingdom"].buylist["foil"]["2022-12-19"]
        ).is_equal_to(1.5)
        await card.save()

        cards = await SerializableCardPrices.find_many().to_list()
        assert_that(len(cards)).is_equal_to(1)
        assert_that(
            cards[0].paper["cardkingdom"].buylist["foil"]["2022-12-19"]
        ).is_equal_to(1.5)
        assert_that(cards[0].id).is_equal_to(
            uuid.UUID("00010d56-fe38-5e35-8aed-518019aa36a5")
        )

        f = pathlib.Path(__file__).parent.joinpath("samples/cardprices.json")
        card2 = SerializableCardPrices.model_validate_json(f.read_bytes())
        card2.paper["cardkingdom"].buylist["foil"]["2022-12-19"] = 500
        await card2.save()

        cards = await SerializableCardPrices.find_many().to_list()
        assert_that(len(cards)).is_equal_to(1)
        assert_that(cards[0].id).is_equal_to(
            uuid.UUID("00010d56-fe38-5e35-8aed-518019aa36a5")
        )
        assert_that(
            cards[0].paper["cardkingdom"].buylist["foil"]["2022-12-19"]
        ).is_equal_to(500)

    async def test_tcgplayerskus(self):
        assert_that(SerializableTcgPlayerSKUs.get_settings().name).is_equal_to(
            "mightstone_mtgjson_tcgplayerskus",
        )

        f = pathlib.Path(__file__).parent.joinpath("samples/tcgplayerskus.json")
        sku = SerializableTcgPlayerSKUs.model_validate_json(f.read_bytes())
        assert_that(sku.skus[0].condition).is_equal_to("NEAR MINT")
        await sku.save()

        skus = await SerializableTcgPlayerSKUs.find_many().to_list()
        assert_that(len(skus)).is_equal_to(1)
        assert_that(skus[0].skus[0].condition).is_equal_to("NEAR MINT")
        assert_that(skus[0].id).is_equal_to(
            uuid.UUID("00010d56-fe38-5e35-8aed-518019aa36a5")
        )

        f = pathlib.Path(__file__).parent.joinpath("samples/tcgplayerskus.json")
        sku2 = SerializableTcgPlayerSKUs.model_validate_json(f.read_bytes())
        sku2.skus[0].condition = "altered text"
        await sku2.save()

        skus = await SerializableTcgPlayerSKUs.find_many().to_list()
        assert_that(len(skus)).is_equal_to(1)
        assert_that(skus[0].skus[0].condition).is_equal_to("altered text")

    async def test_card_atomic(self):
        assert_that(SerializableCardAtomic.get_settings().name).is_equal_to(
            "mightstone_mtgjson_cardatomics"
        )

        f = pathlib.Path(__file__).parent.joinpath("samples/cardatomic.json")
        card = SerializableCardAtomic.model_validate_json(f.read_bytes())
        assert_that(card.ascii_name).is_equal_to('"Lifetime" Pass Holder')
        assert_that(card.faces[0].name).is_equal_to('"Lifetime" Pass Holder')
        await card.save()

        cards = await SerializableCardAtomic.find_many().to_list()
        assert_that(len(cards)).is_equal_to(1)
        assert_that(cards[0].faces[0].name).is_equal_to('"Lifetime" Pass Holder')
        assert_that(cards[0].id).is_equal_to(
            uuid.UUID("96cee960-9cb4-50c6-8cce-4439b83f92c0")
        )

        f = pathlib.Path(__file__).parent.joinpath("samples/cardatomic.json")
        card2 = SerializableCardAtomic.model_validate_json(f.read_bytes())
        card2.faces[0].name = "altered text"
        await card2.save()

        card = await SerializableCardAtomic.find_many().to_list()
        assert_that(len(card)).is_equal_to(1)
        assert_that(card[0].faces[0].name).is_equal_to("altered text")

    async def test_deck(self):
        assert_that(SerializableDeck.get_settings().name).is_equal_to(
            "mightstone_mtgjson_decks"
        )

        f = pathlib.Path(__file__).parent.joinpath("samples/deck.json")
        deck = SerializableDeck.model_validate_json(f.read_bytes())
        assert_that(deck.name).is_equal_to("Blink 1")
        assert_that(deck.id).is_equal_to(
            uuid.UUID("b4c08a29-f3c5-5fa9-af9d-8fdfa80a004e")
        )
        await deck.save()

        decks = await SerializableDeck.find_many().to_list()
        assert_that(len(decks)).is_equal_to(1)
        assert_that(decks[0].name).is_equal_to("Blink 1")
        assert_that(decks[0].id).is_equal_to(
            uuid.UUID("b4c08a29-f3c5-5fa9-af9d-8fdfa80a004e")
        )

        f = pathlib.Path(__file__).parent.joinpath("samples/deck.json")
        deck2 = SerializableDeck.model_validate_json(f.read_bytes())
        deck2.code = "altered text"
        await deck2.save()

        decks = await SerializableDeck.find_many().to_list()
        assert_that(len(decks)).is_equal_to(1)
        assert_that(decks[0].code).is_equal_to("altered text")
        assert_that(decks[0].id).is_equal_to(
            uuid.UUID("b4c08a29-f3c5-5fa9-af9d-8fdfa80a004e")
        )

    async def test_set_list(self):
        assert_that(SerializableSetList.get_settings().name).is_equal_to(
            "mightstone_mtgjson_setlists"
        )

        f = pathlib.Path(__file__).parent.joinpath("samples/setlist.json")
        set = SerializableSetList.model_validate_json(f.read_bytes())
        assert_that(set.name).is_equal_to("Adventures in the Forgotten Realms")
        assert_that(set.id).is_equal_to(
            uuid.UUID("1832e5f5-212a-5199-9318-71d5dfcdefa7")
        )
        await set.save()

        sets = await SerializableSetList.find_many().to_list()
        assert_that(len(sets)).is_equal_to(1)
        assert_that(sets[0].name).is_equal_to("Adventures in the Forgotten Realms")
        assert_that(sets[0].id).is_equal_to(
            uuid.UUID("1832e5f5-212a-5199-9318-71d5dfcdefa7")
        )

        f = pathlib.Path(__file__).parent.joinpath("samples/setlist.json")
        set2 = SerializableSetList.model_validate_json(f.read_bytes())
        set2.name = "altered text"
        await set2.save()

        sets = await SerializableSetList.find_many().to_list()
        assert_that(len(sets)).is_equal_to(1)
        assert_that(sets[0].name).is_equal_to("altered text")
        assert_that(sets[0].id).is_equal_to(
            uuid.UUID("1832e5f5-212a-5199-9318-71d5dfcdefa7")
        )

    async def test_set(self):
        assert_that(SerializableSet.get_settings().name).is_equal_to(
            "mightstone_mtgjson_sets"
        )

        f = pathlib.Path(__file__).parent.joinpath("samples/set.json")
        set = SerializableSet.model_validate_json(f.read_bytes())
        assert_that(set.name).is_equal_to("The Brothers' War")
        assert_that(set.id).is_equal_to(
            uuid.UUID("9a3222d3-46e9-591b-8101-68d406cb0360")
        )
        await set.save()

        sets = await SerializableSet.find_many().to_list()
        assert_that(len(sets)).is_equal_to(1)
        assert_that(sets[0].name).is_equal_to("The Brothers' War")
        assert_that(sets[0].id).is_equal_to(
            uuid.UUID("9a3222d3-46e9-591b-8101-68d406cb0360")
        )

        f = pathlib.Path(__file__).parent.joinpath("samples/set.json")
        set2 = SerializableSet.model_validate_json(f.read_bytes())
        set2.name = "altered text"
        await set2.save()

        sets = await SerializableSet.find_many().to_list()
        assert_that(len(sets)).is_equal_to(1)
        assert_that(sets[0].name).is_equal_to("altered text")
        assert_that(sets[0].id).is_equal_to(
            uuid.UUID("9a3222d3-46e9-591b-8101-68d406cb0360")
        )

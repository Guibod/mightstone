import pathlib
import uuid

from mightstone.services.mtgjson.models import (
    SerializableCardAtomic,
    SerializableCardPrices,
    SerializableCardSet,
    SerializableDeck,
    SerializableSet,
    SerializableSetList,
    SerializableTcgPlayerSKUs,
)

from ...testcase import TestBeanie  # type: ignore


class TestSerialization(TestBeanie):
    async def test_cardset(self):
        self.assertEqual(
            SerializableCardSet.get_settings().name, "mightstone_mtgjson_cardsets"
        )

        f = pathlib.Path(__file__).parent.joinpath("samples/cardset.json")
        card = SerializableCardSet.model_validate_json(f.read_bytes())
        await card.save()

        cards = await SerializableCardSet.find_many().to_list()
        self.assertEqual(len(cards), 1)
        self.assertEqual(cards[0].artist, "Lius Lasahido")
        self.assertEqual(cards[0].id, uuid.UUID("00010d56-fe38-5e35-8aed-518019aa36a5"))

        f = pathlib.Path(__file__).parent.joinpath("samples/cardset.json")
        card2 = SerializableCardSet.model_validate_json(f.read_bytes())
        card2.artist = "altered name"
        await card2.save()

        cards = await SerializableCardSet.find_many().to_list()
        self.assertEqual(len(cards), 1)
        self.assertEqual(cards[0].id, uuid.UUID("00010d56-fe38-5e35-8aed-518019aa36a5"))
        self.assertEqual(cards[0].artist, "altered name")

    async def test_cardprice(self):
        self.assertEqual(
            SerializableCardPrices.get_settings().name, "mightstone_mtgjson_cardprices"
        )

        f = pathlib.Path(__file__).parent.joinpath("samples/cardprices.json")
        card = SerializableCardPrices.model_validate_json(f.read_bytes())
        self.assertEqual(card.paper["cardkingdom"].buylist["foil"]["2022-12-19"], 1.5)
        await card.save()

        cards = await SerializableCardPrices.find_many().to_list()
        self.assertEqual(len(cards), 1)
        self.assertEqual(
            cards[0].paper["cardkingdom"].buylist["foil"]["2022-12-19"], 1.5
        )
        self.assertEqual(cards[0].id, uuid.UUID("00010d56-fe38-5e35-8aed-518019aa36a5"))

        f = pathlib.Path(__file__).parent.joinpath("samples/cardprices.json")
        card2 = SerializableCardPrices.model_validate_json(f.read_bytes())
        card2.paper["cardkingdom"].buylist["foil"]["2022-12-19"] = 500
        await card2.save()

        cards = await SerializableCardPrices.find_many().to_list()
        self.assertEqual(len(cards), 1)
        self.assertEqual(cards[0].id, uuid.UUID("00010d56-fe38-5e35-8aed-518019aa36a5"))
        self.assertEqual(
            cards[0].paper["cardkingdom"].buylist["foil"]["2022-12-19"], 500
        )

    async def test_tcgplayerskus(self):
        self.assertEqual(
            SerializableTcgPlayerSKUs.get_settings().name,
            "mightstone_mtgjson_tcgplayerskus",
        )

        f = pathlib.Path(__file__).parent.joinpath("samples/tcgplayerskus.json")
        sku = SerializableTcgPlayerSKUs.model_validate_json(f.read_bytes())
        self.assertEqual(sku.skus[0].condition, "NEAR MINT")
        await sku.save()

        skus = await SerializableTcgPlayerSKUs.find_many().to_list()
        self.assertEqual(len(skus), 1)
        self.assertEqual(skus[0].skus[0].condition, "NEAR MINT")
        self.assertEqual(skus[0].id, uuid.UUID("00010d56-fe38-5e35-8aed-518019aa36a5"))

        f = pathlib.Path(__file__).parent.joinpath("samples/tcgplayerskus.json")
        sku2 = SerializableTcgPlayerSKUs.model_validate_json(f.read_bytes())
        sku2.skus[0].condition = "altered text"
        await sku2.save()

        skus = await SerializableTcgPlayerSKUs.find_many().to_list()
        self.assertEqual(len(skus), 1)
        self.assertEqual(skus[0].skus[0].condition, "altered text")

    async def test_card_atomic(self):
        self.assertEqual(
            SerializableCardAtomic.get_settings().name, "mightstone_mtgjson_cardatomics"
        )

        f = pathlib.Path(__file__).parent.joinpath("samples/cardatomic.json")
        card = SerializableCardAtomic.model_validate_json(f.read_bytes())
        self.assertEqual(card.ascii_name, '"Lifetime" Pass Holder')
        self.assertEqual(card.faces[0].name, '"Lifetime" Pass Holder')
        await card.save()

        cards = await SerializableCardAtomic.find_many().to_list()
        self.assertEqual(len(cards), 1)
        self.assertEqual(cards[0].faces[0].name, '"Lifetime" Pass Holder')
        self.assertEqual(cards[0].id, uuid.UUID("96cee960-9cb4-50c6-8cce-4439b83f92c0"))

        f = pathlib.Path(__file__).parent.joinpath("samples/cardatomic.json")
        card2 = SerializableCardAtomic.model_validate_json(f.read_bytes())
        card2.faces[0].name = "altered text"
        await card2.save()

        card = await SerializableCardAtomic.find_many().to_list()
        self.assertEqual(len(card), 1)
        self.assertEqual(card[0].faces[0].name, "altered text")

    async def test_deck(self):
        self.assertEqual(
            SerializableDeck.get_settings().name, "mightstone_mtgjson_decks"
        )

        f = pathlib.Path(__file__).parent.joinpath("samples/deck.json")
        deck = SerializableDeck.model_validate_json(f.read_bytes())
        self.assertEqual(deck.name, "Blink 1")
        self.assertEqual(deck.id, uuid.UUID("b4c08a29-f3c5-5fa9-af9d-8fdfa80a004e"))
        await deck.save()

        decks = await SerializableDeck.find_many().to_list()
        self.assertEqual(len(decks), 1)
        self.assertEqual(decks[0].name, "Blink 1")
        self.assertEqual(decks[0].id, uuid.UUID("b4c08a29-f3c5-5fa9-af9d-8fdfa80a004e"))

        f = pathlib.Path(__file__).parent.joinpath("samples/deck.json")
        deck2 = SerializableDeck.model_validate_json(f.read_bytes())
        deck2.code = "altered text"
        await deck2.save()

        decks = await SerializableDeck.find_many().to_list()
        self.assertEqual(len(decks), 1)
        self.assertEqual(decks[0].code, "altered text")
        self.assertEqual(decks[0].id, uuid.UUID("b4c08a29-f3c5-5fa9-af9d-8fdfa80a004e"))

    async def test_set_list(self):
        self.assertEqual(
            SerializableSetList.get_settings().name, "mightstone_mtgjson_setlists"
        )

        f = pathlib.Path(__file__).parent.joinpath("samples/setlist.json")
        set = SerializableSetList.model_validate_json(f.read_bytes())
        self.assertEqual(set.name, "Adventures in the Forgotten Realms")
        self.assertEqual(set.id, uuid.UUID("1832e5f5-212a-5199-9318-71d5dfcdefa7"))
        await set.save()

        sets = await SerializableSetList.find_many().to_list()
        self.assertEqual(len(sets), 1)
        self.assertEqual(sets[0].name, "Adventures in the Forgotten Realms")
        self.assertEqual(sets[0].id, uuid.UUID("1832e5f5-212a-5199-9318-71d5dfcdefa7"))

        f = pathlib.Path(__file__).parent.joinpath("samples/setlist.json")
        set2 = SerializableSetList.model_validate_json(f.read_bytes())
        set2.name = "altered text"
        await set2.save()

        sets = await SerializableSetList.find_many().to_list()
        self.assertEqual(len(sets), 1)
        self.assertEqual(sets[0].name, "altered text")
        self.assertEqual(sets[0].id, uuid.UUID("1832e5f5-212a-5199-9318-71d5dfcdefa7"))

    async def test_set(self):
        self.assertEqual(SerializableSet.get_settings().name, "mightstone_mtgjson_sets")

        f = pathlib.Path(__file__).parent.joinpath("samples/set.json")
        set = SerializableSet.model_validate_json(f.read_bytes())
        self.assertEqual(set.name, "The Brothers' War")
        self.assertEqual(set.id, uuid.UUID("9a3222d3-46e9-591b-8101-68d406cb0360"))
        await set.save()

        sets = await SerializableSet.find_many().to_list()
        self.assertEqual(len(sets), 1)
        self.assertEqual(sets[0].name, "The Brothers' War")
        self.assertEqual(sets[0].id, uuid.UUID("9a3222d3-46e9-591b-8101-68d406cb0360"))

        f = pathlib.Path(__file__).parent.joinpath("samples/set.json")
        set2 = SerializableSet.model_validate_json(f.read_bytes())
        set2.name = "altered text"
        await set2.save()

        sets = await SerializableSet.find_many().to_list()
        self.assertEqual(len(sets), 1)
        self.assertEqual(sets[0].name, "altered text")
        self.assertEqual(sets[0].id, uuid.UUID("9a3222d3-46e9-591b-8101-68d406cb0360"))

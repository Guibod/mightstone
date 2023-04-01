import os.path
import uuid

from mightstone.services.mtgjson.models import (
    CardAtomic,
    CardPrices,
    CardSet,
    Deck,
    Set,
    SetList,
    TcgPlayerSKUs,
)

from ...testcase import TestBeanie  # type: ignore


class TestSerialization(TestBeanie):
    async def test_cardset(self):
        self.assertEqual(CardSet.get_settings().name, "mtgjson_cardsets")

        card = CardSet.parse_file(os.path.dirname(__file__) + "/samples/cardset.json")
        await card.save()

        cards = await CardSet.find_many().to_list()
        self.assertEqual(len(cards), 1)
        self.assertEqual(cards[0].artist, "Lius Lasahido")
        self.assertEqual(cards[0].id, uuid.UUID("00010d56-fe38-5e35-8aed-518019aa36a5"))

        card2 = CardSet.parse_file(os.path.dirname(__file__) + "/samples/cardset.json")
        card2.artist = "altered name"
        await card2.save()

        cards = await CardSet.find_many().to_list()
        self.assertEqual(len(cards), 1)
        self.assertEqual(cards[0].id, uuid.UUID("00010d56-fe38-5e35-8aed-518019aa36a5"))
        self.assertEqual(cards[0].artist, "altered name")

    async def test_cardprice(self):
        self.assertEqual(CardPrices.get_settings().name, "mtgjson_cardprices")

        card = CardPrices.parse_file(
            os.path.dirname(__file__) + "/samples/cardprices.json"
        )
        self.assertEqual(card.paper["cardkingdom"].buylist["foil"]["2022-12-19"], 1.5)
        await card.save()

        cards = await CardPrices.find_many().to_list()
        self.assertEqual(len(cards), 1)
        self.assertEqual(
            cards[0].paper["cardkingdom"].buylist["foil"]["2022-12-19"], 1.5
        )
        self.assertEqual(cards[0].id, uuid.UUID("00010d56-fe38-5e35-8aed-518019aa36a5"))

        card2 = CardPrices.parse_file(
            os.path.dirname(__file__) + "/samples/cardprices.json"
        )
        card2.paper["cardkingdom"].buylist["foil"]["2022-12-19"] = 500
        await card2.save()

        cards = await CardPrices.find_many().to_list()
        self.assertEqual(len(cards), 1)
        self.assertEqual(cards[0].id, uuid.UUID("00010d56-fe38-5e35-8aed-518019aa36a5"))
        self.assertEqual(
            cards[0].paper["cardkingdom"].buylist["foil"]["2022-12-19"], 500
        )

    async def test_tcgplayerskus(self):
        self.assertEqual(TcgPlayerSKUs.get_settings().name, "mtgjson_tcgplayerskus")

        sku = TcgPlayerSKUs.parse_file(
            os.path.dirname(__file__) + "/samples/tcgplayerskus.json"
        )
        self.assertEqual(sku.skus[0].condition, "NEAR MINT")
        await sku.save()

        skus = await TcgPlayerSKUs.find_many().to_list()
        self.assertEqual(len(skus), 1)
        self.assertEqual(skus[0].skus[0].condition, "NEAR MINT")
        self.assertEqual(skus[0].id, uuid.UUID("00010d56-fe38-5e35-8aed-518019aa36a5"))

        sku2 = TcgPlayerSKUs.parse_file(
            os.path.dirname(__file__) + "/samples/tcgplayerskus.json"
        )
        sku2.skus[0].condition = "altered text"
        await sku2.save()

        skus = await TcgPlayerSKUs.find_many().to_list()
        self.assertEqual(len(skus), 1)
        self.assertEqual(skus[0].skus[0].condition, "altered text")

    async def test_card_atomic(self):
        self.assertEqual(CardAtomic.get_settings().name, "mtgjson_cardatomics")

        card = CardAtomic.parse_file(
            os.path.dirname(__file__) + "/samples/cardatomic.json"
        )
        self.assertEqual(card.ascii_name, '"Lifetime" Pass Holder')
        self.assertEqual(card.faces[0].name, '"Lifetime" Pass Holder')
        await card.save()

        cards = await CardAtomic.find_many().to_list()
        self.assertEqual(len(cards), 1)
        self.assertEqual(cards[0].faces[0].name, '"Lifetime" Pass Holder')
        self.assertEqual(cards[0].id, uuid.UUID("96cee960-9cb4-50c6-8cce-4439b83f92c0"))

        card2 = CardAtomic.parse_file(
            os.path.dirname(__file__) + "/samples/cardatomic.json"
        )
        card2.faces[0].name = "altered text"
        await card2.save()

        card = await CardAtomic.find_many().to_list()
        self.assertEqual(len(card), 1)
        self.assertEqual(card[0].faces[0].name, "altered text")

    async def test_deck(self):
        self.assertEqual(Deck.get_settings().name, "mtgjson_decks")

        deck = Deck.parse_file(os.path.dirname(__file__) + "/samples/deck.json")
        self.assertEqual(deck.name, "Blink 1")
        self.assertEqual(deck.id, uuid.UUID("b4c08a29-f3c5-5fa9-af9d-8fdfa80a004e"))
        await deck.save()

        decks = await Deck.find_many().to_list()
        self.assertEqual(len(decks), 1)
        self.assertEqual(decks[0].name, "Blink 1")
        self.assertEqual(decks[0].id, uuid.UUID("b4c08a29-f3c5-5fa9-af9d-8fdfa80a004e"))

        deck2 = Deck.parse_file(os.path.dirname(__file__) + "/samples/deck.json")
        deck2.code = "altered text"
        await deck2.save()

        decks = await Deck.find_many().to_list()
        self.assertEqual(len(decks), 1)
        self.assertEqual(decks[0].code, "altered text")
        self.assertEqual(decks[0].id, uuid.UUID("b4c08a29-f3c5-5fa9-af9d-8fdfa80a004e"))

    async def test_set_list(self):
        self.assertEqual(SetList.get_settings().name, "mtgjson_setlists")

        set = SetList.parse_file(os.path.dirname(__file__) + "/samples/setlist.json")
        self.assertEqual(set.name, "Adventures in the Forgotten Realms")
        self.assertEqual(set.id, uuid.UUID("1832e5f5-212a-5199-9318-71d5dfcdefa7"))
        await set.save()

        sets = await SetList.find_many().to_list()
        self.assertEqual(len(sets), 1)
        self.assertEqual(sets[0].name, "Adventures in the Forgotten Realms")
        self.assertEqual(sets[0].id, uuid.UUID("1832e5f5-212a-5199-9318-71d5dfcdefa7"))

        set2 = SetList.parse_file(os.path.dirname(__file__) + "/samples/setlist.json")
        set2.name = "altered text"
        await set2.save()

        sets = await SetList.find_many().to_list()
        self.assertEqual(len(sets), 1)
        self.assertEqual(sets[0].name, "altered text")
        self.assertEqual(sets[0].id, uuid.UUID("1832e5f5-212a-5199-9318-71d5dfcdefa7"))

    async def test_set(self):
        self.assertEqual(Set.get_settings().name, "mtgjson_sets")

        set = Set.parse_file(os.path.dirname(__file__) + "/samples/set.json")
        self.assertEqual(set.name, "The Brothers' War")
        self.assertEqual(set.id, uuid.UUID("9a3222d3-46e9-591b-8101-68d406cb0360"))
        await set.save()

        sets = await Set.find_many().to_list()
        self.assertEqual(len(sets), 1)
        self.assertEqual(sets[0].name, "The Brothers' War")
        self.assertEqual(sets[0].id, uuid.UUID("9a3222d3-46e9-591b-8101-68d406cb0360"))

        set2 = Set.parse_file(os.path.dirname(__file__) + "/samples/set.json")
        set2.name = "altered text"
        await set2.save()

        sets = await Set.find_many().to_list()
        self.assertEqual(len(sets), 1)
        self.assertEqual(sets[0].name, "altered text")
        self.assertEqual(sets[0].id, uuid.UUID("9a3222d3-46e9-591b-8101-68d406cb0360"))

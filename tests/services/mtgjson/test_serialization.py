import pathlib
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

        f = pathlib.Path(__file__).parent.joinpath("samples/cardset.json")
        card = CardSet.model_validate_json(f.read_bytes())
        await card.save()

        cards = await CardSet.find_many().to_list()
        self.assertEqual(len(cards), 1)
        self.assertEqual(cards[0].artist, "Lius Lasahido")
        self.assertEqual(cards[0].id, uuid.UUID("00010d56-fe38-5e35-8aed-518019aa36a5"))

        f = pathlib.Path(__file__).parent.joinpath("samples/cardset.json")
        card2 = CardSet.model_validate_json(f.read_bytes())
        card2.artist = "altered name"
        await card2.save()

        cards = await CardSet.find_many().to_list()
        self.assertEqual(len(cards), 1)
        self.assertEqual(cards[0].id, uuid.UUID("00010d56-fe38-5e35-8aed-518019aa36a5"))
        self.assertEqual(cards[0].artist, "altered name")

    async def test_cardprice(self):
        self.assertEqual(CardPrices.get_settings().name, "mtgjson_cardprices")

        f = pathlib.Path(__file__).parent.joinpath("samples/cardprices.json")
        card = CardPrices.model_validate_json(f.read_bytes())
        self.assertEqual(card.paper["cardkingdom"].buylist["foil"]["2022-12-19"], 1.5)
        await card.save()

        cards = await CardPrices.find_many().to_list()
        self.assertEqual(len(cards), 1)
        self.assertEqual(
            cards[0].paper["cardkingdom"].buylist["foil"]["2022-12-19"], 1.5
        )
        self.assertEqual(cards[0].id, uuid.UUID("00010d56-fe38-5e35-8aed-518019aa36a5"))

        f = pathlib.Path(__file__).parent.joinpath("samples/cardprices.json")
        card2 = CardPrices.model_validate_json(f.read_bytes())
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

        f = pathlib.Path(__file__).parent.joinpath("samples/tcgplayerskus.json")
        sku = TcgPlayerSKUs.model_validate_json(f.read_bytes())
        self.assertEqual(sku.skus[0].condition, "NEAR MINT")
        await sku.save()

        skus = await TcgPlayerSKUs.find_many().to_list()
        self.assertEqual(len(skus), 1)
        self.assertEqual(skus[0].skus[0].condition, "NEAR MINT")
        self.assertEqual(skus[0].id, uuid.UUID("00010d56-fe38-5e35-8aed-518019aa36a5"))

        f = pathlib.Path(__file__).parent.joinpath("samples/tcgplayerskus.json")
        sku2 = TcgPlayerSKUs.model_validate_json(f.read_bytes())
        sku2.skus[0].condition = "altered text"
        await sku2.save()

        skus = await TcgPlayerSKUs.find_many().to_list()
        self.assertEqual(len(skus), 1)
        self.assertEqual(skus[0].skus[0].condition, "altered text")

    async def test_card_atomic(self):
        self.assertEqual(CardAtomic.get_settings().name, "mtgjson_cardatomics")

        f = pathlib.Path(__file__).parent.joinpath("samples/cardatomic.json")
        card = CardAtomic.model_validate_json(f.read_bytes())
        self.assertEqual(card.ascii_name, '"Lifetime" Pass Holder')
        self.assertEqual(card.faces[0].name, '"Lifetime" Pass Holder')
        await card.save()

        cards = await CardAtomic.find_many().to_list()
        self.assertEqual(len(cards), 1)
        self.assertEqual(cards[0].faces[0].name, '"Lifetime" Pass Holder')
        self.assertEqual(cards[0].id, uuid.UUID("96cee960-9cb4-50c6-8cce-4439b83f92c0"))

        f = pathlib.Path(__file__).parent.joinpath("samples/cardatomic.json")
        card2 = CardAtomic.model_validate_json(f.read_bytes())
        card2.faces[0].name = "altered text"
        await card2.save()

        card = await CardAtomic.find_many().to_list()
        self.assertEqual(len(card), 1)
        self.assertEqual(card[0].faces[0].name, "altered text")

    async def test_deck(self):
        self.assertEqual(Deck.get_settings().name, "mtgjson_decks")

        f = pathlib.Path(__file__).parent.joinpath("samples/deck.json")
        deck = Deck.model_validate_json(f.read_bytes())
        self.assertEqual(deck.name, "Blink 1")
        self.assertEqual(deck.id, uuid.UUID("b4c08a29-f3c5-5fa9-af9d-8fdfa80a004e"))
        await deck.save()

        decks = await Deck.find_many().to_list()
        self.assertEqual(len(decks), 1)
        self.assertEqual(decks[0].name, "Blink 1")
        self.assertEqual(decks[0].id, uuid.UUID("b4c08a29-f3c5-5fa9-af9d-8fdfa80a004e"))

        f = pathlib.Path(__file__).parent.joinpath("samples/deck.json")
        deck2 = Deck.model_validate_json(f.read_bytes())
        deck2.code = "altered text"
        await deck2.save()

        decks = await Deck.find_many().to_list()
        self.assertEqual(len(decks), 1)
        self.assertEqual(decks[0].code, "altered text")
        self.assertEqual(decks[0].id, uuid.UUID("b4c08a29-f3c5-5fa9-af9d-8fdfa80a004e"))

    async def test_set_list(self):
        self.assertEqual(SetList.get_settings().name, "mtgjson_setlists")

        f = pathlib.Path(__file__).parent.joinpath("samples/setlist.json")
        set = SetList.model_validate_json(f.read_bytes())
        self.assertEqual(set.name, "Adventures in the Forgotten Realms")
        self.assertEqual(set.id, uuid.UUID("1832e5f5-212a-5199-9318-71d5dfcdefa7"))
        await set.save()

        sets = await SetList.find_many().to_list()
        self.assertEqual(len(sets), 1)
        self.assertEqual(sets[0].name, "Adventures in the Forgotten Realms")
        self.assertEqual(sets[0].id, uuid.UUID("1832e5f5-212a-5199-9318-71d5dfcdefa7"))

        f = pathlib.Path(__file__).parent.joinpath("samples/setlist.json")
        set2 = SetList.model_validate_json(f.read_bytes())
        set2.name = "altered text"
        await set2.save()

        sets = await SetList.find_many().to_list()
        self.assertEqual(len(sets), 1)
        self.assertEqual(sets[0].name, "altered text")
        self.assertEqual(sets[0].id, uuid.UUID("1832e5f5-212a-5199-9318-71d5dfcdefa7"))

    async def test_set(self):
        self.assertEqual(Set.get_settings().name, "mtgjson_sets")

        f = pathlib.Path(__file__).parent.joinpath("samples/set.json")
        set = Set.model_validate_json(f.read_bytes())
        self.assertEqual(set.name, "The Brothers' War")
        self.assertEqual(set.id, uuid.UUID("9a3222d3-46e9-591b-8101-68d406cb0360"))
        await set.save()

        sets = await Set.find_many().to_list()
        self.assertEqual(len(sets), 1)
        self.assertEqual(sets[0].name, "The Brothers' War")
        self.assertEqual(sets[0].id, uuid.UUID("9a3222d3-46e9-591b-8101-68d406cb0360"))

        f = pathlib.Path(__file__).parent.joinpath("samples/set.json")
        set2 = Set.model_validate_json(f.read_bytes())
        set2.name = "altered text"
        await set2.save()

        sets = await Set.find_many().to_list()
        self.assertEqual(len(sets), 1)
        self.assertEqual(sets[0].name, "altered text")
        self.assertEqual(sets[0].id, uuid.UUID("9a3222d3-46e9-591b-8101-68d406cb0360"))

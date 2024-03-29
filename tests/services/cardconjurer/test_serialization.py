import os
from pathlib import Path

from mightstone.services.cardconjurer import Card

from ...testcase import TestBeanie


class TestSerialization(TestBeanie):
    async def test_card(self):
        self.assertEqual(Card.get_settings().name, "cardconjurer_cards")

        card = Card.parse_file(
            Path(os.path.dirname(__file__)).joinpath("samples/Dimirova Smiley.json")
        )
        await card.save()

        cards = await Card.find_many().to_list()
        self.assertEqual(len(cards), 1)

        card = await Card.find_one({"_id": card.id})
        self.assertEqual(card.name, "Dimirova Smiley")
        self.assertEqual(
            card.dependencies.template.url, "custom/11-20-22/template.json"
        )

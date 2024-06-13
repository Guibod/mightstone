import pathlib

from mightstone.services.cardconjurer import SerializableCard

from ...testcase import TestBeanie


class TestSerialization(TestBeanie):
    async def test_card(self):
        self.assertEqual(
            SerializableCard.get_settings().name, "mightstone_cardconjurer_cards"
        )

        f = pathlib.Path(__file__).parent.joinpath("samples/Dimirova Smiley.json")
        card = SerializableCard.model_validate_json(f.read_bytes())
        await card.save()

        cards = await SerializableCard.find_many().to_list()
        self.assertEqual(len(cards), 1)

        card = await SerializableCard.find_one({"_id": card.id})
        self.assertEqual(card.name, "Dimirova Smiley")
        self.assertEqual(
            card.dependencies.template.url, "custom/11-20-22/template.json"
        )

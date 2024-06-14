import pathlib

import pytest
from assertpy import assert_that

from mightstone.services.cardconjurer import SerializableCard


@pytest.mark.asyncio(scope="session")
@pytest.mark.usefixtures("init_beanie_fixture")
async def test_card():
    assert_that(SerializableCard.get_settings().name).is_equal_to(
        "mightstone_cardconjurer_cards"
    )

    f = pathlib.Path(__file__).parent.joinpath("samples/Dimirova Smiley.json")
    card = SerializableCard.model_validate_json(f.read_bytes())
    await card.save()

    cards = await SerializableCard.find_many().to_list()
    assert_that(cards).is_length(1)

    card = await SerializableCard.find_one({"_id": card.id})
    assert_that(card.name).is_equal_to("Dimirova Smiley")
    assert_that(card.dependencies.template.url).is_equal_to(
        "custom/11-20-22/template.json"
    )

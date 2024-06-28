import pathlib
from uuid import UUID

import pytest
from assertpy import assert_that

from mightstone.services.edhrec.models import SerializablePageDeck


@pytest.mark.asyncio(scope="session")
@pytest.mark.usefixtures("init_beanie_fixture")
async def test_card():
    assert_that(SerializablePageDeck.get_settings().name).is_equal_to(
        "mightstone_edhrec_pagedecks"
    )

    expected_id = UUID("0571eb12-e652-52ec-be35-506c07ed0f14")
    f = pathlib.Path(__file__).parent.joinpath(
        "samples/deck.kxd1YhFNO9SSTqGST2veBw.json"
    )
    deck = SerializablePageDeck.model_validate_json(f.read_bytes())
    assert_that(deck.id).is_equal_to(expected_id)
    await deck.save()

    cards = await SerializablePageDeck.find_many().to_list()
    assert_that(cards).is_length(1)

    deck = await SerializablePageDeck.find_one({"_id": deck.id})
    assert_that(deck.header).is_equal_to("Deck with Aegar, the Freezing Flame")

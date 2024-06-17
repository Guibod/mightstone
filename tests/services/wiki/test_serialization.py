import pathlib

import pytest
from assertpy import assert_that

from mightstone.rule.models.color import Color, Identity
from mightstone.services.wiki import SerializableWikiPage
from mightstone.services.wiki.api import WikiExportParser


@pytest.mark.asyncio(scope="session")
@pytest.mark.usefixtures("init_beanie_fixture")
async def test_page():
    assert_that(SerializableWikiPage.get_settings().name).is_equal_to(
        "mightstone_wiki_wikipages"
    )

    data = pathlib.Path(__file__).parent.joinpath("samples/amplify.xml").read_bytes()
    a = WikiExportParser("https://example.com", data).page("Amplify")

    await a.to_serializable().save()

    pages = await SerializableWikiPage.find_many().to_list()
    assert_that(pages).is_length(1)

    page = await SerializableWikiPage.find_one({"_id": a.id})
    assert_that(page.title).is_equal_to("Amplify")
    assert_that(page.source).starts_with("{{Infobox keyword")

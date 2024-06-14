import os
from pathlib import Path

import pytest
from assertpy import assert_that

from mightstone.services.cardconjurer import Card, CardConjurer

from .. import skip_remote_api  # noqa: F401


@pytest.mark.asyncio(scope="session")
class TestCardConjurerRemote:
    @pytest.mark.skip_remote_api
    async def test_angular_remote_is_valid(self):
        m = CardConjurer()
        template = await m.template_async(
            "https://card-conjurer-assets.s3.us-east-1"
            ".amazonaws.com/custom/11-20-22/template.json"
        )

        assert_that(template.asset_root_url).is_equal_to(
            "https://card-conjurer-assets.s3.us-east-1.amazonaws.com",
        )

        assert_that(template.name).is_equal_to("Angular")
        assert_that(len(template.context.image_sets[0].variants)).is_equal_to(8)
        assert_that(template.context.image_sets[0].variants[0].name).is_equal_to(
            "Black Frame",
        )
        assert_that(template.context.image_sets[0].variants[0].src).is_equal_to(
            "custom/11-20-22/black.png",
        )
        assert_that(template.card).is_instance_of(Card)

    @pytest.mark.skip_remote_api
    async def test_simple_token_remote_is_valid(self):
        m = CardConjurer()
        template = await m.template_async(
            "https://card-conjurer-assets.s3.us-east-1"
            ".amazonaws.com/custom/12-8-22/template.json"
        )

        assert_that(template.asset_root_url).is_equal_to(
            "https://card-conjurer-assets.s3.us-east-1.amazonaws.com",
        )

        # assert_that(template.name).is_equal_to( "Simple Tokens")
        assert_that(len(template.context.image_sets[0].variants)).is_equal_to(2)
        assert_that(template.context.image_sets[0].variants[1].name).is_equal_to(
            "Frame With Stats",
        )
        assert_that(template.card).is_instance_of(Card)

    @pytest.mark.skip_remote_api
    async def test_tall_archaic_remote_is_valid(self):
        m = CardConjurer()
        template = await m.template_async(
            "https://card-conjurer-assets.s3.us-east-1"
            ".amazonaws.com/custom/12-18-22/template.json"
        )

        assert_that(template.asset_root_url).is_equal_to(
            "https://card-conjurer-assets.s3.us-east-1.amazonaws.com",
        )
        assert_that(template.name).is_equal_to("Tall Archaic")
        assert_that(len(template.context.image_sets[0].variants)).is_equal_to(9)
        assert_that(template.context.image_sets[0].variants[1].name).is_equal_to(
            "Blue Frame"
        )
        assert_that(template.card).is_instance_of(Card)


@pytest.mark.asyncio(scope="session")
async def test_dimirova_smiley() -> None:
    from PIL import Image
    from pixelmatch.contrib.PIL import pixelmatch

    cc = CardConjurer()
    path = Path(os.path.dirname(__file__)).joinpath("samples/Dimirova Smiley.json")
    card = await cc.card_async(str(path))
    card.asset_root_url = "https://card-conjurer-assets.s3.us-east-1.amazonaws.com"

    original = Image.open(
        Path(os.path.dirname(__file__)).joinpath("samples/Dimirova Smiley.png")
    )
    image = await cc.render_async(card)
    diff = Image.new("RGBA", original.size)

    differing_pixels = pixelmatch(original, image, diff, includeAA=True, threshold=0.1)
    assert_that(differing_pixels, "The image is similar").is_less_than(120000)

    # diff.save(Path(os.path.dirname(__file__)).joinpath("diffpng"))

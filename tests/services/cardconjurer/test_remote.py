import os
from pathlib import Path

import pytest

from mightstone.services.cardconjurer import Card, CardConjurer

from ...testcase import TestBeanie
from .. import skip_remote_api  # noqa: F401


@pytest.mark.asyncio
class TestCardConjurerRemote(TestBeanie):
    @pytest.mark.skip_remote_api
    async def test_angular_remote_is_valid(self):
        m = CardConjurer()
        template = await m.template_async(
            "https://card-conjurer-assets.s3.us-east-1"
            ".amazonaws.com/custom/11-20-22/template.json"
        )

        self.assertEqual(
            template.asset_root_url,
            "https://card-conjurer-assets.s3.us-east-1.amazonaws.com",
        )

        self.assertEqual(template.metadata.name, "Angular")
        self.assertEqual(len(template.context.image_sets[0].variants), 8)
        self.assertEqual(
            template.context.image_sets[0].variants[0].name,
            "Black Frame",
        )
        self.assertEqual(
            template.context.image_sets[0].variants[0].src,
            "custom/11-20-22/black.png",
        )
        self.assertIsInstance(template.card, Card)

    @pytest.mark.skip_remote_api
    async def test_simple_token_remote_is_valid(self):
        m = CardConjurer()
        template = await m.template_async(
            "https://card-conjurer-assets.s3.us-east-1"
            ".amazonaws.com/custom/12-8-22/template.json"
        )

        self.assertEqual(
            template.asset_root_url,
            "https://card-conjurer-assets.s3.us-east-1.amazonaws.com",
        )

        self.assertEqual(template.metadata.name, "Custom Frame Template")
        self.assertEqual(len(template.context.image_sets[0].variants), 2)
        self.assertEqual(
            template.context.image_sets[0].variants[1].name,
            "Frame With Stats",
        )
        self.assertIsInstance(template.card, Card)

    @pytest.mark.skip_remote_api
    async def test_tall_archaic_remote_is_valid(self):
        m = CardConjurer()
        template = await m.template_async(
            "https://card-conjurer-assets.s3.us-east-1"
            ".amazonaws.com/custom/12-18-22/template.json"
        )

        self.assertEqual(
            template.asset_root_url,
            "https://card-conjurer-assets.s3.us-east-1.amazonaws.com",
        )
        self.assertEqual(template.metadata.name, "Tall Archaic")
        self.assertEqual(len(template.context.image_sets[0].variants), 9)
        self.assertEqual(template.context.image_sets[0].variants[1].name, "Blue Frame")
        self.assertIsInstance(template.card, Card)


@pytest.mark.asyncio
class TestImageCompare(TestBeanie):
    async def test_dimirova_smiley(self) -> None:
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

        differing_pixels = pixelmatch(
            original, image, diff, includeAA=True, threshold=0.1
        )
        self.assertLessEqual(differing_pixels, 120000, "The image is similar")

        # diff.save(Path(os.path.dirname(__file__)).joinpath("diffpng"))

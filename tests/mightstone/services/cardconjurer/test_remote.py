import os
import unittest
from pathlib import Path

import pytest

from mightstone.services.cardconjurer import Card, CardConjurer


@pytest.mark.asyncio
@pytest.mark.skip("Feature is broken")
class TestCardConjurerRemote(unittest.IsolatedAsyncioTestCase):
    @pytest.mark.skip_remote_api
    async def test_angular_remote_is_valid(self):
        m = CardConjurer()
        template = await m.template(
            "https://card-conjurer-assets.s3.us-east-1"
            ".amazonaws.com/custom/11-20-22/template.json"
        )

        self.assertEqual(
            template.asset_root_url,
            "https://card-conjurer-assets.s3.us-east-1.amazonaws.com",
        )

        self.assertEqual(template.metadata.name, "Angular")
        self.assertEqual(len(template.context.image_sets["frame"].variants), 8)
        self.assertEqual(
            template.context.image_sets["frame"].variants["black"]["name"],
            "Black Frame",
        )
        self.assertEqual(
            template.context.image_sets["frame"].variants["black"]["src"],
            "custom/11-20-22/black.png",
        )
        self.assertIsInstance(template.card, Card)

    @pytest.mark.skip_remote_api
    async def test_simple_token_remote_is_valid(self):
        m = CardConjurer()
        template = await m.template(
            "https://card-conjurer-assets.s3.us-east-1"
            ".amazonaws.com/custom/12-8-22/template.json"
        )

        self.assertEqual(
            template.asset_root_url,
            "https://card-conjurer-assets.s3.us-east-1.amazonaws.com",
        )

        self.assertEqual(template.metadata.name, "Custom Frame Template")
        self.assertEqual(len(template.context.image_sets["frame"].variants), 2)
        self.assertEqual(
            template.context.image_sets["frame"].variants["stats"]["name"],
            "Frame With Stats",
        )
        self.assertIsInstance(template.card, Card)

    @pytest.mark.skip_remote_api
    async def test_tall_archaic_remote_is_valid(self):
        m = CardConjurer()
        template = await m.template(
            "https://card-conjurer-assets.s3.us-east-1"
            ".amazonaws.com/custom/12-18-22/template.json"
        )

        self.assertEqual(
            template.asset_root_url,
            "https://card-conjurer-assets.s3.us-east-1.amazonaws.com",
        )
        self.assertEqual(template.metadata.name, "Tall Archaic")
        self.assertEqual(len(template.context.image_sets["frame"].variants), 9)
        self.assertEqual(
            template.context.image_sets["frame"].variants["blue"]["name"], "Blue Frame"
        )
        self.assertIsInstance(template.card, Card)


@pytest.mark.asyncio
@pytest.mark.skip("Broken feature")
class TestImageCompare(unittest.IsolatedAsyncioTestCase):
    async def test_dimirova_smiley(self) -> None:
        from PIL import Image
        from pixelmatch.contrib.PIL import pixelmatch

        cc = CardConjurer()
        path = Path(os.path.dirname(__file__)).joinpath("Dimirova Smiley.json")
        card = await cc.card(str(path))
        card.asset_root_url = "https://card-conjurer-assets.s3.us-east-1.amazonaws.com"

        original = Image.open(
            Path(os.path.dirname(__file__)).joinpath("Dimirova Smiley.png")
        )
        image = await cc.render(card)
        diff = Image.new("RGBA", original.size)

        differing_pixels = pixelmatch(
            original, image, diff, includeAA=True, threshold=0.1
        )
        self.assertLessEqual(differing_pixels, 100000, "The image is similar")

        # diff.save(Path(os.path.dirname(__file__)).joinpath("diffpng"))

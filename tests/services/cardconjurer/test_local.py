import os
import re
import unittest
from pathlib import Path

import PIL.ImageFont
import pytest

from mightstone.services.cardconjurer.api import (
    CardConjurer,
    base64_prefix,
    get_wrapped_text,
)
from mightstone.services.cardconjurer.models import Layer, LayerTypes, Tags

from ...testcase import TestBeanie


@pytest.mark.asyncio
class TestCardConjurer(TestBeanie):
    async def asyncSetUp(self) -> None:
        await super().asyncSetUp()
        self.cc = CardConjurer()
        path = Path(os.path.dirname(__file__)).joinpath("samples/Dimirova Smiley.json")
        self.c = await self.cc.card_async(str(path))

    def test_dimirova_smiley_is_valid(self):
        self.assertEqual(self.c.name, "Dimirova Smiley")
        self.assertEqual(self.c.width, 1500)
        self.assertEqual(self.c.height, 2100)

        self.assertEqual(self.c.data.type, LayerTypes.GROUP)

    def test_dimirova_smiley_children_are_layers(self):
        self.assertIsInstance(self.c.data.children[0], Layer)

    def test_find_all(self):
        found = list(self.c.find_many_layer())

        self.assertEqual(len(found), 30)

    def test_find_all_by_unknown_tag(self):
        found = list(self.c.find_many_layer(tag="unknown"))

        self.assertEqual(len(found), 0)

    def test_find_all_by_unknown_name(self):
        found = list(
            self.c.find_many_layer(name="this incredible name should not appear")
        )

        self.assertEqual(len(found), 0)

    def test_find_all_by_unknown_type(self):
        found = list(self.c.find_many_layer(type="fubar"))

        self.assertEqual(len(found), 0)

    def test_find_all_by_existing_tag(self):
        found = list(self.c.find_many_layer(tag=Tags.EDITABLE))

        self.assertEqual(len(found), 12)
        self.assertEqual(found[0].name, "Art")
        self.assertEqual(found[1].name, "Watermark")
        self.assertEqual(found[2].name, "Set Icon")

    def test_find_all_by_existing_type(self):
        found = list(self.c.find_many_layer(type=LayerTypes.TEXT))

        self.assertEqual(len(found), 10)
        self.assertEqual(found[0].name, "Title")
        self.assertEqual(found[1].name, "Symbols")
        self.assertEqual(found[2].name, "Type")

    def test_find_all_by_existing_name(self):
        found = list(self.c.find_many_layer(name="Title"))

        self.assertEqual(len(found), 2)
        self.assertEqual(found[0].name, "Title")
        self.assertEqual(found[0].type, LayerTypes.IMAGE)
        self.assertEqual(found[1].name, "Title")
        self.assertEqual(found[1].type, LayerTypes.TEXT)

    def test_find_all_by_existing_name_through_regular_expression(self):
        pattern = re.compile(r".+le")
        found = list(self.c.find_many_layer(name=pattern))

        self.assertEqual(len(found), 5)
        for layer in found:
            self.assertRegex(layer.name, pattern)

    def test_find_all_by_many_filters(self):
        pattern = re.compile(".+e")
        found = list(
            self.c.find_many_layer(
                name=pattern, type=LayerTypes.TEXT, tag=Tags.EDITABLE
            )
        )

        self.assertEqual(len(found), 7)
        for layer in found:
            self.assertRegex(layer.name, pattern)
            self.assertIn(Tags.EDITABLE, layer.tags)
            self.assertEqual(LayerTypes.TEXT, layer.type)

    def test_find_by_unknown(self):
        self.assertIsNone(self.c.find_one_layer(name="DOES NOT EXIST"))

    def test_find_by_name(self):
        found = self.c.find_one_layer(name="Title")
        self.assertIsNotNone(found)
        self.assertEqual(found.name, "Title")

    def test_find_by_tag_keeps_first(self):
        found = self.c.find_one_layer(tag=Tags.EDITABLE)
        self.assertIsNotNone(found)
        self.assertEqual(found.name, "Art")

    def test_art_src_is_base64_encoded(self):
        found = self.c.find_one_layer(name="Art")
        self.assertIsNotNone(found)
        self.assertRegex(found.src, base64_prefix)

    def test_with_unknown_extension(self): ...


class TextWrapperTest(unittest.TestCase):
    def setUp(self) -> None:
        path = os.path.dirname(__file__)
        self.font_standard = PIL.ImageFont.truetype(
            os.path.join(path, "samples/OpenSans-Regular.ttf"), size=10
        )
        self.font_large = PIL.ImageFont.truetype(
            os.path.join(path, "samples/OpenSans-Regular.ttf"), size=20
        )

    def test_empty_text(self):
        self.assertEqual("", get_wrapped_text("", self.font_standard, 100))

    def test_short_sentence_in_a_very_small_size(self):
        self.assertEqual(
            "short\nsentence", get_wrapped_text("short sentence", self.font_standard, 1)
        )

    def test_short_sentence_text(self):
        self.assertEqual(
            "short sentence",
            get_wrapped_text("short sentence", self.font_standard, 100),
        )

    def test_short_sentence_with_linefeed_text(self):
        self.assertEqual(
            "short\nsentence",
            get_wrapped_text("short\nsentence", self.font_standard, 100),
        )

    def test_long_sentence(self):
        self.assertEqual(
            (
                "a very long sentence\nthat would not fit in\n100 pixels,"
                " how\nunfortunate !"
            ),
            get_wrapped_text(
                (
                    "a very long sentence that would not fit in 100 pixels, how"
                    " unfortunate !"
                ),
                self.font_standard,
                100,
            ),
        )

    def test_two_long_sentence(self):
        self.assertEqual(
            "a long sentence that\nwould not fit.\nAnd another that is\nalso too long",
            get_wrapped_text(
                (
                    "a long sentence that would not fit.\nAnd another that is also too"
                    " long"
                ),
                self.font_standard,
                100,
            ),
        )

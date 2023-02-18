import os
import re
import unittest
from pathlib import Path

import pytest

from mightstone.services.cardconjurer import CardConjurer, base64_prefix
from mightstone.services.cardconjurer.models import Layer, LayerTypes, Tags


@pytest.mark.asyncio
class TestCardConjurer(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self) -> None:
        self.cc = CardConjurer()
        path = Path(os.path.dirname(__file__)).joinpath("Dimirova Smiley.json")
        self.c = await self.cc.card(str(path))

    def test_dimirova_smiley_is_valid(self):
        self.assertEqual(self.c.name, "Dimirova Smiley")
        self.assertEqual(self.c.width, 1500)
        self.assertEqual(self.c.height, 2100)

        self.assertEqual(self.c.data.type, LayerTypes.GROUP)

    def test_dimirova_smiley_children_are_layers(self):
        self.assertIsInstance(self.c.data.children[0], Layer)

    def test_find_all(self):
        found = list(self.c.find_all())

        self.assertEqual(len(found), 30)

    def test_find_all_by_unknown_tag(self):
        found = list(self.c.find_all(tag="unknown"))

        self.assertEqual(len(found), 0)

    def test_find_all_by_unknown_name(self):
        found = list(self.c.find_all(name="this incredible name should not appear"))

        self.assertEqual(len(found), 0)

    def test_find_all_by_unknown_type(self):
        found = list(self.c.find_all(type="fubar"))

        self.assertEqual(len(found), 0)

    def test_find_all_by_existing_tag(self):
        found = list(self.c.find_all(tag=Tags.EDITABLE))

        self.assertEqual(len(found), 12)
        self.assertEqual(found[0].name, "Art")
        self.assertEqual(found[1].name, "Watermark")
        self.assertEqual(found[2].name, "Set Icon")

    def test_find_all_by_existing_type(self):
        found = list(self.c.find_all(type=LayerTypes.TEXT))

        self.assertEqual(len(found), 10)
        self.assertEqual(found[0].name, "Title")
        self.assertEqual(found[1].name, "Symbols")
        self.assertEqual(found[2].name, "Type")

    def test_find_all_by_existing_name(self):
        found = list(self.c.find_all(name="Title"))

        self.assertEqual(len(found), 2)
        self.assertEqual(found[0].name, "Title")
        self.assertEqual(found[0].type, LayerTypes.IMAGE)
        self.assertEqual(found[1].name, "Title")
        self.assertEqual(found[1].type, LayerTypes.TEXT)

    def test_find_all_by_existing_name_through_regular_expression(self):
        pattern = re.compile(r".+le")
        found = list(self.c.find_all(name=pattern))

        self.assertEqual(len(found), 5)
        for layer in found:
            self.assertRegexpMatches(layer.name, pattern)

    def test_find_all_by_many_filters(self):
        pattern = re.compile(".+e")
        found = list(
            self.c.find_all(name=pattern, type=LayerTypes.TEXT, tag=Tags.EDITABLE)
        )

        self.assertEqual(len(found), 7)
        for layer in found:
            self.assertRegexpMatches(layer.name, pattern)
            self.assertIn(Tags.EDITABLE, layer.tags)
            self.assertEqual(LayerTypes.TEXT, layer.type)

    def test_find_by_unknown(self):
        self.assertIsNone(self.c.find(name="DOES NOT EXIST"))

    def test_find_by_name(self):
        found = self.c.find(name="Title")
        self.assertIsNotNone(found)
        self.assertEqual(found.name, "Title")

    def test_find_by_tag_keeps_first(self):
        found = self.c.find(tag=Tags.EDITABLE)
        self.assertIsNotNone(found)
        self.assertEqual(found.name, "Art")

    def test_art_src_is_base64_encoded(self):
        found = self.c.find(name="Art")
        self.assertIsNotNone(found)
        self.assertRegexpMatches(found.src, base64_prefix)

    def test_with_unknown_extension(self):
        ...

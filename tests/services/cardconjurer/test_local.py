import os
import re
import unittest
from pathlib import Path

import PIL.ImageFont
import pytest
from assertpy import assert_that

from mightstone.services.cardconjurer.api import (
    CardConjurer,
    base64_prefix,
    get_wrapped_text,
)
from mightstone.services.cardconjurer.models import Card, Layer, LayerTypes, Tags


@pytest.fixture()
def sample_card() -> Card:
    sample_conjurer = CardConjurer()
    path = Path(os.path.dirname(__file__)).joinpath("samples/Dimirova Smiley.json")
    return sample_conjurer.card(str(path))


class TestCardConjurer:
    def test_dimirova_smiley_is_valid(self, sample_card: Card):
        assert_that(sample_card.name).is_equal_to("Dimirova Smiley")
        assert_that(sample_card.width).is_equal_to(1500)
        assert_that(sample_card.height).is_equal_to(2100)

        assert_that(sample_card.data.type).is_equal_to(LayerTypes.GROUP)

    def test_dimirova_smiley_children_are_layers(self, sample_card: Card):
        assert_that(sample_card.data.children[0]).is_instance_of(Layer)

    def test_find_all(self, sample_card: Card):
        found = list(sample_card.find_many_layer())

        assert_that(len(found)).is_equal_to(30)

    def test_find_all_by_unknown_tag(self, sample_card: Card):
        found = list(sample_card.find_many_layer(tag="unknown"))

        assert_that(len(found)).is_equal_to(0)

    def test_find_all_by_unknown_name(self, sample_card: Card):
        found = list(
            sample_card.find_many_layer(name="this incredible name should not appear")
        )

        assert_that(len(found)).is_equal_to(0)

    def test_find_all_by_unknown_type(self, sample_card: Card):
        found = list(sample_card.find_many_layer(type="fubar"))

        assert_that(len(found)).is_equal_to(0)

    def test_find_all_by_existing_tag(self, sample_card: Card):
        found = list(sample_card.find_many_layer(tag=Tags.EDITABLE))

        assert_that(len(found)).is_equal_to(12)
        assert_that(found[0].name).is_equal_to("Art")
        assert_that(found[1].name).is_equal_to("Watermark")
        assert_that(found[2].name).is_equal_to("Set Icon")

    def test_find_all_by_existing_type(self, sample_card: Card):
        found = list(sample_card.find_many_layer(type=LayerTypes.TEXT))

        assert_that(len(found)).is_equal_to(10)
        assert_that(found[0].name).is_equal_to("Title")
        assert_that(found[1].name).is_equal_to("Symbols")
        assert_that(found[2].name).is_equal_to("Type")

    def test_find_all_by_existing_name(self, sample_card: Card):
        found = list(sample_card.find_many_layer(name="Title"))

        assert_that(len(found)).is_equal_to(2)
        assert_that(found[0].name).is_equal_to("Title")
        assert_that(found[0].type).is_equal_to(LayerTypes.IMAGE)
        assert_that(found[1].name).is_equal_to("Title")
        assert_that(found[1].type).is_equal_to(LayerTypes.TEXT)

    def test_find_all_by_existing_name_through_regular_expression(
        self, sample_card: Card
    ):
        pattern = re.compile(r".+le")
        found = list(sample_card.find_many_layer(name=pattern))

        assert_that(len(found)).is_equal_to(5)
        for layer in found:
            assert_that(layer.name).matches(pattern.pattern)

    def test_find_all_by_many_filters(self, sample_card: Card):
        pattern = re.compile(".+e")
        found = list(
            sample_card.find_many_layer(
                name=pattern, type=LayerTypes.TEXT, tag=Tags.EDITABLE
            )
        )

        assert_that(len(found)).is_equal_to(7)
        for layer in found:
            assert_that(layer.name).matches(pattern.pattern)
            assert_that(layer.tags).contains(Tags.EDITABLE)
            assert_that(LayerTypes.TEXT).is_equal_to(layer.type)

    def test_find_by_unknown(self, sample_card: Card):
        assert_that(sample_card.find_one_layer(name="DOES NOT EXIST")).is_none()

    def test_find_by_name(self, sample_card: Card):
        found = sample_card.find_one_layer(name="Title")
        assert_that(found).is_not_none()
        assert_that(found.name).is_equal_to("Title")

    def test_find_by_tag_keeps_first(self, sample_card: Card):
        found = sample_card.find_one_layer(tag=Tags.EDITABLE)
        assert_that(found).is_not_none()
        assert_that(found.name).is_equal_to("Art")

    def test_art_src_is_base64_encoded(self, sample_card: Card):
        found = sample_card.find_one_layer(name="Art")
        assert_that(found).is_not_none()
        assert_that(found.src).matches(base64_prefix.pattern)


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
        assert_that(get_wrapped_text("", self.font_standard, 100)).is_equal_to("")

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

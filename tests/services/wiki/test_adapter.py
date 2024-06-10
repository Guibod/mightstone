from pathlib import Path
from unittest import TestCase

from pydantic_core._pydantic_core import Url

from mightstone.rule.models.ability import Ability, AbilityType
from mightstone.rule.models.color import Color, Identity
from mightstone.services.wiki.api import WikiAbilityAdapter
from mightstone.services.wiki.models import WikiString, WikiTag

identity_map = {
    "w": Identity([Color(symbol="w", index=0)]),
    "u": Identity([Color(symbol="u", index=1)]),
    "b": Identity([Color(symbol="b", index=2)]),
    "r": Identity([Color(symbol="r", index=3)]),
    "g": Identity([Color(symbol="g", index=4)]),
}


class TypeMapperTest(TestCase):
    def test_valid_tag_three_reorder(self):
        tag = WikiTag(
            tag="Infobox",
            kwargs={
                "type2": WikiString.from_string("Static"),
                "type": WikiString.from_string("Spell"),
                "type3": WikiString.from_string("Triggered"),
            },
        )

        out = WikiAbilityAdapter.map_ability_types(tag)
        self.assertEqual(
            [AbilityType.SPELL, AbilityType.STATIC, AbilityType.TRIGGERED], out
        )

    def test_valid_tag_single(self):
        tag = WikiTag(
            tag="Infobox",
            kwargs={"type": WikiString.from_string("Static")},
        )

        out = WikiAbilityAdapter.map_ability_types(tag)
        self.assertEqual([AbilityType.STATIC], out)

    def test_invalid_tag_single(self):
        tag = WikiTag(
            tag="Infobox",
            kwargs={"type": WikiString.from_string("FOO")},
        )

        out = WikiAbilityAdapter.map_ability_types(tag)
        self.assertEqual([], out)

    def test_partially_invalid_tag_two(self):
        tag = WikiTag(
            tag="Infobox",
            kwargs={
                "type": WikiString.from_string("FOO"),
                "type2": WikiString.from_string("Static"),
            },
        )

        out = WikiAbilityAdapter.map_ability_types(tag)
        self.assertEqual([AbilityType.STATIC], out)


class AdapterTest(TestCase):
    def test_non_wiki_content(self):
        a = WikiAbilityAdapter("https://example.com", b"", identity_map)

        with self.assertRaises(StopIteration):
            next(a.abilities())

    def test_amplify(self):
        data = Path(__file__).parent.joinpath("samples/amplify.xml").read_bytes()
        a = WikiAbilityAdapter("https://example.com", data, identity_map)

        ability = next(a.abilities())

        self.assertIsInstance(ability, Ability)
        self.assertEqual("Amplify", ability.name)
        self.assertEqual(Url("https://example.com/wiki/Amplify"), ability.wiki)
        self.assertEqual([], ability.rules)
        self.assertEqual([AbilityType.STATIC], ability.types)
        self.assertEqual(True, ability.has_cost)
        self.assertEqual("Legions", ability.introduced)
        self.assertEqual("Legions", ability.last_seen)
        self.assertIsNone(ability.storm)
        self.assertEqual({"b": 3, "g": 3, "r": 1, "w": 2}, ability.stats)
        self.assertEqual(
            "As this creature enters the battlefield, put N +1/+1 counters on it for each creature type card you reveal in your hand.",
            ability.reminder,
        )

    def test_affinity_generates_multiples_items(self):
        data = Path(__file__).parent.joinpath("samples/affinity.xml").read_bytes()
        a = WikiAbilityAdapter("https://example.com", data, identity_map)

        iterator = a.abilities()
        ability1 = next(iterator)
        self.assertEqual("Affinity for artifacts", ability1.name)
        ability2 = next(iterator)
        self.assertEqual("Affinity for Plains", ability2.name)
        ability3 = next(iterator)
        self.assertEqual("Affinity for Islands", ability3.name)
        ability4 = next(iterator)
        self.assertEqual("Affinity for Swamps", ability4.name)
        ability5 = next(iterator)
        self.assertEqual("Affinity for Mountains", ability5.name)

    def test_crew(self):
        data = Path(__file__).parent.joinpath("samples/crew.xml").read_bytes()
        a = WikiAbilityAdapter("https://example.com", data, identity_map)

        iterator = a.abilities()
        ability1 = next(iterator)
        self.assertEqual("Crew", ability1.name)

    def test_ascend(self):
        data = Path(__file__).parent.joinpath("samples/ascend.xml").read_bytes()
        a = WikiAbilityAdapter("https://example.com", data, identity_map)

        iterator = a.abilities()
        ability1 = next(iterator)
        self.assertEqual("Ascend", ability1.name)

    def test_glorify_no_stats(self):
        data = Path(__file__).parent.joinpath("samples/glorify.xml").read_bytes()
        a = WikiAbilityAdapter("https://example.com", data, identity_map)

        iterator = a.abilities()
        ability1 = next(iterator)
        self.assertEqual("Glorify", ability1.name)

        self.assertEqual(0, len(ability1.stats))

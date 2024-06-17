from pathlib import Path
from unittest import TestCase

from pydantic_core import Url

from mightstone.rule.models.ability import Ability, AbilityType
from mightstone.services.wiki.api import WikiExportParser, WikiPageAdapter
from mightstone.services.wiki.models import WikiString, WikiTemplate


class TypeMapperTest(TestCase):
    def test_valid_tag_three_reorder(self):
        tag = WikiTemplate(
            name="Infobox",
            kwargs={
                "type2": WikiString(text="Static"),
                "type": WikiString(text="Spell"),
                "type3": WikiString(text="Triggered"),
            },
        )

        out = WikiPageAdapter.map_ability_types(tag)
        self.assertEqual(
            [AbilityType.SPELL, AbilityType.STATIC, AbilityType.TRIGGERED], out
        )

    def test_valid_tag_single(self):
        tag = WikiTemplate(
            name="Infobox",
            kwargs={"type": WikiString(text="Static")},
        )

        out = WikiPageAdapter.map_ability_types(tag)
        self.assertEqual([AbilityType.STATIC], out)

    def test_invalid_tag_single(self):
        tag = WikiTemplate(
            name="Infobox",
            kwargs={"type": WikiString(text="FOO")},
        )

        out = WikiPageAdapter.map_ability_types(tag)
        self.assertEqual([], out)

    def test_partially_invalid_tag_two(self):
        tag = WikiTemplate(
            name="Infobox",
            kwargs={
                "type": WikiString(text="FOO"),
                "type2": WikiString(text="Static"),
            },
        )

        out = WikiPageAdapter.map_ability_types(tag)
        self.assertEqual([AbilityType.STATIC], out)


class WikiExportParserTest(TestCase):
    def test_non_wiki_content(self):
        a = WikiExportParser("https://example.com", b"")

        with self.assertRaises(StopIteration):
            next(a.abilities())

    def test_amplify(self):
        data = Path(__file__).parent.joinpath("samples/amplify.xml").read_bytes()
        a = WikiExportParser("https://example.com", data)

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
            "As this creature enters the battlefield, put N +1/+1 counters on it for each [creature type] card you reveal in your hand.",
            ability.reminder,
        )

    def test_affinity_generates_multiples_items(self):
        data = Path(__file__).parent.joinpath("samples/affinity.xml").read_bytes()
        a = WikiExportParser("https://example.com", data)

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
        a = WikiExportParser("https://example.com", data)

        iterator = a.abilities()
        ability1 = next(iterator)
        self.assertEqual("Crew", ability1.name)

    def test_ascend(self):
        data = Path(__file__).parent.joinpath("samples/ascend.xml").read_bytes()
        a = WikiExportParser("https://example.com", data)

        iterator = a.abilities()
        ability1 = next(iterator)
        self.assertEqual("Ascend", ability1.name)

    def test_glorify_no_stats(self):
        data = Path(__file__).parent.joinpath("samples/glorify.xml").read_bytes()
        a = WikiExportParser("https://example.com", data)

        iterator = a.abilities()
        ability1 = next(iterator)
        self.assertEqual("Glorify", ability1.name)

        self.assertEqual(0, len(ability1.stats))

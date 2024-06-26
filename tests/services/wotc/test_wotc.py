import datetime
import os
import unittest
from io import StringIO
from pathlib import Path

import pytest as pytest
from assertpy import assert_that

from mightstone.services.wotc.api import RuleExplorer
from mightstone.services.wotc.models import (
    ComprehensiveRules,
    Effectiveness,
    Example,
    Glossary,
    Rule,
    RuleRef,
    Ruleset,
    RuleText,
    SectionRef,
)

from .. import skip_remote_api  # noqa: F401


class TestExample(unittest.TestCase):
    def test_example(self):
        example = Example(
            "Example: If one effect reads “You may play an additional "
            "land this turn” and another reads “You can’t play lands "
            "this turn,” the effect that precludes you from playing "
            "lands wins."
        )
        self.assertEqual(
            example.text,
            (
                "If one effect reads “You may play an "
                "additional land this turn” and another reads "
                "“You can’t play lands this turn,” the effect "
                "that precludes you from playing lands wins."
            ),
        )

    def test_example_is_a_string(self):
        example = Example("Example: fuuu")
        self.assertIsInstance(example, str)

    def test_not_an_example(self):
        with pytest.raises(ValueError):
            Example("not an example")


class TestEffectiveness(unittest.TestCase):
    def test_is_string(self):
        effectiveness = Effectiveness(
            "These rules are effective as of February 3, 2023."
        )
        self.assertIsInstance(effectiveness, str)

    def test_date(self):
        effectiveness = Effectiveness(
            "These rules are effective as of February 3, 2023."
        )
        assert_that(effectiveness.date).is_equal_to(datetime.date(2023, 2, 3))

    def test_not_date(self):
        with self.assertRaises(ValueError):
            Effectiveness("not a date")


class TestSectionReference(unittest.TestCase):
    def test_basic(self):
        ref = SectionRef("8")
        ref.section = 8

    def test_dot_notation(self):
        ref = SectionRef("9.")
        ref.section = 9

    def test_not_a_section(self):
        with self.assertRaises(ValueError):
            SectionRef("XX")


class TestRuleReference(unittest.TestCase):
    def test_basic_rule(self):
        ref = RuleRef("704")
        assert_that(ref.rule).is_equal_to(704)
        assert_that(ref.sub_rule).is_equal_to(None)
        assert_that(ref.section).is_equal_to(7)
        assert_that(ref.letter).is_equal_to(None)
        assert_that(ref.canonical).is_equal_to("704")

    def test_basic_sub_rule(self):
        ref = RuleRef("202.5")
        assert_that(ref.rule).is_equal_to(202)
        assert_that(ref.sub_rule).is_equal_to(5)
        assert_that(ref.letter).is_equal_to(None)
        assert_that(ref.section).is_equal_to(2)
        assert_that(ref.canonical).is_equal_to("202.5")

    def test_basic_sub_rule_with_letter(self):
        ref = RuleRef("704.5p")
        assert_that(ref.rule).is_equal_to(704)
        assert_that(ref.sub_rule).is_equal_to(5)
        assert_that(ref.letter).is_equal_to("p")
        assert_that(ref.section).is_equal_to(7)
        assert_that(ref.canonical).is_equal_to("704.5p")

    def test_sub_rule_with_dot_notation(self):
        ref = RuleRef("118.1.")
        assert_that(ref.rule).is_equal_to(118)
        assert_that(ref.sub_rule).is_equal_to(1)
        assert_that(ref.letter).is_equal_to(None)
        assert_that(ref.section).is_equal_to(1)
        assert_that(ref.canonical).is_equal_to("118.1")

    def test_not_a_rule(self):
        with self.assertRaises(ValueError):
            RuleRef("not a reference")

    def test_not_valid_because_o_in_subrule(self):
        with self.assertRaises(ValueError):
            RuleRef("127.12o")

    def test_not_valid_because_l_in_subrule(self):
        with self.assertRaises(ValueError):
            RuleRef("127.12l")

    def test_compare_equality(self):
        assert_that(RuleRef("101") == RuleRef("101")).is_true()
        assert_that(RuleRef("101.") == RuleRef("101")).is_true()
        assert_that(RuleRef("101.1") == RuleRef("101.1")).is_true()
        assert_that(RuleRef("101.1.") == RuleRef("101.1")).is_true()
        assert_that(RuleRef("101.1a") == RuleRef("101.1a")).is_true()
        assert_that(RuleRef("101.1a") == RuleRef("101.1a.")).is_true()
        assert_that(RuleRef("101.1a.") == RuleRef("101.1a")).is_true()

    def test_compare_against_rule(self):
        assert_that(RuleRef("101") > RuleRef("100")).is_true()
        assert_that(RuleRef("101.") > RuleRef("100")).is_true()
        assert_that(RuleRef("101.1") > RuleRef("101")).is_true()
        assert_that(RuleRef("101.1.") > RuleRef("101")).is_true()
        assert_that(RuleRef("101.1a") > RuleRef("101")).is_true()
        assert_that(RuleRef("101.1a.") > RuleRef("101")).is_true()

    def test_compare_against_sub_rule(self):
        assert_that(RuleRef("101") > RuleRef("100.1")).is_true()
        assert_that(RuleRef("101.") > RuleRef("100.1")).is_true()
        assert_that(RuleRef("101.1") > RuleRef("101.0")).is_true()
        assert_that(RuleRef("101.1.") > RuleRef("101.0")).is_true()
        assert_that(RuleRef("101.1a") > RuleRef("101.1")).is_true()
        assert_that(RuleRef("101.1a.") > RuleRef("101.1")).is_true()

    def test_compare_against_sub_rule_dotted(self):
        assert_that(RuleRef("101") > RuleRef("100.1.")).is_true()
        assert_that(RuleRef("101.") > RuleRef("100.1.")).is_true()
        assert_that(RuleRef("101.1") > RuleRef("101.0.")).is_true()
        assert_that(RuleRef("101.1.") > RuleRef("101.0.")).is_true()
        assert_that(RuleRef("101.1a") > RuleRef("101.1.")).is_true()
        assert_that(RuleRef("101.1a.") > RuleRef("101.1.")).is_true()

    def test_compare_against_sub_rule_letter(self):
        assert_that(RuleRef("101") > RuleRef("100.1a")).is_true()
        assert_that(RuleRef("101.") > RuleRef("100.1a")).is_true()
        assert_that(RuleRef("101.1") > RuleRef("101.0a")).is_true()
        assert_that(RuleRef("101.1.") > RuleRef("101.0a")).is_true()
        assert_that(RuleRef("101.1b") > RuleRef("101.1a")).is_true()
        assert_that(RuleRef("101.1b.") > RuleRef("101.1a")).is_true()

    def test_next(self):
        assert_that(RuleRef("100").next()).is_equal_to(RuleRef("101"))
        assert_that(RuleRef("100.").next()).is_equal_to(RuleRef("101"))
        assert_that(RuleRef("100.1").next()).is_equal_to(RuleRef("100.2"))
        assert_that(RuleRef("100.1a").next()).is_equal_to(RuleRef("100.1b"))

    def test_next_o_l(self):
        assert_that(RuleRef("100.1k").next()).is_equal_to(RuleRef("100.1m"))
        assert_that(RuleRef("100.1n").next()).is_equal_to(RuleRef("100.1p"))

    def test_prev(self):
        assert_that(RuleRef("101").prev()).is_equal_to(RuleRef("100"))
        assert_that(RuleRef("101.").prev()).is_equal_to(RuleRef("100"))
        assert_that(RuleRef("100.2").prev()).is_equal_to(RuleRef("100.1"))
        assert_that(RuleRef("100.1b").prev()).is_equal_to(RuleRef("100.1a"))

    def test_prev_first(self):
        self.assertIsNone(RuleRef("100").prev())
        self.assertIsNone(RuleRef("100.1").prev())
        self.assertIsNone(RuleRef("100.1a").prev())

    def test_prev_o_l(self):
        assert_that(RuleRef("100.1p").prev()).is_equal_to(RuleRef("100.1n"))
        assert_that(RuleRef("100.1m").prev()).is_equal_to(RuleRef("100.1k"))


class TestRuleText(unittest.TestCase):
    def test_no_ref(self):
        text = RuleText("fudufafa")
        assert_that(0).is_equal_to(len(text.refs))

    def test_is_a_string(self):
        text = RuleText("i am a string")
        self.assertIsInstance(text, str)
        assert_that(text).is_equal_to("i am a string")

    def test_one_ref(self):
        text = RuleText(
            "A keyword ability that lets a player cast one half of a "
            "split card only from their graveyard. See rule 702.127, "
            "“Aftermath.”"
        )

        assert_that(text.refs).is_equal_to([RuleRef("702.127")])
        self.assertEqual(
            text,
            (
                "A keyword ability that lets a player cast one "
                "half of a split card only from their graveyard. "
                "See rule 702.127, “Aftermath.”"
            ),
        )
        self.assertIsInstance(text, str)

    def test_many_ref(self):
        text = RuleText(
            "100.2d Some formats and casual play variants allow players "
            "to use a supplementary deck of nontraditional Magic cards ("
            "see rule 108.2a). These supplementary decks have their own "
            "deck construction rules. See rule 718, “Attraction Cards;” "
            "rule 901, “Planechase;” and rule 904, “Archenemy.”"
        )

        self.assertEqual(
            text.refs,
            [RuleRef("108.2a"), RuleRef("718"), RuleRef("901"), RuleRef("904")],
        )

    def test_one_section(self):
        text = RuleText(
            "100.1b A multiplayer game is a game that begins with more than"
            " two players. See section 8, “Multiplayer Rules.”"
        )

        assert_that(text.refs).is_equal_to([SectionRef("8")])

    def test_section_and_rule(self):
        text = RuleText(
            "112.1. A spell is a card on the stack. As the first step of "
            "being cast (see rule 601, “Casting Spells”), the card "
            "becomes a spell and is moved to the top of the stack from "
            "the zone it was in, which is usually its owner’s hand. (See "
            "rule 405, “Stack.”) A spell remains on the stack as a spell "
            "until it resolves (see rule 608, “Resolving Spells and "
            "Abilities”), is countered (see rule 701.5), or otherwise "
            "leaves the stack. For more information, see section 6, "
            "“Spells, Abilities, and Effects.”"
        )

        self.assertEqual(
            text.refs,
            [
                RuleRef("601"),
                RuleRef("405"),
                RuleRef("608"),
                RuleRef("701.5"),
                SectionRef("6"),
            ],
        )


class TestRule(unittest.TestCase):
    def test_text_is_str(self):
        rule = Rule.parse_text(
            "111.10c A Gold token is a colorless Gold artifact "
            "token with “Sacrifice this artifact: Add one mana of "
            "any color.”"
        )

        self.assertIsInstance(rule.text, str)
        self.assertEqual(
            rule.text,
            (
                "A Gold token is a colorless Gold artifact token "
                "with “Sacrifice this artifact: Add one mana of "
                "any color.”"
            ),
        )

    def test_ref_is_str(self):
        rule = Rule.parse_text(
            "111.10c A Gold token is a colorless Gold artifact "
            "token with “Sacrifice this artifact: Add one mana of "
            "any color.”"
        )

        self.assertIsInstance(rule.ref, str)
        assert_that(rule.ref).is_equal_to("111.10c")

    def test_text(self):
        rule = Rule.parse_text(
            "111.10c A Gold token is a colorless Gold artifact "
            "token with “Sacrifice this artifact: Add one mana of "
            "any color.”"
        )

        self.assertEqual(
            rule.text,
            (
                "A Gold token is a colorless Gold artifact token "
                "with “Sacrifice this artifact: Add one mana of "
                "any color.”"
            ),
        )
        self.assertIsInstance(rule.text, str)

    def test_reference(self):
        rule = Rule.parse_text(
            "100.2c Commander decks are subject to additional "
            "deckbuilding restrictions and requirements. See rule "
            "903, “Commander,” for details."
        )

        assert_that(rule.ref).is_equal_to(RuleRef("100.2c"))
        self.assertIsInstance(rule.ref, str)

    def test_reference_dotted(self):
        rule = Rule.parse_text(
            "100.2c. Commander decks are subject to additional "
            "deckbuilding restrictions and requirements. See rule "
            "903, “Commander,” for details."
        )

        assert_that(rule.ref).is_equal_to(RuleRef("100.2c."))
        self.assertIsInstance(rule.ref, str)

    def test_not_a_rule(self):
        with self.assertRaises(ValueError):
            Rule.parse_text(
                "Changes may have been made to this document since its "
                "publication. You can download the most recent version "
                "from the Magic rules website at Magic.Wizards.com/Rules. "
                "If you have questions, you can  get the answers from us "
                "at Support.Wizards.com."
            )


class RulesetTest(unittest.TestCase):
    def test_parse_text_empty(self):
        ruleset = Ruleset()
        ruleset.parse_text("")
        assert_that(0).is_equal_to(len(ruleset.rules))

    def test_parse_text_invalid(self):
        ruleset = Ruleset()
        ruleset.parse_text("not a valid\nnot valid either")
        assert_that(0).is_equal_to(len(ruleset.rules))

    def test_parse_text(self):
        ruleset = Ruleset()
        ruleset.parse_text("")
        assert_that(0).is_equal_to(len(ruleset.rules))

    def test_search(self):
        ruleset = Ruleset()
        ruleset.parse_text("123.45a foo bar")
        ruleset.parse_text("123.45b lorem ipsum")
        ruleset.parse_text("123.45c foo baz")

        found = ruleset.search("foo")
        assert_that(len(found)).is_equal_to(2)
        self.assertIn(ruleset["123.45a"], found)
        self.assertIn(ruleset["123.45c"], found)


class TestGlossary(unittest.TestCase):
    def test_search_content(self):
        glossary = Glossary()
        glossary.add("Eat", "foo bar")
        glossary.add("Drink", "foo baz")
        glossary.add("Live", "lorem ipsum")

        found = glossary.search("foo")
        assert_that(len(found)).is_equal_to(2)
        self.assertIn(glossary["Eat"], found)
        self.assertIn(glossary["Drink"], found)

    def test_search_term(self):
        glossary = Glossary()
        glossary.add("Eat", "foo bar")
        glossary.add("Meat", "foo baz")
        glossary.add("Live", "lorem ipsum")

        found = glossary.search("eat")
        assert_that(len(found)).is_equal_to(2)
        self.assertIn(glossary["Eat"], found)
        self.assertIn(glossary["Meat"], found)


class TestComprehensiveRule(unittest.TestCase):
    def setUp(self) -> None:
        self.buffer = StringIO(
            """
        1. Section 1
        100. Lorem ipsum dolor sit amet
        2. Section 2
        200. In hac habitasse platea dictumst.
        201. Maecenas lobortis id magna vitae facilisis.
        3. Section 3
        300. Suspendisse nibh lectus, maximus sed orci vitae, varius egestas turpis.

        100. Lorem ipsum dolor sit amet
        100.1. Consectetur adipiscing elit. Pellentesque maximus justo see rule 300.
        100.2. Aliquam erat volutpat. Lorem ipsum dolor sit amet, consectetur
        100.2a Proin lectus justo, congue sit amet vestibulum at, venenatis non dui.
        Example: Nullam fringilla lectus tempor sollicitudin congue.
        200. In hac habitasse platea dictumst.
        200.1. Nulla rutrum ligula vitae facilisis rutrum. Nunc vel tristique odio.
        201. Maecenas lobortis id magna vitae facilisis. See section 1, rule 100.2a
        Example: Fusce mollis tempor sapien ac vulputate.
        Example: In vel felis a mauris commodo tincidunt.
        300. Suspendisse nibh lectus, maximus sed orci vitae, varius egestas turpis.
        301. Ut fermentum neque erat, a maximus metus cursus nec.
        302. Nunc dapibus dolor non pellentesque tristique.

        Glossary

        Lorem
        Donec laoreet odio vel libero iaculis ornare.
        Morbi sem orci, vestibulum ut felis sed, vehicula mollis elit.

        Ipsum
        Integer id ultrices augue.

        Sapien
        Vivamus finibus suscipit nulla vel blandit. Cras pharetra feugiat sapien,
        eget sollicitudin est dignissim sit amet. Morbi mattis massa enim.
        """
        )

    def test_ruleset_access(self):
        cr = ComprehensiveRules.parse(self.buffer)

        assert_that(cr.ruleset["200"].text).is_equal_to(
            "In hac habitasse platea dictumst."
        )
        self.assertEqual(
            cr.ruleset["201"].text,
            "Maecenas lobortis id magna vitae facilisis. See section 1, rule 100.2a",
        )

        self.assertEqual(
            cr.ruleset["100.2a"].text,
            "Proin lectus justo, congue sit amet vestibulum at, venenatis non dui.",
        )

    def test_ruleset_key_error(self):
        cr = ComprehensiveRules.parse(self.buffer)

        with self.assertRaises(KeyError):
            print(cr.ruleset["not_found"])

    def test_ruleset_reference(self):
        cr = ComprehensiveRules.parse(self.buffer)

        assert_that(len(cr.ruleset["100.1"].text.refs)).is_equal_to(1)
        assert_that(cr.ruleset["100.1"].text.refs).is_equal_to([RuleRef("300.")])

        assert_that(len(cr.ruleset["201"].text.refs)).is_equal_to(2)
        self.assertEqual(
            cr.ruleset["201"].text.refs, [RuleRef("100.2a"), SectionRef("1")]
        )

    def test_ruleset_examples(self):
        cr = ComprehensiveRules.parse(self.buffer)

        assert_that(len(cr.ruleset["100.2a"].examples)).is_equal_to(1)
        self.assertEqual(
            cr.ruleset["100.2a"].examples[0].text,
            "Nullam fringilla lectus tempor sollicitudin congue.",
        )

        assert_that(len(cr.ruleset["201"].examples)).is_equal_to(2)

    def test_glossary_access(self):
        cr = ComprehensiveRules.parse(self.buffer)

        assert_that(cr.glossary["ipsum"].description).is_equal_to(
            "Integer id ultrices augue."
        )
        assert_that(cr.glossary["IPSUM"].description).is_equal_to(
            "Integer id ultrices augue."
        )
        assert_that(cr.glossary["Ipsum"].description).is_equal_to(
            "Integer id ultrices augue."
        )

    def test_glossary_key_error(self):
        cr = ComprehensiveRules.parse(self.buffer)

        with self.assertRaises(KeyError):
            print(cr.glossary["not_found"])

    def test_search_dont_search_example(self):
        cr = ComprehensiveRules.parse(self.buffer)

        found = cr.search("tempor")
        assert_that(len(found)).is_equal_to(0)

    def test_search(self):
        cr = ComprehensiveRules.parse(self.buffer)

        found = cr.search("ipsum")
        assert_that(len(found)).is_equal_to(3)
        self.assertIn(cr.ruleset["100"], found)
        self.assertIn(cr.ruleset["100.2"], found)
        self.assertIn(cr.glossary["Ipsum"], found)

    def test_range_no_up(self):
        cr = ComprehensiveRules.parse(self.buffer)

        found = cr.ruleset.range("100")
        assert_that(len(found)).is_equal_to(4)
        self.assertIn(cr.ruleset["100"], found)
        self.assertIn(cr.ruleset["100.1"], found)
        self.assertIn(cr.ruleset["100.2"], found)
        self.assertIn(cr.ruleset["100.2a"], found)

    def test_range_sub_rule_no_up(self):
        cr = ComprehensiveRules.parse(self.buffer)

        found = cr.ruleset.range("100.2")
        assert_that(len(found)).is_equal_to(2)
        self.assertIn(cr.ruleset["100.2"], found)
        self.assertIn(cr.ruleset["100.2a"], found)

    def test_range_sub_rule(self):
        cr = ComprehensiveRules.parse(self.buffer)

        found = cr.ruleset.range("100", "300")
        assert_that(len(found)).is_equal_to(7)
        self.assertEqual(
            [ref.ref.canonical for ref in found],
            ["100", "100.1", "100.2", "100.2a", "200", "200.1", "201"],
        )
        self.assertIn(cr.ruleset["100"], found)
        self.assertIn(cr.ruleset["100.2"], found)
        self.assertIn(cr.ruleset["201"], found)
        self.assertNotIn(cr.ruleset["300"], found)


class TestRuleExplorer:
    @pytest.mark.asyncio
    async def test_real_rules_have_a_bunch_of_data(self):
        explorer = RuleExplorer()
        path = os.path.join(os.path.dirname(__file__), "../../rule/rule.20230203.txt")
        assert_that(os.path.exists(path)).is_true()

        rule = await explorer.open_async(path)
        assert_that(rule.effective.date).is_equal_to(datetime.date(2023, 2, 3))
        assert_that(len(rule.ruleset)).is_greater_than(2800)
        assert_that(len(rule.glossary)).is_greater_than(200)

    def test_match_text_rule_url_from_html_source(self):
        assert_that(
            RuleExplorer.match_text_last_url(
                Path(__file__).parent.joinpath("samples/rules.html").read_text()
            )
        ).is_equal_to(
            "https://media.wizards.com/2024/downloads/MagicCompRules%2020240607.txt"
        )

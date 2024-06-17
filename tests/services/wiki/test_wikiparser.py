import datetime
import textwrap
from unittest import TestCase

from assertpy import assert_that
from pydantic_core import Url

from mightstone.services.wiki.models import (
    WikiFlow,
    WikiHtml,
    WikiLink,
    WikiList,
    WikiListBullet,
    WikiListItem,
    WikiListItemStyle,
    WikiListStyle,
    WikiPage,
    WikiParagraph,
    WikiRevision,
    WikiString,
    WikiStyledText,
    WikiTemplate,
    WikiTextStyle,
    WikiTitle,
)
from mightstone.services.wiki.parser import (
    PARSER,
    WIKI_HTML,
    WIKI_LINK,
    WIKI_LIST,
    WIKI_LIST_BULLET,
    WIKI_LIST_ITEM,
    WIKI_PARAGRAPH,
    WIKI_STRING,
    WIKI_STYLED,
    WIKI_TEMPLATE,
    WIKI_TITLE,
    MtgWikiParser,
)


def make_page(title: str, source: str):
    return WikiPage(
        id=131211,
        title=title,
        revisions=[
            WikiRevision(
                id=12132312,
                parent_id=12233123123,
                timestamp=datetime.datetime.now(),
                contributor_name="robert",
                contributor_id=123123124,
                origin=13421321,
                source=source,
            )
        ],
        url=Url("https://example.com/wiki/foo"),
    )


class MtgWikiParserInfoboxTest(TestCase):
    def test_empty(self):
        result = MtgWikiParser(make_page("foo", "")).get_infobox()

        self.assertIsNone(result)

    def test_non_matching(self):
        result = MtgWikiParser(make_page("foo", "foo du fafa")).get_infobox()

        self.assertIsNone(result)

    def test_affinity_infobox(self):
        result = MtgWikiParser(
            make_page(
                "Affinity",
                """
            {{Infobox keyword
            | type = Static
            | first = Mirrodin
            | last = Modern Horizons 3
            | extra = for [text]
            | reminder = This spell costs {{1}} less to cast for each [text] you control.
            | stats = {{stats|Affinity for artifacts|A=6|W=2|U=11|R=3|UB=1|WU=1|state=collapsed}}
            {{stats|Affinity for Plains|A=1|state=collapsed}}
            {{stats|Affinity for Islands|A=1|state=collapsed}}
            {{stats|Affinity for Swamps|A=1|state=collapsed}}
            {{stats|Affinity for Mountains|A=1|state=collapsed}}
            {{stats|Affinity for Forests|A=1|state=collapsed}}
            {{stats|Affinity for Tokens|U=1|state=collapsed}}
            {{stats|Affinity for Clowns|R=1|state=collapsed}}
            {{stats|Affinity for Food|GW=1|state=collapsed}}
            {{stats|Affinity for artifact creatures|M=1|state=collapsed}}
            {{stats|Affinity for Equipment|R=3|RW=1|state=collapsed}}
            {{stats|Affinity for Daleks|BR=1|state=collapsed}}
            {{stats|Affinity for historic permanents|W=1|state=collapsed}}
            {{stats|Affinity for planeswalkers|WB=1|state=collapsed}}
            {{stats|Affinity for outlaws|R=1|state=collapsed}}
            | storm = 2
            | storm_ref = <ref>{{EzTumblr|http://markrosewater.tumblr.com/post/707260642788327424/|title=Hi Mark! I saw that there's an affinity...|2023-01-23}}</ref>
            }}
            """,
            )
        ).get_infobox()

        self.assertIsNotNone(result)
        self.assertEqual("keyword", result.extra.as_text())
        self.assertEqual("Static", result.get_kwarg_as_text("type"))
        self.assertEqual("Mirrodin", result.get_kwarg_as_text("first"))
        self.assertEqual("Modern Horizons 3", result.get_kwarg_as_text("last"))
        self.assertEqual("for [text]", result.get_kwarg_as_text("extra"))
        self.assertIsInstance(result.kwargs["reminder"], WikiFlow)
        self.assertEqual(
            "This spell costs  less to cast for each [text] you control.",
            result.get_kwarg_as_text("reminder"),
        )
        self.assertEqual("1", result.get_kwarg("reminder").items[1].name)
        self.assertEqual(
            "2",
            result.get_kwarg_as_text("storm"),
        )
        self.assertIsInstance(result.kwargs["stats"], WikiFlow)
        self.assertIsInstance(result.kwargs["stats"].items[0], WikiTemplate)
        self.assertEqual("stats", result.kwargs["stats"].items[0].name)
        self.assertEqual(
            "Affinity for artifacts",
            result.kwargs["stats"].items[0].args[0].text,
        )
        self.assertEqual(
            "6",
            result.kwargs["stats"].items[0].kwargs["A"].text,
        )
        self.assertEqual(
            "collapsed",
            result.kwargs["stats"].items[0].kwargs["state"].text,
        )
        self.assertIsInstance(result.kwargs["stats"].items[8], WikiTemplate)
        self.assertEqual(
            "stats",
            result.kwargs["stats"].items[8].name,
        )
        self.assertEqual(
            "Affinity for Food", result.kwargs["stats"].items[8].args[0].text
        )
        self.assertEqual(
            result.kwargs["stats"].items[8].kwargs["GW"].text,
            "1",
        )
        assert_that(result.kwargs["storm_ref"]).is_instance_of(WikiHtml)
        assert_that(result.kwargs["storm_ref"].tag).is_equal_to("ref")
        assert_that(result.kwargs["storm_ref"].content).is_instance_of(WikiTemplate)
        assert_that(result.kwargs["storm_ref"].content.name).is_equal_to("EzTumblr")
        assert_that(result.kwargs["storm_ref"].content.args[0].text).is_equal_to(
            "http://markrosewater.tumblr.com/post/707260642788327424/"
        )
        assert_that(result.kwargs["storm_ref"].content.args[1].text).is_equal_to(
            "2023-01-23"
        )
        assert_that(
            result.kwargs["storm_ref"].content.kwargs["title"].text
        ).is_equal_to("Hi Mark! I saw that there's an affinity...")

    def test_buyback_infobox(self):
        result = MtgWikiParser(
            make_page(
                "Buyback",
                """
            {{Infobox keyword
            | type = Static
            | type2 = Static
            | first = Tempest
            | last = Modern Horizons
            | reminder = You may pay an additional [cost] as you cast this spell. If the buyback cost was paid, put this spell into its owner’s hand instead of into that player’s graveyard as it resolves.
            | cost = yes
            | storm = 8
            | storm_ref=<ref>{{EzTumblr|http://markrosewater.tumblr.com/post/157619348008/|title=Where is Buyback on the storm scale?|2017-02-23}}</ref>
            | stats = {{stats|W=9|U=9|B=9|R=8|G=5}}
            }}
            """,
            )
        ).get_infobox()

        self.assertIsNotNone(result)
        self.assertEqual("keyword", result.extra.text)
        self.assertEqual("Static", result.kwargs["type"].text)
        self.assertEqual("Static", result.kwargs["type2"].text)
        self.assertEqual("Tempest", result.kwargs["first"].text)
        self.assertEqual("Modern Horizons", result.kwargs["last"].text)
        self.assertEqual(
            "You may pay an additional [cost] as you cast this spell. If the buyback cost was paid, put this spell into its owner’s hand instead of into that player’s graveyard as it resolves.",
            result.kwargs["reminder"].text,
        )
        self.assertEqual("8", result.kwargs["storm"].text)
        self.assertEqual("yes", result.kwargs["cost"].text)
        self.assertIsInstance(result.kwargs["stats"], WikiTemplate)
        self.assertEqual("stats", result.kwargs["stats"].name)
        self.assertEqual(
            "9",
            result.kwargs["stats"].kwargs["W"].text,
        )
        self.assertEqual(
            "5",
            result.kwargs["stats"].kwargs["G"].text,
        )
        assert_that(result.kwargs["storm_ref"]).is_instance_of(WikiHtml)
        self.assertEqual("ref", result.kwargs["storm_ref"].tag)
        assert_that(result.kwargs["storm_ref"].content).is_instance_of(WikiTemplate)
        self.assertEqual("EzTumblr", result.kwargs["storm_ref"].content.name)
        self.assertEqual(
            "http://markrosewater.tumblr.com/post/157619348008/",
            result.kwargs["storm_ref"].content.args[0].text,
        )
        self.assertEqual(
            "2017-02-23",
            result.kwargs["storm_ref"].content.args[1].text,
        )
        self.assertEqual(
            result.kwargs["storm_ref"].content.kwargs["title"].text,
            "Where is Buyback on the storm scale?",
        )

    def test_crew_infobox(self):
        result = MtgWikiParser(
            make_page(
                "Crew",
                """
            {{Infobox keyword | type = Activated | first = Kaladesh | last = Modern Horizons 3 | N = N | reminder = Tap any number of other untapped creatures you control with total power N or greater: This permanent becomes an artifact creature until end of turn. | stats= {{stats|W=5|U=8|B=3|R=5|G=5|WU=2|UR=1|RW=1|A=54}} }}
            """,
            )
        ).get_infobox()

        self.assertIsNotNone(result)
        self.assertEqual("keyword", result.extra.text)
        self.assertEqual("Activated", result.kwargs["type"].text)

    def test_ascend_infobox(self):
        result = MtgWikiParser(
            make_page(
                "Ascend",
                """
            {{Infobox keyword
            | icon = MTGA Ascend.png
            | type = Spell
            | type2 = Static
            | first = Rivals of Ixalan
            | last = Modern Horizons 3
            | reminder = If you control ten or more permanents, you get the city’s blessing for the rest of the game.
            | stats = {{stats|C=1|U=6|B=5|W=4|R=2|G=2|UB=1|WU=1|A=1|L=1}}
            }}
            """,
            )
        ).get_infobox()

        self.assertIsNotNone(result)
        self.assertEqual("keyword", result.extra.text)
        self.assertEqual("Spell", result.kwargs["type"].text)
        self.assertEqual("Static", result.kwargs["type2"].text)

    def test_cipher_infobox(self):
        result = MtgWikiParser(
            make_page(
                "Cipher",
                """
            {{Infobox keyword 
            | name = Cipher
            | type = Spell
            | type2 = Static
            | first = Gatecrash
            | last = Thunder Junction Commander
            | reminder = Then you may exile this spell card encoded on a creature you control. Whenever that creature deals combat damage to a player, its controller may cast a copy of this card without paying its mana cost.
            | storm_ref = <ref>{{ DailyRef  | making-magic/storm-scale-ravnica-and-return-ravnica-2016-05-02|Storm Scale: Ravnica and Return to Ravnica|[[Mark Rosewater]]|May 2, 2016}}</ref>
            | stats = {{stats|U=6|B=5|UB=3}}
            | storm = 9
            }}
            """,
            )
        ).get_infobox()

        self.assertIsNotNone(result)
        self.assertEqual("keyword", result.extra.text)
        self.assertEqual("Cipher", result.kwargs["name"].text)
        self.assertEqual("Spell", result.kwargs["type"].text)
        self.assertEqual("Static", result.kwargs["type2"].text)
        self.assertEqual("Gatecrash", result.kwargs["first"].text)
        self.assertEqual("Thunder Junction Commander", result.kwargs["last"].text)
        self.assertEqual(
            "Then you may exile this spell card encoded on a creature you control. Whenever that creature deals combat damage to a player, its controller may cast a copy of this card without paying its mana cost.",
            result.kwargs["reminder"].text,
        )
        self.assertEqual("9", result.kwargs["storm"].text)
        self.assertIsInstance(result.kwargs["stats"], WikiTemplate)
        self.assertEqual("stats", result.kwargs["stats"].name)
        self.assertEqual("6", result.kwargs["stats"].kwargs["U"].text)
        self.assertEqual("5", result.kwargs["stats"].kwargs["B"].text)
        self.assertEqual("3", result.kwargs["stats"].kwargs["UB"].text)
        self.assertIsInstance(result.kwargs["storm_ref"], WikiHtml)
        self.assertEqual("ref", result.kwargs["storm_ref"].tag)
        self.assertIsInstance(result.kwargs["storm_ref"].content, WikiTemplate)
        self.assertEqual("DailyRef", result.kwargs["storm_ref"].content.name)
        self.assertEqual(
            "making-magic/storm-scale-ravnica-and-return-ravnica-2016-05-02",
            result.kwargs["storm_ref"].content.args[0].text,
        )
        self.assertEqual(
            "Storm Scale: Ravnica and Return to Ravnica",
            result.kwargs["storm_ref"].content.args[1].text,
        )
        assert_that(result.kwargs["storm_ref"].content.args[2]).is_instance_of(WikiLink)
        assert_that(result.kwargs["storm_ref"].content.args[2].url).is_equal_to(
            "Mark Rosewater"
        )
        assert_that(result.kwargs["storm_ref"].content.args[2].text).is_equal_to(
            "Mark Rosewater"
        )
        self.assertEqual(
            "May 2, 2016",
            result.kwargs["storm_ref"].content.args[3].text,
        )

    def test_ref_as_argument_in_infobox(self):
        result = MtgWikiParser(
            make_page(
                "Foo",
                """
            {{Infobox foo bar baz 
            | <ref>Spell</ref>
            }}
            """,
            )
        ).get_infobox()

        self.assertIsNotNone(result)
        self.assertEqual("foo bar baz", result.extra.text)
        assert_that(result.args[0]).is_instance_of(WikiHtml)
        assert_that(result.args[0].content).is_instance_of(WikiString)
        assert_that(result.args[0].content.text).is_equal_to("Spell")

    def test_nested_tag_in_text(self):
        result = MtgWikiParser(
            make_page(
                "Foo",
                textwrap.dedent(
                    """\
                    {{Infobox foo bar baz 
                    | foo {{mytag | arg | key = value }} bar
                    }}
                    """,
                ),
            )
        ).get_infobox()

        assert_that(result).is_instance_of(WikiTemplate)
        assert_that(result.extra).is_instance_of(WikiString)
        assert_that(result.extra.text).is_equal_to("foo bar baz")
        assert_that(result.args[0]).is_instance_of(WikiFlow)
        assert_that(result.args[0].items[0]).is_instance_of(WikiString)
        assert_that(result.args[0].items[0].text).is_equal_to("foo")
        assert_that(result.args[0].items[1]).is_instance_of(WikiTemplate)
        assert_that(result.args[0].items[1].name).is_equal_to("mytag")
        assert_that(result.args[0].items[1].args[0]).is_instance_of(WikiString)
        assert_that(result.args[0].items[1].args[0].text).is_equal_to("arg")
        assert_that(result.args[0].items[1].kwargs["key"]).is_instance_of(WikiString)
        assert_that(result.args[0].items[1].kwargs["key"].text).is_equal_to("value")
        assert_that(result.args[0].items[2]).is_instance_of(WikiString)
        assert_that(result.args[0].items[2].text).is_equal_to("bar")

    def test_nested_wiki_tag_in_infobox(self):
        result = MtgWikiParser(
            make_page(
                "Foo",
                """
            {{Infobox foo bar baz 
            | stat = {{statistics | a = 1 | 2 | b= 3 }}
            }}
            """,
            )
        ).get_infobox()

        self.assertIsNotNone(result)
        self.assertEqual("foo bar baz", result.extra.text)
        self.assertIsInstance(result.kwargs["stat"], WikiTemplate)
        self.assertEqual("statistics", result.kwargs["stat"].name)
        self.assertEqual("1", result.kwargs["stat"].kwargs["a"].text)
        self.assertEqual("3", result.kwargs["stat"].kwargs["b"].text)
        self.assertEqual("2", result.kwargs["stat"].args[0].text)

    def test_cipher_simplified_infobox(self):
        result = MtgWikiParser(
            make_page(
                "Cipher",
                """
            {{Infobox keyword | name = Cipher | type = Spell
            | type2 = Static
            | first = Gatecrash
            | last = Thunder Junction Commander
            | reminder = Then you may exile this spell card encoded on a creature you control. Whenever that creature deals combat damage to a player, its controller may cast a copy of this card without paying its mana cost.
            | storm = 9
            }}
            """,
            )
        ).get_infobox()
        self.assertIsNotNone(result)
        self.assertEqual("keyword", result.extra.text)
        self.assertEqual("Cipher", result.kwargs["name"].text)
        self.assertEqual("Spell", result.kwargs["type"].text)
        self.assertEqual("Static", result.kwargs["type2"].text)
        self.assertEqual("Gatecrash", result.kwargs["first"].text)
        self.assertEqual("Thunder Junction Commander", result.kwargs["last"].text)
        self.assertEqual(
            "Then you may exile this spell card encoded on a creature you control. Whenever that creature deals combat damage to a player, its controller may cast a copy of this card without paying its mana cost.",
            result.kwargs["reminder"].text,
        )
        self.assertEqual("9", result.kwargs["storm"].text)

    def test_cipher_oneline_infobox(self):
        result = MtgWikiParser(
            make_page(
                "Cipher",
                """
            {{Infobox keyword | name = Cipher | type = Spell | type2 = Static | storm = 9
            }}
            """,
            )
        ).get_infobox()
        self.assertIsNotNone(result)
        self.assertEqual("keyword", result.extra.text)
        self.assertEqual("Cipher", result.kwargs["name"].text)
        self.assertEqual("Spell", result.kwargs["type"].text)
        self.assertEqual("Static", result.kwargs["type2"].text)
        self.assertEqual("9", result.kwargs["storm"].text)

    def test_cipher_within_others_infobox(self):
        result = MtgWikiParser(
            make_page(
                "Cipher",
                """
            some text before
            
            {{Infobox keyword | name = Cipher | type = Spell | type2 = Static | storm = 9
            }}
            
            some text after
            """,
            )
        ).get_infobox()
        self.assertIsNotNone(result)
        self.assertEqual("keyword", result.extra.text)
        self.assertEqual("Cipher", result.kwargs["name"].text)
        self.assertEqual("Spell", result.kwargs["type"].text)
        self.assertEqual("Static", result.kwargs["type2"].text)
        self.assertEqual("9", result.kwargs["storm"].text)

    def test_emerge_wikiblock_with_trailing_pipe(self):
        result = MtgWikiParser(
            make_page(
                "Emerge",
                """
            {{Infobox keyword
            | type = Static
            | first = Eldritch Moon
            | last = Modern Horizons 3
            | cost = yes
            | reminder = You may cast this spell by sacrificing a creature and paying the emerge cost reduced by that creature's mana value.
            | storm = 6
            | storm_ref=<ref>{{EzTumblr|https://markrosewater.tumblr.com/post/703821607899152384|title=I was wondering where Emerge is on the Storm scale?|2022-12-16}}</ref>
            | stats = {{stats|W=1|U=1|C=10|}} By Emerge cost: {{stats|W=1|U=5|B=2|G=3|GU=1}}
            }}
            """,
            )
        ).get_infobox()

        self.assertIsNotNone(result)
        self.assertEqual("keyword", result.extra.text)
        self.assertEqual("Static", result.kwargs["type"].text)
        self.assertEqual("6", result.kwargs["storm"].text)
        self.assertIsInstance(result.kwargs["stats"], WikiFlow)
        self.assertIsInstance(result.kwargs["stats"].items[0], WikiTemplate)
        self.assertIsInstance(result.kwargs["stats"].items[1], WikiString)
        self.assertIsInstance(result.kwargs["stats"].items[2], WikiTemplate)


class MtgWikiParserGlossaryTest(TestCase):
    def test_gr_plus_g_glossary(self):
        result = MtgWikiParser(
            make_page(
                "Deathtouch",
                """
            foo
            
            {{CR+G}}
            
            bar
            """,
            )
        ).get_glossaries()
        self.assertIsNotNone(result)
        self.assertEqual(["Deathtouch"], list(result))

    def test_gr_plus_g_defined_glossary(self):
        result = MtgWikiParser(
            make_page(
                "Hidden Agenda",
                """
            foo
            
            {{CR+G|Hidden Agenda}}
            {{CR|glossary|Double Agenda}}
            
            bar
            """,
            )
        ).get_glossaries()
        self.assertEqual(["Hidden Agenda", "Double Agenda"], list(result))

    def test_multiple_glossary(self):
        result = MtgWikiParser(
            make_page(
                "Fuse",
                """
            foo
            
            {{CR+G}}
            {{CR|glossary|Fused Split Spell}}
            
            bar
            """,
            )
        ).get_glossaries()
        self.assertIsNotNone(result)
        self.assertEqual(
            [
                "Fuse",
                "Fused Split Spell",
            ],
            list(result),
        )


class MtgWikiParserRulesTest(TestCase):
    def test_mono_rule(self):
        result = MtgWikiParser(
            make_page(
                "Kicker",
                """
            foo
            
            {{CR | 702.33h}}
            
            bar
            """,
            )
        ).get_rules()
        self.assertIsNotNone(result)
        self.assertEqual(["702.33h"], list(result))

    def test_multi_rule(self):
        result = MtgWikiParser(
            make_page(
                "Kicker",
                """
            foo
            
            {{CR|103.2b}}
            {{ CR | 116.2g }}
            
            bar
            """,
            )
        ).get_rules()
        self.assertIsNotNone(result)
        self.assertEqual(["103.2b", "116.2g"], list(result))

    def test_rule_nested(self):
        result = MtgWikiParser(
            make_page(
                "Kicker",
                textwrap.dedent(
                    """\
            
                    ==Rules==
                    {{foo | {{CR|103.2b}} {{ CR | 116.2g }} }}
                    
                    ==Rulings==
                    *The spell with cipher is encoded on the creature as part of that spell's resolution, just after the spell's other effects. That card goes directly from the stack to exile. It never goes to the graveyard.
                    """
                ),
            )
        ).get_rules()
        self.assertIsNotNone(result)
        self.assertEqual(["103.2b", "116.2g"], list(result))


class MtgWikiParserTemplatesTest(TestCase):
    def test_get_wiki_tag_ref_content(self):
        result = list(
            MtgWikiParser(
                make_page(
                    "foo",
                    """
            <ref>{{ DailyRef  | making-magic/storm-scale-ravnica-and-return-ravnica-2016-05-02|Storm Scale: Ravnica and Return to Ravnica|[[Mark Rosewater]]|May 2, 2016}}</ref>
            {{NOT_DAILYREF|foo}}
            """,
                )
            ).get_wiki_templates(templates=["DailyRef"])
        )

        self.assertIsNotNone(result)
        self.assertEqual(1, len(result))
        self.assertIsInstance(result[0], WikiTemplate)
        self.assertEqual("DailyRef", result[0].name)
        self.assertEqual(
            "making-magic/storm-scale-ravnica-and-return-ravnica-2016-05-02",
            result[0].args[0].text,
        )
        self.assertEqual(
            "Storm Scale: Ravnica and Return to Ravnica",
            result[0].args[1].text,
        )
        assert_that(result[0].args[2]).is_instance_of(WikiLink)
        assert_that(result[0].args[2].url).is_equal_to("Mark Rosewater")
        assert_that(result[0].args[2].text).is_equal_to("Mark Rosewater")
        self.assertEqual("May 2, 2016", result[0].args[3].text)
        self.assertEqual({}, result[0].kwargs)

    def test_get_wiki_tag_list_of_args(self):
        result = list(
            MtgWikiParser(
                make_page(
                    "foo",
                    """
            {{CR|103.2b}}
            {{CR|116.2g}}
            {{NOT_CR|foo}}
            """,
                )
            ).get_wiki_templates(["CR"])
        )

        self.assertIsNotNone(result)
        self.assertEqual(2, len(result))
        self.assertIsInstance(result[0], WikiTemplate)
        self.assertEqual("CR", result[0].name)
        self.assertEqual("103.2b", result[0].args[0].text)
        self.assertEqual({}, result[0].kwargs)
        self.assertIsInstance(result[1], WikiTemplate)
        self.assertEqual("CR", result[1].name)
        self.assertEqual("116.2g", result[1].args[0].text)
        self.assertEqual({}, result[1].kwargs)

    def test_get_wiki_tag_named_fields(self):
        result = list(
            MtgWikiParser(
                make_page(
                    "foo",
                    """
            {{FOO|a=1|b=2}}
            {{FOO|x=12|y=12}}
            {{NOT_FOO|foo}}
            """,
                )
            ).get_wiki_templates(["FOO"])
        )

        self.assertIsNotNone(result)
        self.assertEqual(2, len(result))
        self.assertIsInstance(result[0], WikiTemplate)
        self.assertEqual("FOO", result[0].name)
        self.assertEqual([], result[0].args)
        self.assertEqual(
            "1",
            result[0].kwargs["a"].text,
        )
        self.assertEqual(
            "2",
            result[0].kwargs["b"].text,
        )
        self.assertIsInstance(result[1], WikiTemplate)
        self.assertEqual("FOO", result[1].name)
        self.assertEqual([], result[1].args)
        self.assertEqual(
            "12",
            result[1].kwargs["x"].text,
        )
        self.assertEqual(
            "12",
            result[1].kwargs["y"].text,
        )

    def test_get_nested_directly(self):
        result = list(
            MtgWikiParser(
                make_page(
                    "foo",
                    """
            {{FOO #1|a=1|b=2}}
            {{bar | string with {{FOO #2|x=12|y=12}} inside }}
            {{bar | foo = {{FOO #3|c=3|d=4}} }}
            {{NOT_FOO|foo}}
            """,
                )
            ).get_wiki_templates(["FOO"], recurse=True)
        )

        self.assertIsNotNone(result)
        self.assertEqual("#1", result[0].extra.text)
        self.assertEqual("#2", result[1].extra.text)
        self.assertEqual("#3", result[2].extra.text)
        self.assertEqual(3, len(result))


class MtgWikiParserStatsTest(TestCase):
    def test_affinity_get_stats(self):
        result = list(
            MtgWikiParser(
                make_page(
                    "Affinity",
                    """
            {{Infobox keyword
            | type = Static
            | first = Mirrodin
            | last = Modern Horizons 3
            | extra = for [text]
            | reminder = This spell costs {{1}} less to cast for each [text] you control.
            | stats = {{stats|Affinity for artifacts|A=6|W=2|U=11|R=3|UB=1|WU=1|state=collapsed}}
            {{stats|Affinity for Plains|A=1|state=collapsed}}
            {{stats|Affinity for Islands|A=1|state=collapsed}}
            {{stats|Affinity for Swamps|A=1|state=collapsed}}
            {{stats|Affinity for Mountains|A=1|state=collapsed}}
            {{stats|Affinity for Forests|A=1|state=collapsed}}
            {{stats|Affinity for Tokens|U=1|state=collapsed}}
            {{stats|Affinity for Clowns|R=1|state=collapsed}}
            {{stats|Affinity for Food|GW=1|state=collapsed}}
            {{stats|Affinity for artifact creatures|M=1|state=collapsed}}
            {{stats|Affinity for Equipment|R=3|RW=1|state=collapsed}}
            {{stats|Affinity for Daleks|BR=1|state=collapsed}}
            {{stats|Affinity for historic permanents|W=1|state=collapsed}}
            {{stats|Affinity for planeswalkers|WB=1|state=collapsed}}
            {{stats|Affinity for outlaws|R=1|state=collapsed}}
            | storm = 2
            | storm_ref = <ref>{{EzTumblr|http://markrosewater.tumblr.com/post/707260642788327424/|title=Hi Mark! I saw that there's an affinity...|2023-01-23}}</ref>
            }}
            """,
                )
            ).get_stats()
        )

        self.assertEqual(result[0].args[0].text, "Affinity for artifacts")
        self.assertEqual(result[0].get_arg_as_text(0), "Affinity for artifacts")
        self.assertEqual(result[4].get_arg_as_text(0), "Affinity for Mountains")
        self.assertEqual(result[8].get_arg_as_text(0), "Affinity for Food")
        self.assertEqual(
            result[12].get_arg_as_text(0), "Affinity for historic permanents"
        )
        self.assertEqual(15, len(result))


class MtgWikiParserLinkTest(TestCase):
    def test_parse_mixed(self):
        generator = MtgWikiParser(
            make_page(
                "Foo",
                textwrap.dedent(
                    """\
                    '''Affinity''' is a [[keyword ability]]. It first appeared in the [[Mirrodin block]].

                    ==Description==
                    The ability is always written as "Affinity for [something]". The most common instance is "Affinity for artifacts" (see <c>Frogmite</c>).

                    Affinity for artifacts appeared as a one-off in ''[[War of the Spark]]'' with <c>Tezzeret, Master of the Bridge</c>.

                    ===Unkeyworded affinity===
                    Affinity was always designed to use a variety of objects, but the disastrous first try gave the keyword a bad reputation. In between the near-two-decade gap between the debut in ''Mirrodin'' block and its return to becoming deciduous ''[[Phyrexia: All Will Be One]]'', various other forms of Affinity were tested for a better sense of how to cost them. However, the mechanic was not keyworded to save keyword learning space, while some designs have wordings that are not practical in using Affinity phrasing. {{card|Saheeli, the Gifted|Commander 2018}}, {{card|Gearseeker Serpent|Kaladesh}}, {{card|Emry, Lurker of the Loch|Throne of Eldraine}} and {{Card|Reality Heist}} are examples of un-keyworded "affinity for artifacts", which were not errata'ed to have affinity after the policy change.

                    Other un-keyworded objects of affinity include:
                    *<c>Gate Colossus</c> ([[Gate]]s)
                    *<c>The Circle of Loyalty</c> ([[Knight]]s)
                    *{{Card|Argivian Phalanx}} (creatures)
                    *{{Card|Magnus the Red}} (grants "Affinity for creature tokens" to instants and sorceries)

                    Ten spells that care about [[Party]] have "Affinity for creatures in your [[Party]]", but the wording for Party and the wording of Affinity mix poorly. In a similar vein: 
                    *<c>Valiant Changeling</c> has "Affinity for creature types".
                    *<c>Khalni Hydra</c> has a unique version where the cost reduced is {{G}} rather than {{1}}, but otherwise has "Affinity for green creatures".
                    *<c>Ghalta, Primal Hunger</c> and <c>Volcanic Salvo</c> have "Affinity for power". <c>The Pride of Hull Clade</c> has "Affinity for toughness"
                    """
                ),
            )
        ).get_wiki_links()

        links = list(generator)

        assert_that(links).is_length(8)
        assert_that(links[0]).is_instance_of(WikiLink)
        assert_that(links[0].url).is_equal_to("keyword ability")
        assert_that(links[0].text).is_equal_to("keyword ability")
        assert_that(links[4]).is_instance_of(WikiLink)
        assert_that(links[4].url).is_equal_to("Gate")
        assert_that(links[4].text).is_equal_to("Gate")


class TestMtgWikiParserCard:
    def test_parse_mixed(self):
        generator = MtgWikiParser(
            make_page(
                "Foo",
                textwrap.dedent(
                    """\
                    '''Affinity''' is a [[keyword ability]]. It first appeared in the [[Mirrodin block]].

                    ==Description==
                    The ability is always written as "Affinity for [something]". The most common instance is "Affinity for artifacts" (see <c>Frogmite</c>).

                    Affinity for artifacts appeared as a one-off in ''[[War of the Spark]]'' with <c>Tezzeret, Master of the Bridge</c>.

                    ===Unkeyworded affinity===
                    Affinity was always designed to use a variety of objects, but the disastrous first try gave the keyword a bad reputation. In between the near-two-decade gap between the debut in ''Mirrodin'' block and its return to becoming deciduous ''[[Phyrexia: All Will Be One]]'', various other forms of Affinity were tested for a better sense of how to cost them. However, the mechanic was not keyworded to save keyword learning space, while some designs have wordings that are not practical in using Affinity phrasing. {{card|Saheeli, the Gifted|Commander 2018}}, {{card|Gearseeker Serpent|Kaladesh}}, {{card|Emry, Lurker of the Loch|Throne of Eldraine}} and {{Card|Reality Heist}} are examples of un-keyworded "affinity for artifacts", which were not errata'ed to have affinity after the policy change.

                    Other un-keyworded objects of affinity include:
                    *<c>Gate Colossus</c> ([[Gate]]s)
                    *<c>The Circle of Loyalty</c> ([[Knight]]s)
                    *{{Card|Argivian Phalanx}} (creatures)
                    *{{Card|Magnus the Red}} (grants "Affinity for creature tokens" to instants and sorceries)

                    Ten spells that care about [[Party]] have "Affinity for creatures in your [[Party]]", but the wording for Party and the wording of Affinity mix poorly. In a similar vein: 
                    *<c>Valiant Changeling</c> has "Affinity for creature types".
                    *<c>Khalni Hydra</c> has a unique version where the cost reduced is {{G}} rather than {{1}}, but otherwise has "Affinity for green creatures".
                    *<c>Ghalta, Primal Hunger</c> and <c>Volcanic Salvo</c> have "Affinity for power". <c>The Pride of Hull Clade</c> has "Affinity for toughness"
                    """
                ),
            )
        ).get_cards()

        cards = list(generator)

        assert_that(cards).is_length(12)
        assert_that(cards[0]).is_instance_of(str)
        assert_that(cards[0]).is_equal_to("Frogmite")
        assert_that(cards[3]).is_instance_of(str)
        assert_that(cards[3]).is_equal_to("The Circle of Loyalty")
        assert_that(cards[11]).is_instance_of(str)
        assert_that(cards[11]).is_equal_to("Magnus the Red")


class MtgWikiParserParseTest(TestCase):
    def test_parse_plain_paragraph(self):
        generator = MtgWikiParser(
            make_page(
                "Foo",
                textwrap.dedent(
                    """\
                    Lorem ipsum dolor sit amet, consectetur adipiscing elit. Mauris vel varius neque. 
                    
                    Duis quis venenatis elit, eu vehicula diam. Vivamus aliquam a tortor sed dapibus. 
                    
                    Praesent aliquet metus nunc, sed suscipit dui varius et. Suspendisse massa velit, posuere id enim sed, gravida facilisis nisl. Morbi malesuada maximus porta.
                    """
                ),
            )
        ).parse()
        parsed = list(generator)

        assert_that(parsed).is_length(3)

        assert_that(parsed[0]).is_instance_of(WikiParagraph)
        assert_that(parsed[0].items[0]).is_instance_of(WikiString)
        assert_that(parsed[0].items[0].text).starts_with("Lorem ipsum")
        assert_that(parsed[0].items[0].text).ends_with("varius neque.")

        assert_that(parsed[1]).is_instance_of(WikiParagraph)
        assert_that(parsed[1].items[0]).is_instance_of(WikiString)
        assert_that(parsed[1].items[0].text).starts_with("Duis quis")
        assert_that(parsed[1].items[0].text).ends_with("sed dapibus.")

        assert_that(parsed[2]).is_instance_of(WikiParagraph)
        assert_that(parsed[2].items[0]).is_instance_of(WikiString)
        assert_that(parsed[2].items[0].text).starts_with("Praesent aliquet")
        assert_that(parsed[2].items[0].text).ends_with("maximus porta.")

    def test_parse_paragraph_with_bold_and_link(self):
        generator = MtgWikiParser(
            make_page(
                "Foo",
                textwrap.dedent(
                    """\
                    Lorem ipsum [[link]] sit [[other-link | displayed text]], consectetur '''bold''' elit ''italic''. Mauris '''''bold and italic''''' neque.
                    """
                ),
            )
        ).parse()
        parsed = list(generator)

        assert_that(parsed).is_length(1)

        assert_that(parsed[0]).is_instance_of(WikiParagraph)
        assert_that(parsed[0].items).is_length(1)

        assert_that(parsed[0].items[0]).is_instance_of(WikiFlow)
        assert_that(parsed[0].items[0].items).is_length(11)

        assert_that(parsed[0].items[0].items[0]).is_instance_of(WikiString)
        assert_that(parsed[0].items[0].items[0].text).is_equal_to("Lorem ipsum")

        assert_that(parsed[0].items[0].items[1]).is_instance_of(WikiLink)
        assert_that(parsed[0].items[0].items[1].text).is_equal_to("link")
        assert_that(parsed[0].items[0].items[1].url).is_equal_to("link")

        assert_that(parsed[0].items[0].items[2]).is_instance_of(WikiString)
        assert_that(parsed[0].items[0].items[2].text).is_equal_to("sit")

        assert_that(parsed[0].items[0].items[3]).is_instance_of(WikiLink)
        assert_that(parsed[0].items[0].items[3].text).is_equal_to("displayed text")
        assert_that(parsed[0].items[0].items[3].url).is_equal_to("other-link")

        assert_that(parsed[0].items[0].items[4]).is_instance_of(WikiString)
        assert_that(parsed[0].items[0].items[4].text).is_equal_to(", consectetur")

        assert_that(parsed[0].items[0].items[5]).is_instance_of(WikiStyledText)
        assert_that(parsed[0].items[0].items[5].style).is_equal_to(WikiTextStyle.BOLD)
        assert_that(parsed[0].items[0].items[5].content.text).is_equal_to("bold")

        assert_that(parsed[0].items[0].items[6]).is_instance_of(WikiString)
        assert_that(parsed[0].items[0].items[6].text).is_equal_to("elit")

        assert_that(parsed[0].items[0].items[7]).is_instance_of(WikiStyledText)
        assert_that(parsed[0].items[0].items[7].style).is_equal_to(WikiTextStyle.ITALIC)
        assert_that(parsed[0].items[0].items[7].content.text).is_equal_to("italic")

        assert_that(parsed[0].items[0].items[8]).is_instance_of(WikiString)
        assert_that(parsed[0].items[0].items[8].text).is_equal_to(". Mauris")

        assert_that(parsed[0].items[0].items[9]).is_instance_of(WikiStyledText)
        assert_that(parsed[0].items[0].items[9].style).is_equal_to(
            WikiTextStyle.ITALIC_BOLD
        )
        assert_that(parsed[0].items[0].items[9].content.text).is_equal_to(
            "bold and italic"
        )

        assert_that(parsed[0].items[0].items[10]).is_instance_of(WikiString)
        assert_that(parsed[0].items[0].items[10].text).is_equal_to("neque.")

    def test_parse_titles(self):
        generator = MtgWikiParser(
            make_page(
                "Foo",
                textwrap.dedent(
                    """\
                    ==level 1==
                    ===level 2===
                    ====level 3====
                    =====level 4=====
                    """
                ),
            )
        ).parse()
        parsed = list(generator)

        assert_that(parsed).is_length(4)

        assert_that(parsed[0]).is_instance_of(WikiTitle)
        assert_that(parsed[0].title).is_equal_to("level 1")
        assert_that(parsed[0].level).is_equal_to(1)

        assert_that(parsed[1]).is_instance_of(WikiTitle)
        assert_that(parsed[1].title).is_equal_to("level 2")
        assert_that(parsed[1].level).is_equal_to(2)

        assert_that(parsed[2]).is_instance_of(WikiTitle)
        assert_that(parsed[2].title).is_equal_to("level 3")
        assert_that(parsed[2].level).is_equal_to(3)

        assert_that(parsed[3]).is_instance_of(WikiTitle)
        assert_that(parsed[3].title).is_equal_to("level 4")
        assert_that(parsed[3].level).is_equal_to(4)

    def test_parse_bullet_list(self):
        generator = MtgWikiParser(
            make_page(
                "Foo",
                textwrap.dedent(
                    """\
                    *one
                    *two
                    **two point one
                    *three
                    """
                ),
            )
        ).parse()
        parsed = list(generator)

        assert_that(parsed).is_length(1)

        assert_that(parsed[0]).is_instance_of(WikiParagraph)
        assert_that(parsed[0].items[0]).is_instance_of(WikiList)
        assert_that(parsed[0].items[0].style).is_equal_to(WikiListStyle.BULLET)
        assert_that(parsed[0].items[0].items).is_length(4)

        assert_that(parsed[0].items[0].items[0]).is_instance_of(WikiListItem)
        assert_that(parsed[0].items[0].items[0].content.text).is_equal_to("one")

        assert_that(parsed[0].items[0].items[1]).is_instance_of(WikiListItem)
        assert_that(parsed[0].items[0].items[1].content.text).is_equal_to("two")

        assert_that(parsed[0].items[0].items[2]).is_instance_of(WikiList)
        assert_that(parsed[0].items[0].items[2].items[0].content.text).is_equal_to(
            "two point one"
        )

        assert_that(parsed[0].items[0].items[3]).is_instance_of(WikiListItem)
        assert_that(parsed[0].items[0].items[3].content.text).is_equal_to("three")

    def test_parse_mixed(self):
        generator = MtgWikiParser(
            make_page(
                "Foo",
                textwrap.dedent(
                    """\
                    '''Affinity''' is a [[keyword ability]]. It first appeared in the [[Mirrodin block]].
    
                    ==Description==
                    The ability is always written as "Affinity for [something]". The most common instance is "Affinity for artifacts" (see <c>Frogmite</c>).
                    
                    Affinity for artifacts appeared as a one-off in ''[[War of the Spark]]'' with <c>Tezzeret, Master of the Bridge</c>.
                    
                    ===Unkeyworded affinity===
                    Affinity was always designed to use a variety of objects, but the disastrous first try gave the keyword a bad reputation. In between the near-two-decade gap between the debut in ''Mirrodin'' block and its return to becoming deciduous ''[[Phyrexia: All Will Be One]]'', various other forms of Affinity were tested for a better sense of how to cost them. However, the mechanic was not keyworded to save keyword learning space, while some designs have wordings that are not practical in using Affinity phrasing. {{card|Saheeli, the Gifted|Commander 2018}}, {{card|Gearseeker Serpent|Kaladesh}}, {{card|Emry, Lurker of the Loch|Throne of Eldraine}} and {{Card|Reality Heist}} are examples of un-keyworded "affinity for artifacts", which were not errata'ed to have affinity after the policy change.
                    
                    Other un-keyworded objects of affinity include:
                    *<c>Gate Colossus</c> ([[Gate]]s)
                    *<c>The Circle of Loyalty</c> ([[Knight]]s)
                    *{{Card|Argivian Phalanx}} (creatures)
                    *{{Card|Magnus the Red}} (grants "Affinity for creature tokens" to instants and sorceries)
                    
                    Ten spells that care about [[Party]] have "Affinity for creatures in your [[Party]]", but the wording for Party and the wording of Affinity mix poorly. In a similar vein: 
                    *<c>Valiant Changeling</c> has "Affinity for creature types".
                    *<c>Khalni Hydra</c> has a unique version where the cost reduced is {{G}} rather than {{1}}, but otherwise has "Affinity for green creatures".
                    *<c>Ghalta, Primal Hunger</c> and <c>Volcanic Salvo</c> have "Affinity for power". <c>The Pride of Hull Clade</c> has "Affinity for toughness"
                    """
                ),
            )
        ).parse()

        parsed = list(generator)
        assert_that(parsed).is_length(8)

        assert_that(parsed[0]).is_instance_of(WikiParagraph)
        assert_that(parsed[0].items[0]).is_instance_of(WikiFlow)
        assert_that(parsed[0].items[0].items[0]).is_instance_of(WikiStyledText)
        assert_that(parsed[0].items[0].items[1]).is_instance_of(WikiString)
        assert_that(parsed[0].items[0].items[2]).is_instance_of(WikiLink)
        assert_that(parsed[0].items[0].items[3]).is_instance_of(WikiString)
        assert_that(parsed[0].items[0].items[4]).is_instance_of(WikiLink)
        assert_that(parsed[0].items[0].items[5]).is_instance_of(WikiString)

        assert_that(parsed[1]).is_instance_of(WikiTitle)

        assert_that(parsed[2]).is_instance_of(WikiParagraph)
        assert_that(parsed[2].items[0]).is_instance_of(WikiFlow)
        assert_that(parsed[2].items[0].items[0]).is_instance_of(WikiString)
        assert_that(parsed[2].items[0].items[1]).is_instance_of(WikiHtml)
        assert_that(parsed[2].items[0].items[1].content).is_instance_of(WikiString)
        assert_that(parsed[2].items[0].items[2]).is_instance_of(WikiString)

        assert_that(parsed[3]).is_instance_of(WikiParagraph)
        assert_that(parsed[3].items[0]).is_instance_of(WikiFlow)
        assert_that(parsed[3].items[0].items[0]).is_instance_of(WikiString)
        assert_that(parsed[3].items[0].items[1]).is_instance_of(WikiStyledText)
        assert_that(parsed[3].items[0].items[2]).is_instance_of(WikiString)
        assert_that(parsed[3].items[0].items[3]).is_instance_of(WikiHtml)
        assert_that(parsed[3].items[0].items[4]).is_instance_of(WikiString)

        assert_that(parsed[7]).is_instance_of(WikiParagraph)
        assert_that(parsed[7].items).is_length(2)
        assert_that(parsed[7].items[0]).is_instance_of(WikiFlow)

        assert_that(parsed[7].items[1]).is_instance_of(WikiList)
        assert_that(parsed[7].items[0].items[0]).is_instance_of(WikiString)
        assert_that(parsed[7].items[0].items[1]).is_instance_of(WikiLink)
        assert_that(parsed[7].items[0].items[2]).is_instance_of(WikiString)
        assert_that(parsed[7].items[0].items[3]).is_instance_of(WikiLink)
        assert_that(parsed[7].items[0].items[4]).is_instance_of(WikiString)

        assert_that(parsed[7].items[1]).is_instance_of(WikiList)
        assert_that(parsed[7].items[1].items).is_length(3)
        assert_that(parsed[7].items[1].items[0]).is_instance_of(WikiListItem)
        assert_that(parsed[7].items[1].items[0].content).is_instance_of(WikiFlow)
        assert_that(parsed[7].items[1].items[0].content.items[0]).is_instance_of(
            WikiHtml
        )
        assert_that(parsed[7].items[1].items[0].content.items[1]).is_instance_of(
            WikiString
        )
        assert_that(parsed[7].items[1].items[1]).is_instance_of(WikiListItem)
        assert_that(parsed[7].items[1].items[2]).is_instance_of(WikiListItem)


class TestPyparsingParserElements:
    def test_wiki_string_factory(self):
        ws = WIKI_STRING.parse_string("foo du fafa")
        assert_that(ws[0]).is_instance_of(WikiString)
        assert_that(ws[0].text).is_equal_to("foo du fafa")

    def test_wiki_title_factory(self):
        wt = WIKI_TITLE.parse_string("=== foo du fafa ===")
        assert_that(wt[0]).is_instance_of(WikiTitle)
        assert_that(wt[0].level).is_equal_to(2)
        assert_that(wt[0].title).is_equal_to("foo du fafa")

    def test_wiki_link_factory(self):
        wl = WIKI_LINK.parse_string("[[Affinity]]")
        assert_that(wl[0]).is_instance_of(WikiLink)
        assert_that(wl[0].url).is_equal_to("Affinity")
        assert_that(wl[0].text).is_equal_to("Affinity")

    def test_wiki_link_with_alt_display_factory(self):
        wl = WIKI_LINK.parse_string("[[Affinity|Foo bar]]")
        assert_that(wl[0]).is_instance_of(WikiLink)
        assert_that(wl[0].url).is_equal_to("Affinity")
        assert_that(wl[0].text).is_equal_to("Foo bar")

    def test_wiki_multiple_matches_factory(self):
        ws = WIKI_STYLED[1, ...].parse_string(
            "'''bold text''' ''italic text''", parse_all=True
        )
        assert_that(ws).is_length(2)

        assert_that(ws[0]).is_instance_of(WikiStyledText)
        assert_that(ws[0].content).is_instance_of(WikiString)
        assert_that(ws[0].content.text).is_equal_to("bold text")
        assert_that(ws[0].style).is_equal_to(WikiTextStyle.BOLD)

        assert_that(ws[1]).is_instance_of(WikiStyledText)
        assert_that(ws[1].content).is_instance_of(WikiString)
        assert_that(ws[1].content.text).is_equal_to("italic text")
        assert_that(ws[1].style).is_equal_to(WikiTextStyle.ITALIC)

    def test_wiki_styled_bold_spaced(self):
        ws = WIKI_STYLED.parse_string("''' bold text '''")
        assert_that(ws[0]).is_instance_of(WikiStyledText)
        assert_that(ws[0].content).is_instance_of(WikiString)
        assert_that(ws[0].content.text).is_equal_to("bold text")
        assert_that(ws[0].style).is_equal_to(WikiTextStyle.BOLD)

    def test_wiki_styled_bold(self):
        ws = WIKI_STYLED.parse_string("'''bold text'''")
        assert_that(ws[0]).is_instance_of(WikiStyledText)
        assert_that(ws[0].content).is_instance_of(WikiString)
        assert_that(ws[0].content.text).is_equal_to("bold text")
        assert_that(ws[0].style).is_equal_to(WikiTextStyle.BOLD)

    def test_wiki_styled_italic(self):
        ws = WIKI_STYLED.parse_string("''italic text''")
        assert_that(ws[0]).is_instance_of(WikiStyledText)
        assert_that(ws[0].content).is_instance_of(WikiString)
        assert_that(ws[0].content.text).is_equal_to("italic text")
        assert_that(ws[0].style).is_equal_to(WikiTextStyle.ITALIC)

    def test_wiki_styled_italic_and_bold(self):
        ws = WIKI_STYLED.parse_string("'''''italic and bold text'''''")
        assert_that(ws[0]).is_instance_of(WikiStyledText)
        assert_that(ws[0].content).is_instance_of(WikiString)
        assert_that(ws[0].content.text).is_equal_to("italic and bold text")
        assert_that(ws[0].style).is_equal_to(WikiTextStyle.ITALIC_BOLD)

    def test_wiki_tag(self):
        wt = WIKI_TEMPLATE.parse_string("{{ Foo extra more stuff | a | b | c = 3 }}")
        assert_that(wt[0]).is_instance_of(WikiTemplate)
        assert_that(wt[0].name).is_equal_to("Foo")
        assert_that(wt[0].extra.text).is_equal_to("extra more stuff")
        assert_that(wt[0].args[0].text).is_equal_to("a")
        assert_that(wt[0].args[1].text).is_equal_to("b")
        assert_that(wt[0].kwargs["c"].text).is_equal_to("3")

    def test_styled_link(self):
        ws = WIKI_STYLED.parse_string("'''[[link]]'''")
        assert_that(ws[0]).is_instance_of(WikiStyledText)
        assert_that(ws[0].style).is_equal_to(WikiTextStyle.BOLD)
        assert_that(ws[0].content).is_instance_of(WikiLink)
        assert_that(ws[0].content.text).is_equal_to("link")
        assert_that(ws[0].content.url).is_equal_to("link")

    def test_styled_link_with_spaces(self):
        ws = WIKI_STYLED.parse_string("'''[[link | displayed value]]'''")
        assert_that(ws[0]).is_instance_of(WikiStyledText)
        assert_that(ws[0].style).is_equal_to(WikiTextStyle.BOLD)
        assert_that(ws[0].content).is_instance_of(WikiLink)
        assert_that(ws[0].content.text).is_equal_to("displayed value")
        assert_that(ws[0].content.url).is_equal_to("link")

    def test_wiki_paragraph_one_line(self):
        wt = WIKI_PARAGRAPH.parse_string(
            "text {{tag}} ''italic'' '''[[Foo|Bold link]]''' more <c>text</c> until the end"
        )
        assert_that(wt[0]).is_instance_of(WikiParagraph)
        assert_that(wt[0].items[0]).is_instance_of(WikiFlow)
        assert_that(wt[0].items[0].items[0]).is_instance_of(WikiString)
        assert_that(wt[0].items[0].items[0].text).is_equal_to("text")
        assert_that(wt[0].items[0].items[1]).is_instance_of(WikiTemplate)
        assert_that(wt[0].items[0].items[1].name).is_equal_to("tag")
        assert_that(wt[0].items[0].items[2]).is_instance_of(WikiStyledText)
        assert_that(wt[0].items[0].items[2].content.text).is_equal_to("italic")
        assert_that(wt[0].items[0].items[2].style).is_equal_to(WikiTextStyle.ITALIC)
        assert_that(wt[0].items[0].items[3].content).is_instance_of(WikiLink)
        assert_that(wt[0].items[0].items[3].content.text).is_equal_to("Bold link")
        assert_that(wt[0].items[0].items[3].style).is_equal_to(WikiTextStyle.BOLD)
        assert_that(wt[0].items[0].items[4]).is_instance_of(WikiString)
        assert_that(wt[0].items[0].items[4].text).is_equal_to("more")
        assert_that(wt[0].items[0].items[5]).is_instance_of(WikiHtml)
        assert_that(wt[0].items[0].items[5].tag).is_equal_to("c")
        assert_that(wt[0].items[0].items[5].content.text).is_equal_to("text")
        assert_that(wt[0].items[0].items[6]).is_instance_of(WikiString)
        assert_that(wt[0].items[0].items[6].text).is_equal_to("until the end")

    def test_foo(self):
        import pyparsing as pp

        newl = pp.CharsNotIn("\n")
        newl1 = pp.DelimitedList(newl, delim="\n\n").leaveWhitespace()
        res = newl1.parseString("a\n\nb\nc")

        parsed = list(res)
        assert_that(parsed).is_length(2)

    def test_foo3(self):
        import pyparsing as pp

        newl = pp.CharsNotIn("x")
        newl1 = pp.DelimitedList(newl, delim="xx")
        res = newl1.parseString("axxbxc")

        parsed = list(res)
        assert_that(parsed).is_length(2)

    def test_foo2(self):
        import pyparsing as pp

        EOP = pp.Suppress(pp.OneOrMore(pp.LineStart() + pp.LineEnd()) | pp.StringEnd())
        EOL = pp.Suppress(pp.LineEnd())

        line = (
            pp.OneOrMore(
                pp.Char(pp.printables + " ") & pp.CharsNotIn("\n"),
                stop_on=pp.Literal("{{") | pp.Literal("[[") | EOL,
            ).leave_whitespace()
        ).set_parse_action(lambda x: "".join(x))

        res = line.parse_string("first line\n")
        parsed = list(res)

        assert_that(parsed[0]).is_equal_to(("first line"))

        paragraph = pp.Opt(EOL) + pp.Group(
            pp.OneOrMore(line + EOL, stop_on=EOP).set_results_name("lines")
        )

        res = paragraph.parse_string("first para\nwith foo")
        parsed = list(res)

        assert_that(parsed[0]).is_length(2)
        assert_that(parsed[0].lines[0]).is_equal_to(("first para"))
        assert_that(parsed[0].lines[1]).is_equal_to(("with foo"))

        res = paragraph.parse_string("first para\nwith foo\n\nsecond")
        parsed = list(res)

        assert_that(parsed[0]).is_length(2)
        assert_that(parsed[0].lines[0]).is_equal_to(("first para"))
        assert_that(parsed[0].lines[1]).is_equal_to(("with foo"))

        paragraphs = pp.OneOrMore(paragraph + EOP).set_results_name("paragraphs")

        foo = textwrap.dedent(
            """\
            first paragraph

            second paragraph
            with another line

            last paragraph has no line feed
            niek

            fooo
            fo
            foooo
            fo

            nounou
            """
        )
        res = paragraphs.parse_string(foo, parse_all=True)
        parsed = list(res)
        assert_that(parsed).is_length(5)

    def test_wiki_paragraphs(self):
        wt = PARSER.set_debug(True).parse_string(
            textwrap.dedent(
                """\
                first paragraph
                
                second paragraph
                with another line
                
                last paragraph has no line feed
                """
            )
        )
        assert_that(wt).is_length(3)
        assert_that(wt[0]).is_instance_of(WikiParagraph)
        assert_that(wt[0].items[0].text).is_equal_to("first paragraph")
        assert_that(wt[1]).is_instance_of(WikiParagraph)
        assert_that(wt[1].items[0].text).is_equal_to("second paragraph")
        assert_that(wt[1].items[1].text).is_equal_to("with another line")
        assert_that(wt[2]).is_instance_of(WikiParagraph)
        assert_that(wt[2].items[0].text).is_equal_to("last paragraph has no line feed")

    def test_wiki_string_all_line(self):
        ws = WIKI_STRING.parse_string("text is long and is not interrupted")
        assert_that(ws[0]).is_instance_of(WikiString)
        assert_that(ws[0].text).is_equal_to("text is long and is not interrupted")

    def test_wiki_string_stopped_by_tag(self):
        ws = WIKI_STRING.parse_string("text is {{tag}}")
        assert_that(ws[0]).is_instance_of(WikiString)
        assert_that(ws[0].text).is_equal_to("text is")

    def test_wiki_string_stopped_by_style(self):
        ws = WIKI_STRING.parse_string("text is '''bold'''")
        assert_that(ws[0]).is_instance_of(WikiString)
        assert_that(ws[0].text).is_equal_to("text is")

    def test_wiki_string_stopped_by_link(self):
        ws = WIKI_STRING.parse_string("text is [[link]]")
        assert_that(ws[0]).is_instance_of(WikiString)
        assert_that(ws[0].text).is_equal_to("text is")

    def test_wiki_string_stopped_by_html_tag(self):
        ws = WIKI_STRING.parse_string("text is <b>bold</bold>")
        assert_that(ws[0]).is_instance_of(WikiString)
        assert_that(ws[0].text).is_equal_to("text is")

    def test_wiki_list_item_bullet(self):
        wli = WIKI_LIST_BULLET.parse_string(":")
        assert_that(wli[0]).is_instance_of(WikiListBullet)
        assert_that(wli[0].level).is_equal_to(0)
        assert_that(wli[0].style).is_instance_of(WikiListItemStyle)
        assert_that(wli[0].style).is_equal_to(WikiListItemStyle.DEFINITION)

        wli = WIKI_LIST_BULLET.parse_string(";")
        assert_that(wli[0]).is_instance_of(WikiListBullet)
        assert_that(wli[0].level).is_equal_to(0)
        assert_that(wli[0].style).is_instance_of(WikiListItemStyle)
        assert_that(wli[0].style).is_equal_to(WikiListItemStyle.TERM)

        wli = WIKI_LIST_BULLET.parse_string("**")
        assert_that(wli[0]).is_instance_of(WikiListBullet)
        assert_that(wli[0].level).is_equal_to(1)
        assert_that(wli[0].style).is_instance_of(WikiListItemStyle)
        assert_that(wli[0].style).is_equal_to(WikiListItemStyle.BULLET)

        wli = WIKI_LIST_BULLET.parse_string("*#")
        assert_that(wli[0]).is_instance_of(WikiListBullet)
        assert_that(wli[0].level).is_equal_to(1)
        assert_that(wli[0].style).is_instance_of(WikiListItemStyle)
        assert_that(wli[0].style).is_equal_to(WikiListItemStyle.NUMBERED)

    def test_wiki_list_item(self):
        wli = WIKI_LIST_ITEM.parse_string("*# two one")
        assert_that(wli[0]).is_instance_of(WikiListItem)
        assert_that(wli[0].level).is_equal_to(1)
        assert_that(wli[0].style).is_equal_to(WikiListItemStyle.NUMBERED)
        assert_that(wli[0].content).is_instance_of(WikiString)
        assert_that(wli[0].content.text).is_equal_to("two one")

    def test_wiki_list(self):
        ws = WIKI_LIST.parse_string(
            """\
            * one
            * two
            ** two one
            ** two two
            * three
            """
        )
        assert_that(ws[0]).is_instance_of(WikiList)
        assert_that(ws[0].items).is_length(4)

        assert_that(ws[0].items[0]).is_instance_of(WikiListItem)
        assert_that(ws[0].items[0].content.text).is_equal_to("one")

        assert_that(ws[0].items[1]).is_instance_of(WikiListItem)
        assert_that(ws[0].items[1].content.text).is_equal_to("two")

        assert_that(ws[0].items[2]).is_instance_of(WikiList)

        assert_that(ws[0].items[2].items[0]).is_instance_of(WikiListItem)
        assert_that(ws[0].items[2].items[0].content.text).is_equal_to("two one")

        assert_that(ws[0].items[2].items[1]).is_instance_of(WikiListItem)
        assert_that(ws[0].items[2].items[1].content.text).is_equal_to("two two")

        assert_that(ws[0].items[3]).is_instance_of(WikiListItem)
        assert_that(ws[0].items[3].content.text).is_equal_to("three")

    def test_wiki_definition_list(self):
        ws = WIKI_LIST.parse_string(
            """\
            * Or create mixed lists
            *# and nest them
            *#* like this.
            *#*; Fruits
            *#*: Apple
            *#*: Blueberry
            """
        )
        assert_that(ws[0]).is_instance_of(WikiList)
        assert_that(ws[0].items).is_length(2)
        assert_that(ws[0].style).is_equal_to(WikiListStyle.BULLET)

        assert_that(ws[0].items[0]).is_instance_of(WikiListItem)
        assert_that(ws[0].items[0].content.text).is_equal_to("Or create mixed lists")

        assert_that(ws[0].items[1]).is_instance_of(WikiList)
        assert_that(ws[0].items[1].style).is_equal_to(WikiListStyle.NUMBERED)

        assert_that(ws[0].items[1].items[0].content.text).is_equal_to("and nest them")

        assert_that(ws[0].items[1].items[1]).is_instance_of(WikiList)
        assert_that(ws[0].items[1].items[1].style).is_equal_to(WikiListStyle.BULLET)

        assert_that(ws[0].items[1].items[1].items[0].content.text).is_equal_to(
            "like this."
        )
        assert_that(ws[0].items[1].items[1].items[1]).is_instance_of(WikiList)
        assert_that(ws[0].items[1].items[1].items[1].style).is_equal_to(
            WikiListStyle.DEF
        )

        assert_that(ws[0].items[1].items[1].items[1].items[0].content.text).is_equal_to(
            "Fruits"
        )
        assert_that(ws[0].items[1].items[1].items[1].items[0].style).is_equal_to(
            WikiListItemStyle.TERM
        )
        assert_that(ws[0].items[1].items[1].items[1].items[1].content.text).is_equal_to(
            "Apple"
        )
        assert_that(ws[0].items[1].items[1].items[1].items[1].style).is_equal_to(
            WikiListItemStyle.DEFINITION
        )
        assert_that(ws[0].items[1].items[1].items[1].items[2].content.text).is_equal_to(
            "Blueberry"
        )
        assert_that(ws[0].items[1].items[1].items[1].items[2].style).is_equal_to(
            WikiListItemStyle.DEFINITION
        )

    def test_wiki_list_mixed(self):
        ws = WIKI_LIST.parse_string(
            """\
            * one
            * two
            *# two one
            *# two two
            * three
            """
        )
        assert_that(ws[0]).is_instance_of(WikiList)
        assert_that(ws[0].items).is_length(4)
        assert_that(ws[0].style).is_equal_to(WikiListStyle.BULLET)

        assert_that(ws[0].items[0]).is_instance_of(WikiListItem)
        assert_that(ws[0].items[0].content.text).is_equal_to("one")

        assert_that(ws[0].items[1]).is_instance_of(WikiListItem)
        assert_that(ws[0].items[1].content.text).is_equal_to("two")

        assert_that(ws[0].items[2]).is_instance_of(WikiList)
        assert_that(ws[0].items[2].style).is_equal_to(WikiListStyle.NUMBERED)

        assert_that(ws[0].items[2].items[0]).is_instance_of(WikiListItem)
        assert_that(ws[0].items[2].items[0].content.text).is_equal_to("two one")

        assert_that(ws[0].items[2].items[1]).is_instance_of(WikiListItem)
        assert_that(ws[0].items[2].items[1].content.text).is_equal_to("two two")

        assert_that(ws[0].items[3]).is_instance_of(WikiListItem)
        assert_that(ws[0].items[3].content.text).is_equal_to("three")

    def test_wiki_html(self):
        wh = WIKI_HTML.parse_string("<c>this is the content</c>")

        assert_that(wh[0]).is_instance_of(WikiHtml)
        assert_that(wh[0].tag).is_equal_to("c")
        assert_that(wh[0].attributes).is_length(0)
        assert_that(wh[0].content).is_instance_of(WikiString)
        assert_that(wh[0].content.text).is_equal_to("this is the content")

    def test_wiki_html_with_attributes(self):
        wh = WIKI_HTML.parse_string('<c class="foo" bar="baz">this is the content</c>')

        assert_that(wh[0].tag).is_equal_to("c")
        assert_that(wh[0].attributes["class"]).is_equal_to("foo")
        assert_that(wh[0].attributes["bar"]).is_equal_to("baz")
        assert_that(wh[0].content).is_instance_of(WikiString)
        assert_that(wh[0].content.text).is_equal_to("this is the content")

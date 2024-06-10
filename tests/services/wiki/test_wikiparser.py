from unittest import TestCase

from mightstone.services.wiki.api import WikiParser
from mightstone.services.wiki.models import WikiString, WikiTag


class WikiParserTest(TestCase):
    def test_empty(self):
        result = WikiParser("foo", "").get_infobox()

        self.assertIsNone(result)

    def test_non_matching(self):
        result = WikiParser("foo", "foo du fafa").get_infobox()

        self.assertIsNone(result)

    def test_affinity_infobox(self):
        result = WikiParser(
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
            | storm_ref = &lt;ref&gt;{{EzTumblr|http://markrosewater.tumblr.com/post/707260642788327424/|title=Hi Mark! I saw that there's an affinity...|2023-01-23}}&lt;/ref&gt;
            }}
            """,
        ).get_infobox()

        self.assertIsNotNone(result)
        self.assertEqual("keyword", result.extra.tokens[0])
        self.assertEqual("Static", result.kwargs["type"].tokens[0])
        self.assertEqual("Mirrodin", result.kwargs["first"].tokens[0])
        self.assertEqual("Modern Horizons 3", result.kwargs["last"].tokens[0])
        self.assertEqual("for [text]", result.kwargs["extra"].tokens[0])
        self.assertIsInstance(result.kwargs["reminder"], WikiString)
        self.assertEqual("This spell costs", result.kwargs["reminder"].tokens[0])
        self.assertEqual("1", result.kwargs["reminder"].tokens[1].tag)
        self.assertEqual(
            "less to cast for each [text] you control.",
            result.kwargs["reminder"].tokens[2],
        )
        self.assertEqual(
            "2",
            result.kwargs["storm"].tokens[0],
        )
        self.assertIsInstance(result.kwargs["stats"], WikiString)
        self.assertIsInstance(result.kwargs["stats"].tokens[0], WikiTag)
        self.assertEqual("stats", result.kwargs["stats"].tokens[0].tag)
        self.assertEqual(
            "Affinity for artifacts",
            result.kwargs["stats"].tokens[0].args[0].tokens[0],
        )
        self.assertEqual(
            "6",
            result.kwargs["stats"].tokens[0].kwargs["A"].tokens[0],
        )
        self.assertEqual(
            "collapsed",
            result.kwargs["stats"].tokens[0].kwargs["state"].tokens[0],
        )
        self.assertIsInstance(result.kwargs["stats"].tokens[8], WikiTag)
        self.assertEqual(
            "stats",
            result.kwargs["stats"].tokens[8].tag,
        )
        self.assertEqual(
            "Affinity for Food", result.kwargs["stats"].tokens[8].args[0].tokens[0]
        )
        self.assertEqual(
            result.kwargs["stats"].tokens[8].kwargs["GW"].tokens[0],
            "1",
        )
        self.assertEqual(
            "&lt;ref&gt;",
            result.kwargs["storm_ref"].tokens[0],
        )
        self.assertEqual(
            "EzTumblr",
            result.kwargs["storm_ref"].tokens[1].tag,
        )
        self.assertEqual(
            "http://markrosewater.tumblr.com/post/707260642788327424/",
            result.kwargs["storm_ref"].tokens[1].args[0].tokens[0],
        )
        self.assertEqual(
            "2023-01-23",
            result.kwargs["storm_ref"].tokens[1].args[1].tokens[0],
        )
        self.assertEqual(
            "Hi Mark! I saw that there's an affinity...",
            result.kwargs["storm_ref"].tokens[1].kwargs["title"].tokens[0],
        )
        self.assertEqual(result.kwargs["storm_ref"].tokens[2], "&lt;/ref&gt;")

    def test_buyback_infobox(self):
        result = WikiParser(
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
            | storm_ref=&lt;ref&gt;{{EzTumblr|http://markrosewater.tumblr.com/post/157619348008/|title=Where is Buyback on the storm scale?|2017-02-23}}&lt;/ref&gt;
            | stats = {{stats|W=9|U=9|B=9|R=8|G=5}}
            }}
            """,
        ).get_infobox()

        self.assertIsNotNone(result)
        self.assertEqual("keyword", result.extra.tokens[0])
        self.assertEqual("Static", result.kwargs["type"].tokens[0])
        self.assertEqual("Static", result.kwargs["type2"].tokens[0])
        self.assertEqual("Tempest", result.kwargs["first"].tokens[0])
        self.assertEqual("Modern Horizons", result.kwargs["last"].tokens[0])
        self.assertEqual(
            "You may pay an additional [cost] as you cast this spell. If the buyback cost was paid, put this spell into its owner’s hand instead of into that player’s graveyard as it resolves.",
            result.kwargs["reminder"].tokens[0],
        )
        self.assertEqual("8", result.kwargs["storm"].tokens[0])
        self.assertEqual("yes", result.kwargs["cost"].tokens[0])
        self.assertIsInstance(result.kwargs["stats"].tokens[0], WikiTag)
        self.assertEqual("stats", result.kwargs["stats"].tokens[0].tag)
        self.assertEqual(
            "9",
            result.kwargs["stats"].tokens[0].kwargs["W"].tokens[0],
        )
        self.assertEqual(
            "5",
            result.kwargs["stats"].tokens[0].kwargs["G"].tokens[0],
        )
        self.assertEqual("&lt;ref&gt;", result.kwargs["storm_ref"].tokens[0])
        self.assertEqual("EzTumblr", result.kwargs["storm_ref"].tokens[1].tag)
        self.assertEqual(
            "http://markrosewater.tumblr.com/post/157619348008/",
            result.kwargs["storm_ref"].tokens[1].args[0].tokens[0],
        )
        self.assertEqual(
            "2017-02-23",
            result.kwargs["storm_ref"].tokens[1].args[1].tokens[0],
        )
        self.assertEqual(
            result.kwargs["storm_ref"].tokens[1].kwargs["title"].tokens[0],
            "Where is Buyback on the storm scale?",
        )
        self.assertEqual("&lt;/ref&gt;", result.kwargs["storm_ref"].tokens[2])

    def test_crew_infobox(self):
        result = WikiParser(
            "Crew",
            """
            {{Infobox keyword | type = Activated | first = Kaladesh | last = Modern Horizons 3 | N = N | reminder = Tap any number of other untapped creatures you control with total power N or greater: This permanent becomes an artifact creature until end of turn. | stats= {{stats|W=5|U=8|B=3|R=5|G=5|WU=2|UR=1|RW=1|A=54}} }}
            """,
        ).get_infobox()

        self.assertIsNotNone(result)
        self.assertEqual("keyword", result.extra.tokens[0])
        self.assertEqual("Activated", result.kwargs["type"].tokens[0])

    def test_ascend_infobox(self):
        result = WikiParser(
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
        ).get_infobox()

        self.assertIsNotNone(result)
        self.assertEqual("keyword", result.extra.tokens[0])
        self.assertEqual("Spell", result.kwargs["type"].tokens[0])
        self.assertEqual("Static", result.kwargs["type2"].tokens[0])

    def test_cipher_infobox(self):
        result = WikiParser(
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
        ).get_infobox()

        self.assertIsNotNone(result)
        self.assertEqual("keyword", result.extra.tokens[0])
        self.assertEqual("Cipher", result.kwargs["name"].tokens[0])
        self.assertEqual("Spell", result.kwargs["type"].tokens[0])
        self.assertEqual("Static", result.kwargs["type2"].tokens[0])
        self.assertEqual("Gatecrash", result.kwargs["first"].tokens[0])
        self.assertEqual("Thunder Junction Commander", result.kwargs["last"].tokens[0])
        self.assertEqual(
            "Then you may exile this spell card encoded on a creature you control. Whenever that creature deals combat damage to a player, its controller may cast a copy of this card without paying its mana cost.",
            result.kwargs["reminder"].tokens[0],
        )
        self.assertEqual("9", result.kwargs["storm"].tokens[0])
        self.assertIsInstance(result.kwargs["stats"], WikiString)
        self.assertIsInstance(result.kwargs["stats"].tokens[0], WikiTag)
        self.assertEqual("stats", result.kwargs["stats"].tokens[0].tag)
        self.assertEqual("6", result.kwargs["stats"].tokens[0].kwargs["U"].tokens[0])
        self.assertEqual("5", result.kwargs["stats"].tokens[0].kwargs["B"].tokens[0])
        self.assertEqual("3", result.kwargs["stats"].tokens[0].kwargs["UB"].tokens[0])
        self.assertIsInstance(result.kwargs["storm_ref"], WikiString)
        self.assertEqual("<ref>", result.kwargs["storm_ref"].tokens[0])
        self.assertIsInstance(result.kwargs["storm_ref"].tokens[1], WikiTag)
        self.assertEqual("DailyRef", result.kwargs["storm_ref"].tokens[1].tag)
        self.assertEqual(
            "making-magic/storm-scale-ravnica-and-return-ravnica-2016-05-02",
            result.kwargs["storm_ref"].tokens[1].args[0].tokens[0],
        )
        self.assertEqual(
            "Storm Scale: Ravnica and Return to Ravnica",
            result.kwargs["storm_ref"].tokens[1].args[1].tokens[0],
        )
        self.assertEqual(
            "[[Mark Rosewater]]",
            result.kwargs["storm_ref"].tokens[1].args[2].tokens[0],
        )
        self.assertEqual(
            "May 2, 2016",
            result.kwargs["storm_ref"].tokens[1].args[3].tokens[0],
        )
        self.assertEqual("</ref>", result.kwargs["storm_ref"].tokens[2])

    def test_ref_as_argument_in_infobox(self):
        result = WikiParser(
            "Foo",
            """
            {{Infobox foo bar baz 
            | <ref>Spell</ref>
            }}
            """,
        ).get_infobox()

        self.assertIsNotNone(result)
        self.assertEqual("foo bar baz", result.extra.tokens[0])
        self.assertEqual("<ref>Spell</ref>", result.args[0].tokens[0])

    def test_nested_tag_in_text(self):
        result = WikiParser(
            "Foo",
            """
            {{Infobox foo bar baz 
            | foo {{mytag | arg | key = value }} bar
            }}
            """,
        ).get_infobox()

        self.assertIsNotNone(result)
        self.assertEqual("foo bar baz", result.extra.tokens[0])
        self.assertEqual("foo", result.args[0].tokens[0])
        self.assertEqual("mytag", result.args[0].tokens[1].tag)
        self.assertEqual("arg", result.args[0].tokens[1].args[0].tokens[0])
        self.assertEqual("value", result.args[0].tokens[1].kwargs["key"].tokens[0])
        self.assertEqual("bar", result.args[0].tokens[2])

    def test_nested_wiki_tag_in_infobox(self):
        result = WikiParser(
            "Foo",
            """
            {{Infobox foo bar baz 
            | stat = {{statistics | a = 1 | 2 | b= 3 }}
            }}
            """,
        ).get_infobox()

        self.assertIsNotNone(result)
        self.assertEqual("foo bar baz", result.extra.tokens[0])
        self.assertIsInstance(result.kwargs["stat"], WikiString)
        self.assertIsInstance(result.kwargs["stat"].tokens[0], WikiTag)
        self.assertEqual("statistics", result.kwargs["stat"].tokens[0].tag)
        self.assertEqual("1", result.kwargs["stat"].tokens[0].kwargs["a"].tokens[0])
        self.assertEqual("3", result.kwargs["stat"].tokens[0].kwargs["b"].tokens[0])
        self.assertEqual("2", result.kwargs["stat"].tokens[0].args[0].tokens[0])

    def test_cipher_simplified_infobox(self):
        result = WikiParser(
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
        ).get_infobox()
        self.assertIsNotNone(result)
        self.assertEqual("keyword", result.extra.tokens[0])
        self.assertEqual("Cipher", result.kwargs["name"].tokens[0])
        self.assertEqual("Spell", result.kwargs["type"].tokens[0])
        self.assertEqual("Static", result.kwargs["type2"].tokens[0])
        self.assertEqual("Gatecrash", result.kwargs["first"].tokens[0])
        self.assertEqual("Thunder Junction Commander", result.kwargs["last"].tokens[0])
        self.assertEqual(
            "Then you may exile this spell card encoded on a creature you control. Whenever that creature deals combat damage to a player, its controller may cast a copy of this card without paying its mana cost.",
            result.kwargs["reminder"].tokens[0],
        )
        self.assertEqual("9", result.kwargs["storm"].tokens[0])

    def test_cipher_oneline_infobox(self):
        result = WikiParser(
            "Cipher",
            """
            {{Infobox keyword | name = Cipher | type = Spell | type2 = Static | storm = 9
            }}
            """,
        ).get_infobox()
        self.assertIsNotNone(result)
        self.assertEqual("keyword", result.extra.tokens[0])
        self.assertEqual("Cipher", result.kwargs["name"].tokens[0])
        self.assertEqual("Spell", result.kwargs["type"].tokens[0])
        self.assertEqual("Static", result.kwargs["type2"].tokens[0])
        self.assertEqual("9", result.kwargs["storm"].tokens[0])

    def test_cipher_within_others_infobox(self):
        result = WikiParser(
            "Cipher",
            """
            some text before
            
            {{Infobox keyword | name = Cipher | type = Spell | type2 = Static | storm = 9
            }}
            
            some text after
            """,
        ).get_infobox()
        self.assertIsNotNone(result)
        self.assertEqual("keyword", result.extra.tokens[0])
        self.assertEqual("Cipher", result.kwargs["name"].tokens[0])
        self.assertEqual("Spell", result.kwargs["type"].tokens[0])
        self.assertEqual("Static", result.kwargs["type2"].tokens[0])
        self.assertEqual("9", result.kwargs["storm"].tokens[0])

    def test_emerge_wikiblock_with_trailing_pipe(self):
        result = WikiParser(
            "Emerge",
            """
            {{Infobox keyword
            | type = Static
            | first = Eldritch Moon
            | last = Modern Horizons 3
            | cost = yes
            | reminder = You may cast this spell by sacrificing a creature and paying the emerge cost reduced by that creature's mana value.
            | storm = 6
            | storm_ref=&lt;ref&gt;{{EzTumblr|https://markrosewater.tumblr.com/post/703821607899152384|title=I was wondering where Emerge is on the Storm scale?|2022-12-16}}&lt;/ref&gt;
            | stats = {{stats|W=1|U=1|C=10|}} By Emerge cost: {{stats|W=1|U=5|B=2|G=3|GU=1}}
            }}
            """,
        ).get_infobox()

        self.assertIsNotNone(result)
        self.assertEqual("keyword", result.extra.tokens[0])
        self.assertEqual("Static", result.kwargs["type"].tokens[0])
        self.assertEqual("6", result.kwargs["storm"].tokens[0])
        self.assertIsInstance(result.kwargs["stats"], WikiString)
        self.assertIsInstance(result.kwargs["stats"].tokens[0], WikiTag)
        self.assertIsInstance(result.kwargs["stats"].tokens[1], str)
        self.assertIsInstance(result.kwargs["stats"].tokens[2], WikiTag)

    def test_gr_plus_g_glossary(self):
        result = WikiParser(
            "Deathtouch",
            """
            foo
            
            {{CR+G}}
            
            bar
            """,
        ).get_glossaries()
        self.assertIsNotNone(result)
        self.assertEqual(["Deathtouch"], list(result))

    def test_gr_plus_g_defined_glossary(self):
        result = WikiParser(
            "Hidden Agenda",
            """
            foo
            
            {{CR+G|Hidden Agenda}}
            {{CR|glossary|Double Agenda}}
            
            bar
            """,
        ).get_glossaries()
        self.assertEqual(["Hidden Agenda", "Double Agenda"], list(result))

    def test_multiple_glossary(self):
        result = WikiParser(
            "Fuse",
            """
            foo
            
            {{CR+G}}
            {{CR|glossary|Fused Split Spell}}
            
            bar
            """,
        ).get_glossaries()
        self.assertIsNotNone(result)
        self.assertEqual(
            [
                "Fuse",
                "Fused Split Spell",
            ],
            list(result),
        )

    def test_mono_rule(self):
        result = WikiParser(
            "Kicker",
            """
            foo
            
            {{CR | 702.33h}}
            
            bar
            """,
        ).get_rules()
        self.assertIsNotNone(result)
        self.assertEqual(["702.33h"], list(result))

    def test_multi_rule(self):
        result = WikiParser(
            "Kicker",
            """
            foo
            
            {{CR|103.2b}}
            {{CR|116.2g}}
            
            bar
            """,
        ).get_rules()
        self.assertIsNotNone(result)
        self.assertEqual(["103.2b", "116.2g"], list(result))

    def test_get_wiki_tag_ref_content(self):
        result = list(
            WikiParser(
                "foo",
                """
            <ref>{{ DailyRef  | making-magic/storm-scale-ravnica-and-return-ravnica-2016-05-02|Storm Scale: Ravnica and Return to Ravnica|[[Mark Rosewater]]|May 2, 2016}}</ref>
            {{NOT_DAILYREF|foo}}
            """,
            ).get_wiki_tags("DailyRef")
        )

        self.assertIsNotNone(result)
        self.assertEqual(1, len(result))
        self.assertIsInstance(result[0], WikiTag)
        self.assertEqual("DailyRef", result[0].tag)
        self.assertEqual(
            "making-magic/storm-scale-ravnica-and-return-ravnica-2016-05-02",
            result[0].args[0].tokens[0],
        )
        self.assertEqual(
            "Storm Scale: Ravnica and Return to Ravnica", result[0].args[1].tokens[0]
        )
        self.assertEqual("[[Mark Rosewater]]", result[0].args[2].tokens[0])
        self.assertEqual("May 2, 2016", result[0].args[3].tokens[0])
        self.assertEqual({}, result[0].kwargs)

    def test_get_wiki_tag_list_of_args(self):
        result = list(
            WikiParser(
                "foo",
                """
            {{CR|103.2b}}
            {{CR|116.2g}}
            {{NOT_CR|foo}}
            """,
            ).get_wiki_tags(["CR"])
        )

        self.assertIsNotNone(result)
        self.assertEqual(2, len(result))
        self.assertIsInstance(result[0], WikiTag)
        self.assertEqual("CR", result[0].tag)
        self.assertEqual("103.2b", result[0].args[0].tokens[0])
        self.assertEqual({}, result[0].kwargs)
        self.assertIsInstance(result[1], WikiTag)
        self.assertEqual("CR", result[1].tag)
        self.assertEqual("116.2g", result[1].args[0].tokens[0])
        self.assertEqual({}, result[1].kwargs)

    def test_get_wiki_tag_named_fields(self):
        result = list(
            WikiParser(
                "foo",
                """
            {{FOO|a=1|b=2}}
            {{FOO|x=12|y=12}}
            {{NOT_FOO|foo}}
            """,
            ).get_wiki_tags(["FOO"])
        )

        self.assertIsNotNone(result)
        self.assertEqual(2, len(result))
        self.assertIsInstance(result[0], WikiTag)
        self.assertEqual("FOO", result[0].tag)
        self.assertEqual([], result[0].args)
        self.assertEqual(
            "1",
            result[0].kwargs["a"].tokens[0],
        )
        self.assertEqual(
            "2",
            result[0].kwargs["b"].tokens[0],
        )
        self.assertIsInstance(result[1], WikiTag)
        self.assertEqual("FOO", result[1].tag)
        self.assertEqual([], result[1].args)
        self.assertEqual(
            "12",
            result[1].kwargs["x"].tokens[0],
        )
        self.assertEqual(
            "12",
            result[1].kwargs["y"].tokens[0],
        )

    def test_get_nested_directly(self):
        result = list(
            WikiParser(
                "foo",
                """
            {{FOO #1|a=1|b=2}}
            {{bar | string with {{FOO #2|x=12|y=12}} inside }}
            {{bar | foo = {{FOO #3|c=3|d=4}} }}
            {{NOT_FOO|foo}}
            """,
            ).get_wiki_tags(["FOO"], recurse=True)
        )

        self.assertIsNotNone(result)
        self.assertEqual("#1", result[0].extra.tokens[0])
        self.assertEqual("#2", result[1].extra.tokens[0])
        self.assertEqual("#3", result[2].extra.tokens[0])
        self.assertEqual(3, len(result))

    def test_affinity_get_stats(self):
        result = list(
            WikiParser(
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
            | storm_ref = &lt;ref&gt;{{EzTumblr|http://markrosewater.tumblr.com/post/707260642788327424/|title=Hi Mark! I saw that there's an affinity...|2023-01-23}}&lt;/ref&gt;
            }}
            """,
            ).get_stats()
        )

        self.assertEqual(result[0].args[0].tokens[0], "Affinity for artifacts")
        self.assertEqual(result[4].args[0].tokens[0], "Affinity for Mountains")
        self.assertEqual(result[8].args[0].tokens[0], "Affinity for Food")
        self.assertEqual(
            result[12].args[0].tokens[0], "Affinity for historic permanents"
        )
        self.assertEqual(15, len(result))

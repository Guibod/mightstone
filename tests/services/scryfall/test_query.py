import re

import pytest
from assertpy import assert_that

from mightstone.services.scryfall.query import (
    BinOp,
    ComparatorEnum,
    KeywordEnum,
    OperatorEnum,
    Query,
    Term,
    UnOp,
)


class TestParser:
    @pytest.mark.parametrize(
        "test_input",
        [
            "c:rg",
            "color<=uw -c:red",
            "id>=esper t:instant",
            "id:c t:land",
            "t:merfolk t:legend",
            "t:goblin -t:creature",
            "o:draw t:creature",
            'o:"~ enters the battlefield tapped"',
            "mana:{G}{U}",
            "m:2WW",
            "m<3WU",
            "m:{R/P}",
            "c:u mv=5",
            "devotion:{u/b}{u/b}{u/b}",
            "produces=wu",
            "pow<=8",
            "pow<tou c:w t:creature",
            "t:planeswalker loy=3",
            "is:meld",
            "is:split",
            "c<=br is:spell f:duel",
            "is:permanent t:rebel",
            "is:vanilla",
            "is:funny",
            "t:scheme",
            "power include:extras",
            "r:common t:artifact",
            "r<=r",
            "rarity:common e:ima new:rarity",
            "in:rare -rarity:rare",
            "e:war",
            "e:war is:booster",
            "b:wwk",
            "in:lea in:m15",
            "t:legendary -in:booster",
            "is:datestamped is:prerelease",
            "cube:vintage",
            "cube:modern t:planeswalker",
            "c:g t:creature f:pauper",
            "banned:legacy",
            "is:commander",
            "is:reserved",
            "tix<15.00",
            "usd<=0.50 e:ema",
            'a:"proce"',
            "ft:mishra",
            "ft:designed e:m15",
            "wm:orzhov",
            "e:m10 new:art is:reprint",
            "new:art -new:artist st:masters game:paper",
            "new:flavor e:m15 is:reprint",
            "border:white t:creature",
            "is:new r:mythic",
            "is:old t:artifact",
            "is:hires",
            "is:foil e:c16",
            "frame:2003 new:frame in:fut is:reprint",
            "game:arena",
            "-in:mtgo f:legacy",
            "is:promo",
            "is:spotlight",
            "year>=1994",
            "year=2024",
            "date<=2015-08-18",
            "date<ori",
            "art:squirrel",
            "function:removal",
            "e:c16 not:reprint",
            "e:ktk is:unique",
            "sets<=20",
            "e:arn papersets=1",
            "lang:japanese",
            "lang:any t:planeswalker unique:prints",
            "lang:ko new:language t:goblin",
            "in:ru in:zhs",
            "is:dual",
            "is:fetchland",
            "is:colorshifted",
            "-fire c:r t:instant",
            "o:changeling -t:creature",
            "not:reprint e:c16",
            "t:creature o:/^{T}:/",
            "t:instant o:/\\spp/",
            "name:/\\bizzet\\b/",
            "!fire",
            '!"sift through sands"',
            "t:fish or t:bird",
            "t:land (a:titus or a:avon)",
            "t:legendary (t:goblin or t:elf)",
            "through (depths or sands or mists)",
            '!"Lightning Bolt" unique:prints',
            "t:forest a:avon unique:art",
            "f:modern order:rarity direction:asc",
            "t:human display:text",
            "in:leb game:paper prefer:newest",
        ],
    )
    def test_parse_scryfall_examples_raises_no_exception(self, test_input):
        query = Query(test_input)
        assert_that(query).is_instance_of(Query)


class TestQueryBuilder:
    def test_complete(self):
        q = Query("(rarity:common e:ima new:rarity) AND (emra OR kozi OR ulam)")

        assert_that(q).is_instance_of(Query)

        assert isinstance(q.root, BinOp)
        assert_that(q.root.operator).is_equal_to(OperatorEnum.AND)
        assert_that(q.root.operands).is_length(2)

        assert isinstance(q[0], BinOp)
        assert_that(q[0]).is_length(3)

        assert isinstance(q[0][0], Term)
        assert_that(q[0][0].comparator, ComparatorEnum.COLON)
        assert_that(q[0][0].value, "common")
        assert_that(q[0][0].keyword, KeywordEnum.RARITY)

        assert isinstance(q[0][1], Term)
        assert_that(q[0][1].comparator, ComparatorEnum.COLON)
        assert_that(q[0][1].value, "ima")
        assert_that(q[0][1].keyword, KeywordEnum.SET)

        assert isinstance(q[0][2], Term)
        assert_that(q[0][2].comparator, ComparatorEnum.COLON)
        assert_that(q[0][2].value, "rarity")
        assert_that(q[0][2].keyword, KeywordEnum.NEW)

        assert isinstance(q[1], BinOp)
        assert_that(q[1]).is_length(3)

        assert isinstance(q[1][0], Term)
        assert_that(q[1][0].comparator, ComparatorEnum.COLON)
        assert_that(q[1][0].value, "emra")
        assert_that(q[1][0].keyword, KeywordEnum.NAME)

        assert isinstance(q[1][1], Term)
        assert_that(q[1][1].comparator, ComparatorEnum.COLON)
        assert_that(q[1][1].value, "kozi")
        assert_that(q[1][1].keyword, KeywordEnum.NAME)

        assert isinstance(q[1][2], Term)
        assert_that(q[1][2].comparator, ComparatorEnum.COLON)
        assert_that(q[1][2].value, "ulam")
        assert_that(q[1][2].keyword, KeywordEnum.NAME)

    def test_regex(self):
        q = Query("name:/rat.*k/")
        assert isinstance(q, Query)

        assert_that(q.root).is_instance_of(Term)
        assert_that(q[0].comparator, ComparatorEnum.COLON)
        assert isinstance(q[0].value, re.Pattern)
        assert_that(q[0].value.pattern).is_equal_to(r"rat.*k")
        assert_that(q[0].keyword, KeywordEnum.NAME)

    def test_exact(self):
        q = Query("!fire")

        assert_that(q).is_instance_of(Query)

        assert isinstance(q.root, Term)
        assert_that(q[0].comparator, ComparatorEnum.EXACT)
        assert_that(q[0].value, "fire")
        assert_that(q[0].keyword, KeywordEnum.NAME)

    def test_exact_explicit_or(self):
        q = Query("!fire or !thud")

        assert_that(q).is_instance_of(Query)

        assert isinstance(q.root, BinOp)
        assert_that(q.root.operator).is_equal_to(OperatorEnum.OR)
        assert_that(q.root.operands).is_length(2)

        assert_that(q.root[0]).is_instance_of(Term)
        assert_that(q.root[0].comparator, ComparatorEnum.EXACT)
        assert_that(q.root[0].value, "fire")
        assert_that(q.root[0].keyword, KeywordEnum.NAME)

        assert_that(q.root[1]).is_instance_of(Term)
        assert_that(q.root[1].comparator, ComparatorEnum.EXACT)
        assert_that(q.root[1].value, "thud")
        assert_that(q.root[1].keyword, KeywordEnum.NAME)

    def test_nested_nor(self):
        q = Query("NOT (!fire or !thud)")

        assert_that(q).is_instance_of(Query)
        assert_that(q.root).is_length(1)

        assert isinstance(q.root, UnOp)
        assert_that(q.root.operator).is_equal_to(OperatorEnum.NOT)
        assert_that(q.root.operands).is_length(1)

        assert isinstance(q[0], BinOp)
        assert_that(q[0].operator).is_equal_to(OperatorEnum.OR)
        assert_that(q[0]).is_length(2)

        assert_that(q[0][0]).is_instance_of(Term)
        assert_that(q[0][0].comparator).is_equal_to(ComparatorEnum.EXACT)
        assert_that(q[0][0].value).is_equal_to("fire")
        assert_that(q[0][0].keyword).is_equal_to(KeywordEnum.NAME)

        assert_that(q[0][1]).is_instance_of(Term)
        assert_that(q[0][1].comparator).is_equal_to(ComparatorEnum.EXACT)
        assert_that(q[0][1].value).is_equal_to("thud")
        assert_that(q[0][1].keyword).is_equal_to(KeywordEnum.NAME)


@pytest.fixture
def fxt_simple():
    return "emrakul"


@pytest.fixture
def fxt_or_double():
    return "emrakul or kozilek"


class TestComposition:
    @pytest.mark.parametrize(
        "a,long,short",
        [
            ("emrakul", "NOT name:emrakul", "-emrakul"),
            (
                "emrakul or kozilek",
                "NOT (name:emrakul OR name:kozilek)",
                "NOT (emrakul OR kozilek)",
            ),
        ],
    )
    def test_invert(self, a: str, long: str, short: str):
        q = ~Query(a)
        assert isinstance(q, Query)
        assert_that(q.to_string(False), "long version").is_equal_to(long)
        assert_that(q.to_string(True), "short version").is_equal_to(short)

    @pytest.mark.parametrize(
        "a,b,long,short",
        [
            (
                "emrakul",
                "kozilek",
                "name:emrakul OR name:kozilek",
                "emrakul OR kozilek",
            ),
            (
                "emrakul and ulamog",
                "kozilek",
                "(name:emrakul AND name:ulamog) OR name:kozilek",
                "(emrakul ulamog) OR kozilek",
            ),
            (
                "kozilek",
                "emrakul and ulamog",
                "name:kozilek OR (name:emrakul AND name:ulamog)",
                "kozilek OR (emrakul ulamog)",
            ),
            (
                "kozilek and squee",
                "emrakul and ulamog",
                "(name:kozilek AND name:squee) OR (name:emrakul AND name:ulamog)",
                "(kozilek squee) OR (emrakul ulamog)",
            ),
        ],
    )
    def test_or(self, a: str, b: str, long: str, short: str):
        q = Query(a) | Query(b)
        assert isinstance(q, Query)
        assert_that(q.to_string(False), "long version").is_equal_to(long)
        assert_that(q.to_string(True), "short version").is_equal_to(short)

    @pytest.mark.parametrize(
        "a,b,long,short",
        [
            (
                "emrakul",
                "kozilek",
                "name:emrakul AND name:kozilek",
                "emrakul kozilek",
            ),
            (
                "emrakul OR ulamog",
                "kozilek",
                "(name:emrakul OR name:ulamog) AND name:kozilek",
                "(emrakul OR ulamog) kozilek",
            ),
            (
                "emrakul AND ulamog",
                "kozilek",
                "name:emrakul AND name:ulamog AND name:kozilek",
                "emrakul ulamog kozilek",
            ),
            (
                "emrakul AND ulamog",
                "kozilek OR squee",
                "(name:emrakul AND name:ulamog) AND (name:kozilek OR name:squee)",
                "(emrakul ulamog) (kozilek OR squee)",
            ),
        ],
    )
    def test_and(self, a: str, b: str, long: str, short: str):
        q = Query(a) & Query(b)
        assert isinstance(q, Query)
        assert_that(q.to_string(False), "long version").is_equal_to(long)
        assert_that(q.to_string(True), "short version").is_equal_to(short)

    @pytest.mark.parametrize(
        "a,b,long,short",
        [
            (
                "emrakul",
                "kozilek",
                "name:emrakul AND name:kozilek",
                "emrakul kozilek",
            ),
            (
                "emrakul OR ulamog",
                "kozilek",
                "name:emrakul OR name:ulamog OR name:kozilek",
                "emrakul OR ulamog OR kozilek",
            ),
            (
                "emrakul AND ulamog",
                "kozilek",
                "name:emrakul AND name:ulamog AND name:kozilek",
                "emrakul ulamog kozilek",
            ),
            (
                "emrakul AND ulamog",
                "kozilek OR squee ",
                "name:emrakul AND name:ulamog AND (name:kozilek OR name:squee)",
                "emrakul ulamog (kozilek OR squee)",
            ),
            (
                "emrakul AND ulamog",
                "NOT kozilek",
                "name:emrakul AND name:ulamog AND NOT name:kozilek",
                "emrakul ulamog -kozilek",
            ),
        ],
    )
    def test_concat(self, a: str, b: str, long: str, short: str):
        q = Query(a) + Query(b)
        assert isinstance(q, Query)
        assert_that(q.to_string(False), "long version").is_equal_to(long)
        assert_that(q.to_string(True), "short version").is_equal_to(short)

    @pytest.mark.parametrize(
        "a,b,long,short",
        [
            (
                "emrakul",
                "kozilek",
                "name:emrakul AND NOT name:kozilek",
                "emrakul -kozilek",
            ),
            (
                "emrakul",
                "NOT kozilek",
                "name:emrakul AND name:kozilek",
                "emrakul kozilek",
            ),
            (
                "emrakul squee",
                "NOT kozilek",
                "(name:emrakul AND name:squee) AND name:kozilek",
                "(emrakul squee) kozilek",
            ),
        ],
    )
    def test_minus(self, a: str, b: str, long: str, short: str):
        q = Query(a) - Query(b)
        assert isinstance(q, Query)
        assert_that(q.to_string(False), "long version").is_equal_to(long)
        assert_that(q.to_string(True), "short version").is_equal_to(short)

    @pytest.mark.parametrize(
        "a,b,long,short",
        [
            (
                "emrakul",
                "kozilek",
                "(name:emrakul OR name:kozilek) AND NOT (name:emrakul AND name:kozilek)",
                "(emrakul OR kozilek) AND NOT (emrakul kozilek)",
            ),
        ],
    )
    def test_xor(self, a: str, b: str, long: str, short: str):
        q = Query(a) ^ Query(b)
        assert isinstance(q, Query)
        assert_that(q.to_string(False), "long version").is_equal_to(long)
        assert_that(q.to_string(True), "short version").is_equal_to(short)

    def test_build(self):
        q = (
            (Query("id:rakdos") | Query("id>jund")) & Query("t:instant or t:sorcery")
        ) + Query("cmc<10")
        assert isinstance(q, Query)
        assert_that(q.to_string(False), "long version").is_equal_to(
            "(identity:rakdos OR identity>jund) AND (type:instant OR type:sorcery) AND manavalue<10"
        )
        assert_that(q.to_string(True), "short version").is_equal_to(
            "(id:rakdos OR id>jund) (t:instant OR t:sorcery) mv<10"
        )

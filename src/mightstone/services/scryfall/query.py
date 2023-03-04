import re
import shlex
import string
from enum import Enum
from typing import List, Union, Optional, Mapping, Iterator, Literal

from pydantic.types import constr

from mightstone.core import MightstoneModel

class NewEnum(Enum):
    RARITY: ""
    ART: ""
    ARTIST: ""
    FLAVOR: ""
    FRAME: ""
    LANGUAGE: ""

class Is(Enum):
    INDICATOR: "color indicators"
    HYBRID: "the cards have hybrid mana"
    PHYREXIAN: "the cards have Phyrexian mana"
    SPLIT: "split card"
    FLIP: "flip card"
    TRANSFORM: "cards that transform"
    MELD: "cards that meld"
    LEVELER: "cards with level ups"
    DFC: "double faced cards"
    MDFC: "modal double faced cards"
    SPELL: "modal double faced cards"
    PERMANENT: "modal double faced cards"
    HISTORIC: "modal double faced cards"
    PARTY: "modal double faced cards"
    VANILLA: "modal double faced cards"
    FRENCHVANILLA: "modal double faced cards"
    BEAR: "modal double faced cards"
    FUNNY: "Un-cards, holiday cards, and other funny cards"
    BOOSTER: ""
    PLANESWALKER_DECK: ""
    LEAGUE: ""
    BUYABOX: ""
    GIFTBOX: ""
    INTRO_PACK: ""
    GAMEDAY: ""
    PRERELEASE: ""
    RELEASE: ""
    FNM: ""
    JUDGE_GIFT: ""
    ARENA_LEAGUE: ""
    PLAYER_REWARDS: ""
    MEDIA_INSERT: ""
    INSTORE: ""
    CONVENTION: ""
    SET_PROMO: ""
    DATESTAMPED: ""
    COMMANDER: ""
    RESERVED: ""
    BRAWLER: ""
    COMPANION: ""
    DUELCOMMANDER: ""
    WATERMARK: ""
    FULL: ""
    NONFOIL: ""
    FOIL: ""
    ETCHED: ""
    GLOSSY: ""
    HIRES: ""
    DIGITAL: ""
    PROMO: ""
    SPOTLIGHT: ""
    SCRYFALLPREVIEW: ""
    REPRINT: ""
    UNIQUE: ""
    BIKELAND: ""
    CYCLELAND: ""
    BICYCLELAND: ""
    BOUNCELAND: ""
    KAROO: ""
    CANOPYLAND: ""
    CANLAND: ""
    CHECKLAND: ""
    DUAL: ""
    FASTLAND: ""
    FETCHLAND: ""
    FILTERLAND: ""
    GAINLAND: ""
    PAINLAND: ""
    SCRYLAND: ""
    SHADOWLAND: ""
    SHOCKLAND: ""
    STORAGELAND: ""
    CREATURELAND: ""
    TRILAND: ""
    TANGOLAND: ""
    BATTLELAND: ""
    MASTERPIECE: ""

class Operators(str, Enum):
    EQUAL = "="
    GT = ">"
    GTE = ">="
    LT = "<"
    LTE = "<="
    NE = "!="

class Keyword(MightstoneModel):
    keywords: List[Union[str,None]] = constr(regex=r"^[^a-z]*$")
    description: Optional[str]

class RegexKeyword(Keyword):
    ...

class ComparableKeyword(Keyword):
    default_operator: Operators = Operators.EQUAL

class EnumKeyword(Keyword):
    enum: type[Enum]

# negate with -
# replace card name in oracle by ~
# force strict card name with !
# non comparable reacts with : and = separator
# include:extras
# not:X seems to be alias for -is:X

class Keywords(Mapping):
    def __init__(self, keywords: List[Keyword]):
        self.keywords = keywords

    def __len__(self) -> int:
        return len(self.keywords)

    def __iter__(self) -> Iterator[Keyword]:
        return iter(self.keywords)

    def __getitem__(self, k: str) -> Keyword:
        return next(x for x in self.keywords if k in x.keywords)



KEYWORDS = Keywords([
            RegexKeyword(keywords=[None, "name"], description="the card name"),
            ComparableKeyword(keywords=["c", "color"], default_operator=">=",
                              description="the colors"),
            ComparableKeyword(keywords=["id", "identity"], default_operator=">=",
                              description="the color identity"),
            RegexKeyword(keywords=["t", "type"], 
                         description="the color identity"),
            RegexKeyword(keywords=["o", "oracle"], description="the text"),
            Keyword(keywords=["fo", "fulloracle"], description="the full Oracle text"),
            Keyword(keywords=["keyword"], description="the card has the keyword"),
            ComparableKeyword(keywords=["m", "mana"], default_operator=">=",
                              description="the mana cost"),
            ComparableKeyword(keywords=["mv", "manavalue"], 
                              description="the mana cost"),
            ComparableKeyword(keywords=["devotion"], default_operator=">=",
                              description="card's devotion"),
            ComparableKeyword(keywords=["produces"], default_operator=">=",
                              description="mana produced"),
            ComparableKeyword(keywords=["pow", "power"], 
                              description="the power"),
            ComparableKeyword(keywords=["tou", "toughness"], 
                              description="the toughness"),
            ComparableKeyword(keywords=["pt", "powtou"], 
                              description="the sum of power and toughness"),
            ComparableKeyword(keywords=["loy", "loyalty"], 
                              description="the loyalty"),
            Keyword(keywords=["include"],  description="the loyalty"),
            ComparableKeyword(keywords=["r", "rarity"], 
                              description="the rarity"),
            EnumKeyword(keywords=["new"], 
                        description="the cards were printed at a new", enum=NewEnum),
            ComparableKeyword(keywords=["in"], 
                              description="the cards was in "),
            Keyword(keywords=["e", "s", "set", "edition"], description="the set"),
            Keyword(keywords=["cn", "number"], description="the collector number"),
            ComparableKeyword(keywords=["cn", "number"], 
                              description="the collector number"),
            Keyword(keywords=["b", "block"], description="the block"),
            Keyword(keywords=["st", "settype"], description="the set type"),
            Keyword(keywords=["cube"], description="the card is in the %s deck/cube"),
            Keyword(keywords=["f", "format"], description="it’s legal in %s"),
            Keyword(keywords=["banned"], description="it’s banned in %s"),
            Keyword(keywords=["restricted"], description="it’s restricted in %s"),
            ComparableKeyword(keywords=["usd"],  description="the USD price"),
            ComparableKeyword(keywords=["eur"],  description="the EUR price"),
            ComparableKeyword(keywords=["tix"],  description="the TIX price"),
            Keyword(keywords=["cheapeast"],
                    description="the card has the lowest %s price"),
            Keyword(keywords=["a", "artist"], description="the artist name"),
            ComparableKeyword(keywords=["artists"], 
                              description="the number of artists"),
            RegexKeyword(keywords=["ft", "flavor"], description="the flavor text"),
            ComparableKeyword(keywords=["illustrations"],
                              description="the number of distinct illustrations"),
            Keyword(keywords=["border"], description="the border color is %s"),
            Keyword(keywords=["frame"],
                    description="the cards have the %s frame effect"),
            Keyword(keywords=["stamp"],
                    description="the cards have the %s security stamp"),
            Keyword(keywords=["game"], description="the card is available on %s"),
            ComparableKeyword(keywords=["year"], description="the release year"),
            ComparableKeyword(keywords=["date"], description="the date"),
            Keyword(keywords=["art", "atag", "arttag"],
                    description="the illustration contains %s"),
            Keyword(keywords=["otag", "oracletag", "function"],
                    description="the card is tagged %s"),
            ComparableKeyword(keywords=["sets"],
                              description="the number of times a card has appeared in a set"),
            ComparableKeyword(keywords=["papersets"],
                              description="the number of paper sets"),
            ComparableKeyword(keywords=["prints"], description="the number of prints"),
            ComparableKeyword(keywords=["paperprints"],
                              description="the number of paper prints"),
            Keyword(keywords=["lang", "language"], description="the language is %s"),
            Keyword(keywords=["unique"], description=""),
            Keyword(keywords=["display"], description=""),
            Keyword(keywords=["order"], description=""),
            Keyword(keywords=["prefer"], description=""),
            Keyword(keywords=["direction"], description=""),
            EnumKeyword(keywords=["is", "has"], description="the cards have...",
                        enum=Is)
        ])

#
# class BooleanProperty(str, Enum):
#     """
#     To be used with Keywords.IS
#     """
#     # Mana Cost
#     HYBRID = "hybrid"
#     """Hybrid mana symbol"""
#     PHYREXIAN = "phyrexian"
#     """Phyrexian mana symbol"""
#
#     # Multi - faced Cards
#     SPLIT = "split"
#     """split cards"""
#     FLIP = "flip"
#     """flip cards"""
#     MELD = "meld"
#     """cards that meld"""
#     LEVELER = "leveler"
#     """cards with level-up"""
#     DFC = "dfc"
#     """double-faced cards"""
#     MDFC = "mdfc"
#     """modal double-faced cards"""
#
#     # Spell, permanents, effects
#     SPELL = "spell"
#     """Cards that are cast as spells"""
#     PERMANENT = "permanent"
#     """Cards that are permanents"""
#     HISTORIC = "historic"
#     """Cards that are historic"""
#     PARTY = "party"
#     """Creatures that can be in your party"""
#     MODAL = "modal"
#     """Cards with modal effect"""
#     VANILLA = "vanilla"
#     """Vanilla cards (no-oracle)"""
#     FRENCH_VANILLA = "frenchvanilla"
#     """French Vanilla cards (only keywords abilities)"""
#     BEAR = "bear"
#     """Bear cards (MV=2, POW=2, TOU=2)"""
#
#     # Extra / Funny cards
#     FUNNY = "funny"
#     """Un-cards, holiday cards, and other funny cards"""
#
#
# class Includes(str, Enum):
#     EXTRAS = "extras"
#
#
# class Keywords(str, Enum):
#     HAS = "has"
#     IS = "is"
#
#     COLOR = "color"
#     IDENTITY = "identity"
#     TYPE = "type"
#     ORACLE = "oracle"
#     KEYWORD = "keyword"
#     MANA = "mana"
#     MANA_VALUE = "manavalue"
#     DEVOTION = "devotion"
#     PRODUCES = "produces"
#     POWER = "power"
#     TOUGHNESS = "toughness"
#     POWER_TOUGHNESS = "powtou"
#     LOYALTY = "loyalty"
#     INCLUDE = "include"
#     RARITY = "rarity" # (common, uncommon, rare, ‘special’, mythic, and ‘bonus’.)
#     NEW = "new" # (rarity, art, artist, flavor, frame, language,
#     IN = "in" # (rare, common, ... / {set} / paper, mtgo, arena / en, fr, ru ...
#     SET = "set" # (synonym of e, edition, s)
#     NUMBER = "number" # Synonym of cn
#     BLOCK = "block" # Synonym of b
#
#
# class KeywordsShorthand(Keywords):
#     COLOR = "c"
#     IDENTITY = "id"
#     TYPE = "t"
#     ORACLE = "o"
#     FULL_ORACLE = "fo"
#     MANA = "m"
#     MANA_VALUE = "mv"
#     POWER = "pow"
#     TOUGHNESS = "tou"
#     POWER_TOUGHNESS = "pt"
#     LOYALTY = "loy"
#     RARITY = "r"
#
#
#
# class Tags(str, Enum):
#     INDICATOR = "indicator"
#


class Term:
    def __init__(self, keyword: Keyword, term: str):
        self.keyword = keyword
        self.term = term

    def explain(self):
        self.k


class And(list):
    ...


class Or(list):
    ...


def tokenize(string) -> List[str]:
    return shlex.split(string)


class And():
    pass

import pyparsing
from pyparsing import Word, Forward, Group, OneOrMore, ZeroOrMore, Suppress, oneOf, Combine, alphanums
import string


def tokenize(fu) -> List[str]:
    RawWord = Word(re.sub(r'[()" ]', '', string.printable))
    Exactly = Word("!")
    Negate = Word("-")
    Token = Forward()
    Token << (RawWord |
              Group('"' + OneOrMore(RawWord) + '"') |
              Group('(' + OneOrMore(Token) + ')'))
    Phrase = ZeroOrMore(Token)

    return Phrase.parse_string(fu, parseAll=True).as_list()


class SearchQueryParser:
    def __init__(self):
        self._methods = {
            "and": self.evaluateAnd,
            "or": self.evaluateOr,
            "not": self.evaluateNot,
            "parenthesis": self.evaluateParenthesis,
            "quotes": self.evaluateQuotes,
            "word": self.evaluateWord,
            "wordwildcard": self.evaluateWordWildcard,
        }
        self._parser = self.parser()

    def parser(self):
        """
        This function returns a parser.
        The grammar should be like most full text search engines (Google, Tsearch, Lucene).
        Grammar:
        - a query consists of alphanumeric words, with an optional '*' wildcard
          at the end of a word
        - a sequence of words between quotes is a literal string
        - words can be used together by using operators ('and' or 'or')
        - words with operators can be grouped with parenthesis
        - a word or group of words can be preceded by a 'not' operator
        - the 'and' operator precedes an 'or' operator
        - if an operator is missing, use an 'and' operator
        """
        operatorOr = Forward()

        operatorWord = Group(Combine(Word(alphanums) + Suppress("*"))).setResultsName(
            "wordwildcard"
        ) | Group(Word(alphanums)).setResultsName("word")

        operatorQuotesContent = Forward()
        operatorQuotesContent << ((operatorWord + operatorQuotesContent) | operatorWord)

        operatorQuotes = (
            Group(Suppress('"') + operatorQuotesContent + Suppress('"')).setResultsName(
                "quotes"
            )
            | operatorWord
        )

        operatorParenthesis = (
            Group(Suppress("(") + operatorOr + Suppress(")")).setResultsName(
                "parenthesis"
            )
            | operatorQuotes
        )

        operatorNot = Forward()
        operatorNot << (
            Group(Suppress(pyparsing.Keyword("not", caseless=True)) + operatorNot).setResultsName(
                "not"
            )
            | operatorParenthesis
        )

        operatorAnd = Forward()
        operatorAnd << (
            Group(
                operatorNot + Suppress(pyparsing.Keyword("and", caseless=True)) + operatorAnd
            ).setResultsName("and")
            | Group(
                operatorNot + OneOrMore(~oneOf("and or") + operatorAnd)
            ).setResultsName("and")
            | operatorNot
        )

        operatorOr << (
            Group(
                operatorAnd + Suppress(pyparsing.Keyword("or", caseless=True)) + operatorOr
            ).setResultsName("or")
            | operatorAnd
        )

        return operatorOr.parseString

    def evaluateAnd(self, argument):
        return self.evaluate(argument[0]).intersection(self.evaluate(argument[1]))

    def evaluateOr(self, argument):
        return self.evaluate(argument[0]).union(self.evaluate(argument[1]))

    def evaluateNot(self, argument):
        return self.GetNot(self.evaluate(argument[0]))

    def evaluateParenthesis(self, argument):
        return self.evaluate(argument[0])

    def evaluateQuotes(self, argument):
        """Evaluate quoted strings
        First is does an 'and' on the indidual search terms, then it asks the
        function GetQuoted to only return the subset of ID's that contain the
        literal string.
        """
        r = set()
        search_terms = []
        for item in argument:
            search_terms.append(item[0])
            if len(r) == 0:
                r = self.evaluate(item)
            else:
                r = r.intersection(self.evaluate(item))
        return self.GetQuotes(" ".join(search_terms), r)

    def evaluateWord(self, argument):
        return self.GetWord(argument[0])

    def evaluateWordWildcard(self, argument):
        return self.GetWordWildcard(argument[0])

    def evaluate(self, argument):
        return self._methods[argument.getName()](argument)

    def Parse(self, query):
        # print self._parser(query)[0]
        return self.evaluate(self._parser(query)[0])

    def GetWord(self, word):
        return set()

    def GetWordWildcard(self, word):
        return set()

    def GetQuotes(self, search_string, tmp_result):
        return set()

    def GetNot(self, not_set):
        return set().difference(not_set)

class Query(str):
    def parse(self) -> List[Term]:
        ...

    def simplify(self):
        return

    def explain(self):
        pass

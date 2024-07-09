import re
from copy import copy
from enum import Enum
from typing import Optional, Union

import pyparsing as pp

pp.ParserElement.enablePackrat()


class OperatorEnum(str, Enum):
    OR = "OR"
    AND = "AND"
    XOR = "XOR"
    NOT = "NOT"

    @staticmethod
    def factory(candidate: Optional[str]) -> Union["OperatorEnum", None]:
        if not candidate:
            return None

        return OperatorEnum(candidate)


class OpNode:
    operands: list["OpNode"]
    operator: OperatorEnum

    def __or__(self, other: "OpNode") -> "OpNode":
        if isinstance(self, BinOp):
            if len(other.operands) == 1 and len(self.operands) == 1:
                return BinOp([self.operands[0], other.operands[0]], OperatorEnum.OR)
            elif len(other.operands) == 1 and self.operator == OperatorEnum.OR:
                return self + other
            elif len(self.operands) == 1 and other.operator == OperatorEnum.OR:
                return BinOp([self.operands[0], *other.operands], OperatorEnum.OR)
        return BinOp([self, other], OperatorEnum.OR)

    def __and__(self, other: "OpNode") -> "OpNode":
        if isinstance(self, BinOp):
            if len(other.operands) == 1 and len(self.operands) == 1:
                return BinOp([self.operands[0], other.operands[0]], OperatorEnum.AND)
            elif len(other.operands) == 1 and self.operator == OperatorEnum.AND:
                return self + other
            elif len(self.operands) == 1 and other.operator == OperatorEnum.AND:
                return BinOp([self.operands[0], *other.operands], OperatorEnum.AND)
        return BinOp([self, other], OperatorEnum.AND)

    def __add__(self, other: "OpNode") -> "OpNode":
        if isinstance(self, Term):
            return BinOp([self]) + other
        out = copy(self)
        out.operands.append(other)
        return out

    def __sub__(self, other: "OpNode") -> "BinOp":
        if isinstance(other, UnOp):
            return BinOp([self, other.operands[0]], OperatorEnum.AND)
        return BinOp([self, UnOp([other])], OperatorEnum.AND)

    def __xor__(self, other: "OpNode") -> "BinOp":
        return BinOp([self, other], OperatorEnum.XOR)

    def __invert__(self):
        return UnOp([self])

    def __repr__(self):
        return "{}({}):{!r}".format(
            self.__class__.__name__, self.operator, self.operands
        )

    def __str__(self):
        return self.to_string()

    def __getitem__(self, item):
        return self.operands[item]

    def __len__(self):
        return len(self.operands)

    @staticmethod
    def wrap(wrapped: "OpNode", shorten=False) -> str:
        out = wrapped.to_string(shorten)
        if isinstance(wrapped, OpNode) and len(wrapped.operands) > 1:
            return f"({out})"
        return out

    def join(self, operator: OperatorEnum, items: list["OpNode"], shorten=False):
        if len(items) == 1:
            return str(items[0])

        wrapped_items = map(lambda x: self.wrap(x, shorten), items)
        if shorten and operator == OperatorEnum.AND:
            return " ".join(wrapped_items)
        return f" {operator.value} ".join(wrapped_items)

    def to_string(self, shorten=False):
        if self.operator == OperatorEnum.NOT:
            if (
                shorten
                and len(self.operands) == 1
                and isinstance(self.operands[0], Term)
            ):
                return f"-{self.operands[0].to_string(shorten)}"
            return f"NOT {self.wrap(self.operands[0], shorten)}"

        if len(self.operands) == 1:
            return self.operands[0].to_string(shorten)

        if self.operator == OperatorEnum.XOR:
            return f"({self.join(OperatorEnum.OR, self.operands, shorten)}) AND NOT ({self.join(OperatorEnum.AND, self.operands, shorten)})"

        return f"{self.join(self.operator, self.operands, shorten)}"


class UnOp(OpNode):
    def __init__(self, operands: list["OpNode"]):
        self.operator = OperatorEnum.NOT
        self.operands = operands

    @staticmethod
    def from_tokens(tokens):
        return UnOp([tokens[0][1]])


class BinOp(OpNode):
    def __init__(
        self, operands: list[OpNode], operator: OperatorEnum = OperatorEnum.AND
    ):
        self.operator = operator
        self.operands = operands

    @staticmethod
    def from_tokens(tokens):
        return BinOp(tokens[0][::2], OperatorEnum(tokens[0][1]))


class ComparatorEnum(str, Enum):
    COLON = ":"
    LT = "<"
    GT = ">"
    EQUAL = "="
    LTE = "<="
    GTE = ">="
    NEQUAL = "!="
    EXACT = "!"

    @staticmethod
    def factory(candidate: Optional[str]) -> "ComparatorEnum":
        if not candidate:
            return ComparatorEnum.COLON

        return ComparatorEnum(candidate)


class KeywordEnum(str, Enum):
    ILLUSTRATIONS = "illustrations"
    STAMP = "stamp"
    MANA_VALUE = "manavalue"
    ORDER = "order"
    DISPLAY = "display"
    DIRECTION = "direction"
    LANGUAGE = "lang"
    TAG_ORACLE = "otag"
    NOT = "not"
    FRAME = "frame"
    BORDER = "border"
    PRODUCT_TYPE = "st"
    GAME = "game"
    INCLUDE = "include"
    FORMAT = "format"
    BANNED = "banned"
    RESTRICTED = "restricted"
    IS = "is"
    BLOCK = "block"
    NUMBER = "number"
    ARTIST = "artist"
    ARTISTS = "artists"
    WATERMARK = "watermark"
    FLAVOR = "flavor"
    TYPE = "type"
    ORACLE = "oracle"
    YEAR = "year"
    DATE = "date"
    MANA = "mana"
    NAME = "name"
    NEW = "new"
    SETS = "sets"
    SET = "set"
    RARITY = "rarity"
    COLOR = "color"
    IDENTITY = "identity"
    POWER = "power"
    TOUGHNESS = "toughness"
    POWTOU = "powtou"
    LOYALTY = "loyalty"
    USD = "usd"
    EUR = "eur"
    TIX = "tix"
    DEVOTION = "devotion"
    PRODUCES = "produces"
    IN = "in"
    UNIQUE = "unique"
    CUBE = "cube"
    TAG_ART = "art"
    PREFER = "prefer"
    ...

    @staticmethod
    def factory(candidate: Optional[str]) -> "KeywordEnum":
        if not candidate:
            return KeywordEnum.NAME

        try:
            return KeywordEnum(candidate)
        except ValueError:
            ...

        for k, v in keyword_map.items():
            if candidate in v:
                return k

        raise ValueError(f"Unable to resolve keyword `{candidate}`")


can_use_comparison_expr = {
    KeywordEnum.IDENTITY,
    KeywordEnum.COLOR,
    KeywordEnum.MANA_VALUE,
    KeywordEnum.MANA,
    KeywordEnum.POWER,
    KeywordEnum.TOUGHNESS,
    KeywordEnum.POWTOU,
    KeywordEnum.USD,
    KeywordEnum.EUR,
    KeywordEnum.TIX,
    KeywordEnum.YEAR,
    KeywordEnum.DATE,
    KeywordEnum.RARITY,
    KeywordEnum.ARTISTS,
    KeywordEnum.ILLUSTRATIONS,
    KeywordEnum.SETS,
}
can_use_regex = {
    KeywordEnum.TYPE,
    KeywordEnum.ORACLE,
    KeywordEnum.FLAVOR,
    KeywordEnum.NAME,
}

keyword_map: dict[KeywordEnum, list[Optional[str]]] = {
    KeywordEnum.NAME: [None, "name"],
    KeywordEnum.ORACLE: ["o", "oracle"],
    KeywordEnum.TYPE: ["t", "type"],
    KeywordEnum.FLAVOR: ["ft", "flavor"],
    KeywordEnum.WATERMARK: ["wm", "watermark"],
    KeywordEnum.ARTIST: ["a", "artist"],
    KeywordEnum.NUMBER: ["cn", "number"],
    KeywordEnum.BLOCK: ["b", "block"],
    KeywordEnum.SET: ["s", "e", "set", "edition"],
    KeywordEnum.RARITY: ["r", "rarity"],
    KeywordEnum.COLOR: ["c", "color"],
    KeywordEnum.IDENTITY: ["id", "identity"],
    KeywordEnum.MANA: ["m", "mana"],
    KeywordEnum.MANA_VALUE: ["mv", "manavalue", "cmc"],
    KeywordEnum.POWER: ["pow", "power"],
    KeywordEnum.TOUGHNESS: ["tou", "toughness"],
    KeywordEnum.POWTOU: ["pt", "powtou"],
    KeywordEnum.LOYALTY: ["loy", "loyalty"],
    KeywordEnum.USD: ["usd"],
    KeywordEnum.EUR: ["eur"],
    KeywordEnum.TIX: ["tix"],
    KeywordEnum.YEAR: ["year"],
    KeywordEnum.DATE: ["date"],
    KeywordEnum.DEVOTION: ["devotion"],
    KeywordEnum.PRODUCES: ["produces"],
    KeywordEnum.IS: ["is"],
    KeywordEnum.NOT: ["not"],
    KeywordEnum.FORMAT: ["f", "format"],
    KeywordEnum.RESTRICTED: ["restricted"],
    KeywordEnum.BANNED: ["banned"],
    KeywordEnum.INCLUDE: ["include"],
    KeywordEnum.IN: ["in"],
    KeywordEnum.UNIQUE: ["unique"],
    KeywordEnum.CUBE: ["cube"],
    KeywordEnum.GAME: ["game"],
    KeywordEnum.PRODUCT_TYPE: ["st"],
    KeywordEnum.BORDER: ["border"],
    KeywordEnum.FRAME: ["frame"],
    KeywordEnum.TAG_ORACLE: ["otag", "oracletag", "function"],
    KeywordEnum.LANGUAGE: ["lang"],
    KeywordEnum.DIRECTION: ["direction"],
    KeywordEnum.DISPLAY: ["display"],
    KeywordEnum.ORDER: ["order"],
    KeywordEnum.TAG_ART: ["atag", "arttag", "art"],
    KeywordEnum.PREFER: ["prefer"],
    KeywordEnum.STAMP: ["stamp"],
    KeywordEnum.ARTISTS: ["artists"],
    KeywordEnum.ILLUSTRATIONS: ["illustrations"],
}


EXACT = pp.Literal("!")

COLON, LT, GT, EQUAL = map(pp.Literal, ":<>=")
LTE = pp.Literal("<=")
GTE = pp.Literal(">=")
NEQUAL = pp.Literal("!=")
LPAR, RPAR = map(pp.Suppress, "()")

AND = pp.CaselessKeyword("AND").set_parse_action(lambda t: OperatorEnum.factory(t[0]))
OR = pp.CaselessKeyword("OR").set_parse_action(lambda t: OperatorEnum.factory(t[0]))
NOT = (pp.CaselessKeyword("NOT") | pp.Literal("-")).set_parse_action(
    lambda t: OperatorEnum.NOT
)
KEYWORDS = AND | OR | NOT

EXPRESSION = pp.Forward()

COMPARATORS = COLON | LTE | GTE | LT | EQUAL | GT | NEQUAL

VALID_SYMBOL = pp.nested_expr("{", "}")
VALID_WORD = pp.Word(init_chars=pp.printables, exclude_chars="<>{}():", as_keyword=True)
STRING = pp.QuotedString('"')

PROHIBIT = pp.Literal("-")("prohibit")

TERM = pp.Optional(
    (
        VALID_WORD.copy().setResultsName("keyword")
        + COMPARATORS.setResultsName("comparator")
    )
    | EXACT.setResultsName("comparator")
) + (
    pp.QuotedString("/").set_parse_action(lambda t: re.compile(t[0]))
    | pp.OneOrMore(VALID_SYMBOL)
    | VALID_WORD
    | STRING
).setResultsName(
    "value"
)
TERM.setParseAction(lambda tokens: Term.from_tokens(tokens))

EXPRESSION << pp.infix_notation(
    TERM,
    [
        (NOT, 1, pp.opAssoc.RIGHT, UnOp.from_tokens),
        (OR, 2, pp.opAssoc.LEFT, BinOp.from_tokens),
        (pp.Optional(AND, OperatorEnum.AND), 2, pp.opAssoc.LEFT, BinOp.from_tokens),
    ],
)


class Term(OpNode):
    def __init__(
        self,
        value: Union[str, re.Pattern],
        keyword: KeywordEnum,
        comparator: ComparatorEnum,
    ):
        self.value = value
        self.comparator: ComparatorEnum = comparator
        self.keyword: KeywordEnum = keyword

        self.validate()

    def validate(self):
        if self.keyword != KeywordEnum.NAME and self.comparator == ComparatorEnum.EXACT:
            raise ValueError(
                f"`Invalid expression {self}. {self.keyword}` does not "
                f"accept exact expression (!expr)."
            )

        if isinstance(self.value, re.Pattern) and self.keyword not in can_use_regex:
            raise ValueError(
                f"`Invalid expression {self}. {self.keyword}` does not "
                f"accept regular expression."
            )

        if (
            self.comparator
            in (
                ComparatorEnum.GT,
                ComparatorEnum.GTE,
                ComparatorEnum.LT,
                ComparatorEnum.LTE,
                ComparatorEnum.NEQUAL,
            )
            and self.keyword not in can_use_comparison_expr
        ):
            raise ValueError(
                f"`Invalid expression {self}. {self.keyword}` does not accept "
                f"comparison operators (<, >, <=, >=, !=)."
            )

    @property
    def operands(self):
        return [self]

    @property
    def operator(self):
        return None

    def to_string(self, shorten=False):
        value = self.value
        if " " in value:
            value = f'"{value}"'

        if self.keyword:
            k = self.keyword.value
            c = self.comparator.value
            if (
                self.keyword not in can_use_comparison_expr
                and c == ComparatorEnum.EQUAL
            ):
                c = ComparatorEnum.COLON

            if shorten:
                k = keyword_map[self.keyword][0]
                if k is None:
                    k = ""
                    if c == ComparatorEnum.COLON:
                        c = ""

            return f"{k}{c}{value}"
        if self.comparator == ComparatorEnum.EXACT:
            return f"!{value}"
        return f"{value}"

    def __str__(self):
        return self.to_string()

    def __repr__(self):
        return f"Term({self})"

    @classmethod
    def from_tokens(cls, tokens):
        return Term(
            tokens.value[0],
            KeywordEnum.factory(tokens.keyword),
            ComparatorEnum.factory(tokens.comparator),
        )


class Query:
    def __init__(self, operand: Union[OpNode, str]):
        if isinstance(operand, str):
            self.root = self.parse(operand)
        else:
            self.root = operand

    @staticmethod
    def parse(expression: str) -> OpNode:
        """
        Parse a string and return the root object (``BinOp``, ``UnOp``, ``Term``)
        :param expression:  The string to parse
        :return:
        """
        results: pp.ParseResults = EXPRESSION.parse_string(expression, parse_all=True)
        return results[0]

    def to_string(self, shorten=False):
        """
        Recompose the query as a string

        :param shorten: If true, the query will be simplified and shorten using less explicit statements
        :return: The recomposed query
        """
        return self.root.to_string(shorten)

    def __getitem__(self, item):
        return self.root[item]

    def __repr__(self):
        return f"Query({repr(self.root)})"

    def __str__(self):
        return self.to_string()

    def __or__(self, other: "Query"):
        return Query(self.root | other.root)

    def __and__(self, other: "Query"):
        return Query(self.root & other.root)

    def __xor__(self, other: "Query"):
        return Query(self.root ^ other.root)

    def __add__(self, other: "Query"):
        return Query(self.root + other.root)

    def __sub__(self, other):
        return Query(self.root - other.root)

    def __invert__(self):
        return Query(~self.root)

import itertools
import logging
from collections import Counter
from typing import (
    Annotated,
    Any,
    Dict,
    Iterable,
    Iterator,
    List,
    Mapping,
    Optional,
    Sequence,
    Union,
    overload,
)

from ordered_set import OrderedSet
from pydantic import GetCoreSchemaHandler, StringConstraints
from pydantic_core import CoreSchema, core_schema

from mightstone.core import MightstoneModel

logger = logging.getLogger(__name__)

ColorGlyph = Annotated[
    str, StringConstraints(min_length=1, max_length=1, to_lower=True)
]


class Color(MightstoneModel):
    symbol: ColorGlyph
    index: int

    def __str__(self):
        return f"{{{self.symbol.upper()}}}"

    def __repr__(self):
        return f"Color({self.symbol})"


class ColorPie(Sequence[Color]):
    def __init__(self, colors: Iterable[Color]):
        if not all(isinstance(x, Color) for x in colors):
            raise ValueError("Please provide a Color object iterable")

        duplicates = [k for k, v in Counter(list(colors)).items() if v > 1]
        if len(duplicates):
            duplicates_as_string = ",".join(map(str, duplicates))
            raise ValueError(
                f"A color pie cannot hold the same color twice. {duplicates_as_string}"
            )

        # TODO: search duplicates color values
        self.colors = list(colors)

    def __getitem__(self, i: Union[int, slice, Union[int, str]]):
        if isinstance(i, int):
            return self.colors[i]

        try:
            return next(color for color in self.colors if color.symbol == i)
        except StopIteration:
            raise KeyError(f"{i} not found in {self}")

    def __len__(self) -> int:
        return len(self.colors)

    def __iter__(self) -> Iterator[Color]:
        for color in self.colors:
            yield color

    def shift(self, color: Color, step: int = 1) -> Color:
        return self.colors[(step + self.index(color)) % len(self.colors)]

    def __hash__(self):
        return hash(tuple(self))

    def parse(self, identity_as_string: str) -> "Identity":
        colors = []
        for letter in identity_as_string:
            colors.append(self[letter])
        return Identity(colors)

    def combinations(self) -> List["Identity"]:
        """
        A mathematical computation of all possible combinations of colors
        This will not provide a proper color pie centric combination though
        and cannot be used to provide a complete identity map that would
        build the red enemy guild (Boros) as rw, instead of wr in this case
        """
        return [
            Identity(c)
            for length in range(0, len(self.colors) + 1)
            for c in itertools.combinations(self.colors, length)
        ]

    def build_identity_map(self) -> "IdentityMap":
        idmap = IdentityMap(self)

        for combination in self.combinations():
            idmap.add(combination)

        return idmap

    def __repr__(self):
        return f"ColorPie({self.colors})"


class Identity(Sequence[Color]):
    def __init__(self, colors: Iterable[Color]):
        self.colors = OrderedSet(colors)
        self._name = ""
        self.aliases: List[str] = []
        self._canonical: Optional[str] = None

    @classmethod
    def __get_pydantic_core_schema__(
        cls, source_type: Any, handler: GetCoreSchemaHandler
    ) -> CoreSchema:
        return core_schema.no_info_after_validator_function(cls, handler(str))

    def describe(
        self,
        name: Optional[str] = None,
        aliases: Optional[List[str]] = None,
        canonical: Optional[str] = None,
    ):
        if name:
            self._name = name
        if aliases:
            self.aliases.extend(aliases)
        if canonical:
            self._canonical = canonical

    @property
    def name(self):
        if not self._name:
            return self.canonical
        return self._name

    @property
    def canonical(self) -> str:
        if self._canonical:
            return self._canonical
        if len(self.colors) == 0:
            return ""
        return "".join(
            [color.symbol for color in sorted(self.colors, key=lambda x: x.index)]
        )

    def checksum(self) -> int:
        """Checksum is computed from binary position of the color in the color-pie"""
        return sum(1 << color.index for color in self.colors)

    def matches(self, k: str):
        search = k.lower()
        if search in self.name.lower():
            return True
        if search in map(lambda x: x.lower(), self.aliases):
            return True
        return False

    def __str__(self):
        return f"{self.name}"

    def __repr__(self):
        return f"Identity({self.canonical})"

    @overload
    def __getitem__(self, i: int) -> Color: ...

    @overload
    def __getitem__(self, i: slice) -> OrderedSet[Color]: ...

    def __getitem__(self, i: Union[int, slice]) -> Union[Color, OrderedSet[Color]]:
        return self.colors.__getitem__(i)

    def __len__(self):
        return len(self.colors)

    def __eq__(self, other: object):
        if not isinstance(other, Identity):
            return NotImplemented

        return other.checksum() == self.checksum()


class IdentityMap(Mapping[int, Identity]):
    def __init__(self, pie: ColorPie):
        self.map: Dict[int, Identity] = {}
        self.pie = pie

    def refine(
        self,
        canonical: str,
        name: Optional[str] = None,
        aliases: Optional[List[str]] = None,
    ):
        self[canonical].describe(name=name, aliases=aliases, canonical=canonical)

    def add(self, colors=Iterable[Color]):
        """
        Appends an identity to the map
        No addition if the identity already exists
        """
        ident = Identity(colors)
        if ident.checksum() not in self.map:
            self.map[ident.checksum()] = ident

    def __getitem__(self, k: Union[int, str, Identity]) -> Identity:
        if isinstance(k, int):
            return self.map[k]

        if isinstance(k, Identity):
            return self.map[k.checksum()]

        if not isinstance(k, str):
            raise KeyError

        try:
            match = self.pie.parse(k)
            return self.map[match.checksum()]
        except KeyError:
            for identity in self.map.values():
                if identity.matches(k):
                    return identity

        raise KeyError

    def __len__(self) -> int:
        return self.map.__len__()

    def __iter__(self) -> Iterator[int]:
        return self.map.__iter__()


class ColorAffinity(MightstoneModel):
    """
    When talking about which colors get which evergreen creature keywords,
    R&D tends to talk about a system called "primary/secondary/tertiary".
    In their quest to differentiate the colors in the color wheel,
    each should have strengths and weaknesses.
    """

    primary: List[Color] = []
    secondary: List[Color] = []
    tertiary: List[Color] = []

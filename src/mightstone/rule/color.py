import itertools
import logging
from collections import Counter
from typing import Iterable, Iterator, List, Mapping, Sequence, Union

from ordered_set import OrderedSet
from pydantic import constr, validator

from mightstone.core import MightstoneModel

logger = logging.getLogger(__name__)


class Color(MightstoneModel):
    symbol: constr(to_lower=True, min_length=1, max_length=1)

    def __str__(self):
        return f"{{{self.symbol.upper()}}}"

    def __repr__(self):
        return f"Color({self.symbol})"


class ColorPie(MightstoneModel, Sequence[Color]):
    colors: List[Color]

    @validator("colors")
    def sanitize(cls, colors: Iterable[Color]) -> [Color]:
        if not all(isinstance(x, Color) for x in colors):
            raise ValueError("Please provide a Color object iterable")

        duplicates = [k for k, v in Counter(list(colors)).items() if v > 1]
        if len(duplicates):
            duplicates_as_string = ",".join(map(str, duplicates))
            raise ValueError(
                f"A color pie cannot hold the same color twice. {duplicates_as_string}"
            )

        # TODO: search duplicates color values
        return list(colors)

    def __getitem__(self, i: Union[int, str]):
        if isinstance(i, int):
            return self.colors[i]

        try:
            return next(color for color in self.colors if color.symbol == i)
        except StopIteration:
            raise KeyError(f"{i} not found in {self}")

    def __len__(self) -> int:
        return len(self.colors)

    def __iter__(self) -> Iterator[Color]:
        return iter(self.colors)

    def shift(self, color: Color, step: int = 1) -> Color:
        return self.colors[(step + self.index(color)) % len(self.colors)]

    def __hash__(self):
        return hash(tuple(self))

    def parse(self, identity_as_string: str) -> "Identity":
        colors = []
        for letter in identity_as_string:
            colors.append(self[letter])
        return Identity(self, colors)

    def combinations(self) -> ["Identity"]:
        """
        A mathematical computation of all possible combinations of colors
        This will not provide a proper color pie centric combination though
        and cannot be used to provide a complete identity map that would
        build the red enemy guild (Boros) as rw, instead of wr in this case
        """
        return [
            Identity(self, c)
            for length in range(0, len(self.colors) + 1)
            for c in itertools.combinations(self.colors, length)
        ]

    def build_identity_map(self) -> "IdentityMap":
        idmap = IdentityMap(self)
        logger.debug("Start color-pie combinations")
        idmap.add(Identity(self, []))
        logger.debug("Already added colorless")

        size = len(self.colors)
        for n in range(0, size + 1):
            logger.debug("building a list of %d color(s)", n)
            for step in range(1, n + 1):
                logger.debug("- With step: %d (0=same 1=allied, 2=enemy, 3+=!?)", step)
                if size % step == 0 and size / step < n:
                    logger.debug(
                        "This strategy cannot be fulfilled and will result a loop"
                    )
                    continue

                for color in self.colors:
                    logger.debug("With color: %s", color)
                    colors = [color]
                    i = 0
                    while i < n - 1:
                        picked_color = self.shift(colors[-1], step)
                        logger.debug("Picking color %d: %s", i, picked_color)
                        colors.append(picked_color)
                        i += 1

                    ident = Identity(self, colors)
                    logger.debug("added %s", ident)
                    idmap.add(ident)

        return idmap

    def __repr__(self):
        return f"ColorPie({self.colors})"


class Identity(Sequence[Color]):
    def __init__(self, pie: ColorPie, colors: Iterable[Color]):
        self.pie = pie
        self.colors = OrderedSet(colors)
        self._name = None
        self.aliases = []

    def describe(self, name: str = None, aliases: [str] = None):
        if name:
            self._name = name
        if aliases:
            self.aliases.extend(aliases)

    @property
    def name(self):
        if not self._name:
            return self.canonical
        return self._name

    @property
    def canonical(self) -> str:
        if len(self.colors) == 0:
            return "colorless"
        return "".join([color.symbol for color in self.colors])

    def checksum(self) -> int:
        """Checksum is computed from binary position of the color in the color-pie"""
        return sum(1 << self.pie.index(color) for color in self.colors)

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

    def __getitem__(self, i: int) -> Color:
        return self.colors.__getitem__(i)

    def __len__(self):
        return len(self.colors)

    def __eq__(self, other: "Identity"):
        try:
            return other.checksum() == self.checksum()
        except TypeError:
            return False


class IdentityMap(Mapping[int, Identity]):
    def __init__(self, pie: ColorPie):
        self.map = {}
        self.pie = pie

    def add(self, ident: Identity):
        """
        Appends an identity to the map
        No addition if the identity already exists
        """
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

    def __iter__(self) -> Iterator[str]:
        return self.map.__iter__()


class ColorAffinity(MightstoneModel):
    """
    When talking about which colors get which evergreen creature keywords,
    R&D tends to talk about a system called "primary/secondary/tertiary".
    In their quest to differentiate the colors in the color wheel,
    each should have strengths and weaknesses.
    """

    primary: List[Color]
    secondary: List[Color]
    tertiary: List[Color]

from enum import Enum
from typing import Annotated, Optional

from pydantic_core._pydantic_core import Url

from ...core import Fallback, MightstoneModel
from .color import ColorAffinity, Identity


class AbilityType(str, Enum):
    AUTO = "auto"
    STATIC = "static"
    SPELL = "spell"
    TRIGGERED = "triggered"
    ACTIVATED = "activated"
    EVASION = "evasion"
    CHARACTERISTIC_DEFINING = "characteristic-defining"


class Ability(MightstoneModel):
    name: str
    types: list[AbilityType]
    rules: list[str] = []
    glossaries: list[str] = []
    wiki: Optional[Url] = None
    introduced: Optional[str] = None
    last_seen: Optional[str] = None
    has_cost: bool = False
    reminder: Optional[str] = None
    stats: dict[str, int] = {}
    storm: Annotated[Optional[int], Fallback(None)] = None

    @property
    def is_evergreen(self) -> bool:
        return self.last_seen == "Evergreen"

    def affinity(self) -> ColorAffinity:
        raise NotImplementedError


class AbilityList(MightstoneModel):
    abilities: list[Ability] = []

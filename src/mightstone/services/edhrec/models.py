import re
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional

from pydantic import Field

from mightstone.core import MightstoneModel

salt_parser = re.compile(r"Salt Score: (?P<salt>[\d.]+)\n")
synergy_parser = re.compile(r"(?P<synergy>[\d.]+)% synergy")


class EdhRecCategory(Enum):
    TOP_COMMANDER = "topcommanders"
    COMMANDER = "commanders"
    NEW = "newcards"
    HIGH_SYNERGY = "highsynergycards"
    TOP_CARD = "topcards"
    CREATURE = "creatures"
    INSTANT = "instants"
    SORCERY = "sorceries"
    ARTEFACT_UTIL = "utilityartifacts"
    ENCHANTMENT = "enchantments"
    PLANEWALKER = "planeswalkers"
    LAND_UTIL = "utilitylands"
    ARTEFACT_MANA = "manaartifacts"
    LAND = "lands"


class EdhRecPeriod(Enum):
    PAST_WEEK = "pastweek"
    PAST_MONTH = "pastmonth"
    PAST_2YEAR = "past2years"


class EdhRecCardRef(MightstoneModel):
    name: str
    url: str


class EdhRecCard(MightstoneModel):
    cmc: int
    color_identity: List[str]

    combos: Optional[bool] = None
    label: Optional[str] = None
    legal_commander: Optional[bool] = None

    image_uris: List[dict]
    is_commander: Optional[bool] = None
    layout: str
    name: str
    names: List[str]
    inclusion: Optional[int] = None
    num_decks: Optional[int] = None
    potential_decks: Optional[int] = None
    precon: Optional[str] = None
    prices: dict
    primary_type: str
    rarity: str
    salt: float
    sanitized: str
    sanitized_wo: str
    type: str
    url: Optional[str] = None
    aetherhub_uri: Optional[str] = None
    archidekt_uri: Optional[str] = None
    deckstats_uri: Optional[str] = None
    moxfield_uri: Optional[str] = None
    mtggoldfish_uri: Optional[str] = None
    scryfall_uri: Optional[str] = None
    spellbook_uri: Optional[str] = None


class EdhRecCommanderSub(MightstoneModel):
    count: int
    suffix: str = Field(alias="href-suffix")
    value: str


class EdhRecCommanderDistribution(MightstoneModel):
    artifact: int = 0
    creature: int = 0
    enchantment: int = 0
    instant: int = 0
    land: int = 0
    planeswalker: int = 0
    sorcery: int = 0


class EdhRecCardItem(MightstoneModel):
    tag: str
    name: str
    slug: str
    url: Path
    label: Optional[str] = None
    inclusion: Optional[int] = None
    cards: Optional[List[EdhRecCardRef]] = None
    count: Optional[int] = None
    num_decks: Optional[int] = None
    potential_decks: Optional[int] = None
    synergy: Optional[float] = None
    salt: Optional[float] = None

    @classmethod
    def parse_payload(cls, data: dict, tag: Optional[str]):
        salt = salt_parser.search(data.get("label", "unspecified"))
        if salt:
            data["salt"] = float(salt.group("salt"))

        synergy = synergy_parser.search(data.get("label", ""))
        if synergy:
            data["synergy"] = float(synergy.group("synergy"))

        return EdhRecCardItem.model_validate(
            {
                **data,
                "tag": tag,
                "url": f"/pages{data.get('url')}.json",
                "slug": slugify(data.get("name", "")),
            }
        )


class EdhRecCardList(MightstoneModel):
    tag: str
    items: List[EdhRecCardItem] = []

    @classmethod
    def parse_payload(cls, data: dict):
        tag = data.get("tag")
        return EdhRecCardList.model_validate(
            {
                "tag": tag,
                "items": list(
                    EdhRecCardItem.parse_payload(item, tag).dict()
                    for item in data["cardviews"]
                ),
            }
        )


class EdhRecCommander(MightstoneModel):
    card: EdhRecCard
    articles: List[dict] = []
    cards: List[EdhRecCardList] = []
    mana_curve: Dict[int, int] = {i: 0 for i in range(0, 11)}
    themes: List[EdhRecCommanderSub] = []
    budget: List[EdhRecCommanderSub] = []
    distribution: EdhRecCommanderDistribution
    links: List[dict] = []

    @classmethod
    def parse_payload(cls, data: dict):
        return EdhRecCommander(
            card=EdhRecCard.model_validate(
                data.get("container", {}).get("json_dict", {}).get("card")
            ),
            cards=[
                EdhRecCardList.parse_payload(payload)
                for payload in data.get("container", {})
                .get("json_dict", {})
                .get("cardlists")
            ],
            articles=data.get("panels", {}).get("articles", []),
            links=data.get("panels", {}).get("links", []),
            mana_curve=data.get("panels", {}).get("mana_curve", {}),
            themes=data.get("panels", {}).get("tribelinks", {}).get("themes", {}),
            budget=data.get("panels", {}).get("tribelinks", {}).get("budget", {}),
            distribution=data,  # type: ignore
        )


class EdhRecFilterOperator(Enum):
    GREATER_THAN = "gt"
    LESS_THAN = "lt"
    EQUAL = "eq"
    NOT_EQUAL = "ne"


class EdhRecFilterType(Enum):
    CREATURE = "c"
    INSTANT = "i"
    SORCERY = "s"
    ARTIFACT = "a"
    ENCHANTMENT = "e"
    PLANESWALKER = "p"
    LANDS = "l"
    PRICE = "d"


class EdhRecFilterComparator(MightstoneModel):
    value: int = 0
    operator: EdhRecFilterOperator = EdhRecFilterOperator.EQUAL

    def __str__(self):
        return f"{self.operator.value}={self.value}"


class EdhRecFilterQuery(MightstoneModel):
    card_in: List[str] = []
    card_out: List[str] = []
    count: Dict[EdhRecFilterType, EdhRecFilterComparator] = {}

    def __str__(self):
        filters = []
        filters.extend([f"Out={card}" for card in self.card_out])
        filters.extend([f"In={card}" for card in self.card_in])
        filters.extend(
            [f"{field.value}:{comparator}" for field, comparator in self.count.items()]
        )
        return ";".join(filters)


class EdhRecRecs(MightstoneModel):
    commanders: List[EdhRecCard] = []
    inRecs: List[EdhRecCard] = []
    outRecs: List[EdhRecCard] = []


def slugify(string: Optional[str]):
    import slugify

    if string is None:
        return None
    return slugify.slugify(
        string, separator="-", replacements=[("'", ""), ("+", "plus-")]
    )

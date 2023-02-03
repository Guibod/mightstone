import logging
import re
from enum import Enum
from pathlib import Path
from typing import AsyncGenerator, Dict, List, Optional, Tuple, Union

from aiohttp import ClientResponseError, ClientSession
from pydantic.error_wrappers import ValidationError
from pydantic.fields import Field

from mightstone.ass import asyncio_run
from mightstone.core import MightstoneModel
from mightstone.services import ServiceError

salt_parser = re.compile(r"Salt Score: (?P<salt>[\d.]+)\n")
synergy_parser = re.compile(r"(?P<synergy>[\d.]+)% synergy")

logger = logging.getLogger(__name__)


class EdhRecIdentity(Enum):
    COLORLESS = "colorless"
    W = "w"
    U = "u"
    B = "b"
    R = "r"
    G = "g"
    WU = "wu"
    UB = "ub"
    BR = "br"
    RG = "rg"
    GW = "gw"
    WB = "wb"
    UR = "ur"
    BG = "bg"
    RW = "rw"
    GU = "gu"
    WUB = "wub"
    UBR = "ubr"
    BRG = "brg"
    RGW = "rgw"
    GWU = "gwu"
    WBG = "wbg"
    URW = "urw"
    BGU = "bgu"
    RWB = "rwb"
    GUR = "gur"
    WUBR = "wubr"
    UBRG = "ubrg"
    BRGW = "brgw"
    RGWU = "rgwu"
    GWUB = "gwub"
    WUBRG = "wubrg"


class EdhRecTag(Enum):
    TRIBES = "tribes"
    SET = "sets"
    NONE = ""
    THEME_POPULARITY = "themesbypopularitysort"
    THEME = "themes"
    COMMANDER = "topcommanders"
    COMPANION = "companions"


class EdhRecType(Enum):
    CREATURE = "creatures"
    INSTANT = "instants"
    SORCERY = "sorceries"
    ARTIFACT = "artifacts"
    ARTIFACT_EQUIPMENT = "equipment"
    ARTIFACT_UTILITY = "utility-artifacts"
    ARTIFACT_MANA = "mana-artifacts"
    ENCHANTMENT = "enchantments"
    ENCHANTMENT_AURA = "auras"
    PLANESWALKER = "planeswalker"
    LAND = "lands"
    LAND_UTILITY = "utility-lands"
    LAND_FIXING = "color-fixing-lands"


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
    combos: bool
    image_uris: List[dict]
    is_commander: bool = None
    legal_commander: bool
    label: str
    layout: str
    name: str
    names: List[str]
    inclusion: int = None
    num_decks: int = None
    potential_decks: int = None
    precon: str = None
    prices: dict
    primary_type: str
    rarity: str
    salt: float
    sanitized: str
    sanitized_wo: str
    type: str
    url: str = None
    aetherhub_uri: str = None
    archidekt_uri: str = None
    deckstats_uri: str = None
    moxfield_uri: str = None
    mtggoldfish_uri: str = None
    scryfall_uri: str = None
    spellbook_uri: str = None


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
    label: str
    slug: str
    url: Path
    inclusion: int = None
    cards: List[EdhRecCardRef] = None
    count: int = None
    num_decks: int = None
    potential_decks: int = None
    synergy: float = None
    salt: float = None

    @classmethod
    def parse_payload(cls, data: dict, tag: str = None):
        salt = salt_parser.search(data.get("label", "unspecified"))
        if salt:
            data["salt"] = float(salt.group("salt"))

        synergy = synergy_parser.search(data.get("label", ""))
        if synergy:
            data["synergy"] = float(synergy.group("synergy"))

        return EdhRecCardItem.parse_obj(
            {
                **data,
                "tag": tag,
                "url": str("/pages" + data.get("url") + ".json"),
                "slug": slugify(data.get("name", "")),
            }
        )


class EdhRecCardList(MightstoneModel):
    tag: str
    items: List[EdhRecCardItem] = []

    @classmethod
    def parse_payload(cls, data: dict):
        tag = data.get("tag")
        return EdhRecCardList.parse_obj(
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
            card=EdhRecCard.parse_obj(
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
            distribution=data,
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


class EdhRecApi:
    def __init__(self):
        self.session = ClientSession(base_url="https://edhrec.com")

    async def filter(self, commander: str, query: EdhRecFilterQuery):
        try:
            async with self.session:
                async with self.session.get(
                    "/api/filters/",
                    params={
                        "f": str(query),
                        "dir": "commanders",
                        "cmdr": slugify(commander),
                    },
                ) as f:
                    f.raise_for_status()
                    return EdhRecCommander.parse_payload(await f.json())

        except ClientResponseError as e:
            raise ServiceError(
                message="Failed to fetch data from EDHREC",
                url=e.request_info.real_url,
                status=e.status,
            )


class EdhRecStatic:
    def __init__(self):
        self.session = ClientSession(base_url="https://json.edhrec.com")

    async def commander(self, name: str, sub: str = None):
        path = f"commanders/{slugify(name)}.json"
        if sub:
            path = f"commanders/{slugify(name)}/{slugify(sub)}.json"

        data = await self._get_static_page(path)

        return EdhRecCommander.parse_payload(data)

    async def tribes(
        self, identity: Union[EdhRecIdentity, str] = None
    ) -> AsyncGenerator[EdhRecCardItem, None]:
        if identity:
            identity = EdhRecIdentity(identity)
            async for item in self._page_item_generator(
                f"commanders/{identity.value}.json", EdhRecTag.TRIBES, related=True
            ):
                yield item
        else:
            async for item in self._page_item_generator(
                "tribes.json", EdhRecTag.TRIBES
            ):
                yield item

    async def themes(
        self, identity: Union[EdhRecIdentity, str] = None
    ) -> AsyncGenerator[EdhRecCardItem, None]:
        if identity:
            identity = EdhRecIdentity(identity)
            async for item in self._page_item_generator(
                f"commanders/{identity.value}.json", EdhRecTag.THEME, related=True
            ):
                yield item
        else:
            async for item in self._page_item_generator(
                "themes.json", EdhRecTag.THEME_POPULARITY
            ):
                yield item

    async def sets(self) -> AsyncGenerator[dict, None]:
        async for item in self._page_item_generator("sets.json", EdhRecTag.SET):
            yield item

    async def salt(self, year: int = None) -> AsyncGenerator[EdhRecCardItem, None]:
        path = "top/salt.json"
        if year:
            path = f"top/salt-{year}.json"
        async for item in self._page_item_generator(path):
            yield item

    async def top_cards(
        self,
        type: EdhRecType = None,
        period: Union[str, EdhRecPeriod] = EdhRecPeriod.PAST_WEEK,
    ) -> AsyncGenerator[EdhRecCardItem, None]:
        period = EdhRecPeriod(period)
        if type:
            async for item in self._page_item_generator(
                f"top/{type.value}.json", period
            ):
                yield item
            return

        if period == EdhRecPeriod.PAST_WEEK:
            path = "top/week.json"
        elif period == EdhRecPeriod.PAST_MONTH:
            path = "top/month.json"
        else:
            path = "top/year.json"
        async for item in self._page_item_generator(path):
            yield item

    async def cards(
        self,
        theme: str = None,
        commander: str = None,
        identity: Union[EdhRecIdentity, str] = None,
        set: str = None,
        category: EdhRecCategory = None,
    ) -> AsyncGenerator[EdhRecCardItem, None]:
        if category:
            category = EdhRecCategory(category)

        if commander:
            if theme:
                raise ValueError("commander and theme options are mutually exclusive")
            if identity:
                raise ValueError(
                    "commander and identity options are mutually exclusive"
                )
            if set:
                raise ValueError("commander and set options are mutually exclusive")

            slug = slugify(commander)
            path = f"commanders/{slug}.json"
            if theme:
                path = f"commanders/{slug}/{slugify(theme)}.json"
            async for item in self._page_item_generator(path, category):
                yield item

            return

        if set:
            if theme:
                raise ValueError("set and theme options are mutually exclusive")
            if identity:
                raise ValueError("set and identity options are mutually exclusive")
            async for item in self._page_item_generator(
                f"sets/{slugify(set)}.json", category
            ):
                yield item
            return

        if identity and not theme:
            raise ValueError("youn must specify a theme to search by color identity")

        path = f"themes/{slugify(theme)}.json"
        if identity:
            identity = EdhRecIdentity(identity)
            path = f"themes/{slugify(theme)}/{identity.value}.json"
        async for item in self._page_item_generator(path, category):
            yield item

    async def companions(self) -> AsyncGenerator[EdhRecCardItem, None]:
        async for item in self._page_item_generator(
            "companions.json", EdhRecTag.COMPANION
        ):
            yield item

    async def partners(
        self, identity: Union[EdhRecIdentity, str] = None
    ) -> AsyncGenerator[EdhRecCardItem, None]:
        path = "partners.json"
        if identity:
            identity = EdhRecIdentity(identity)
            path = f"partners/{identity.value}.json"
        async for item in self._page_item_generator(path):
            yield item

    async def commanders(
        self, identity: Union[EdhRecIdentity, str] = None
    ) -> AsyncGenerator[EdhRecCardItem, None]:
        path = "commanders.json"
        if identity:
            identity = EdhRecIdentity(identity)
            path = f"commanders/{identity.value}.json"
        async for item in self._page_item_generator(path):
            yield item

    async def combos(
        self, identity: Union[EdhRecIdentity, str]
    ) -> AsyncGenerator[EdhRecCardItem, None]:
        identity = EdhRecIdentity(identity)
        async for item in self._page_item_generator(f"combos/{identity.value}.json"):
            yield item

    async def combo(
        self, identity: str, identifier: Union[EdhRecIdentity, str]
    ) -> AsyncGenerator[EdhRecCardItem, None]:
        identity = EdhRecIdentity(identity)
        async for item in self._page_item_generator(
            f"combos/{identity.value}/{int(identifier)}.json"
        ):
            yield item

    async def _page_item_generator(
        self,
        path,
        tag: Union[EdhRecTag, EdhRecType, EdhRecPeriod, EdhRecCategory] = None,
        related=False,
    ) -> AsyncGenerator[EdhRecCardItem, None]:
        """
        Async generator that will wrap Pydantic validation
        and ensure that no validation error are raised
        """
        if tag:
            tag = tag.value
        async for (tag, page, index, item) in self._get_page(path, tag, related):
            try:
                yield EdhRecCardItem.parse_payload(item, tag)
            except ValidationError as e:
                logging.warning(
                    "Failed to parse an EDHREC item from %s at page %d, index %d",
                    path,
                    page,
                    index,
                )
                logging.debug(e.json())

    async def _get_static_page(self, path) -> dict:
        try:
            async with self.session:
                async with self.session.get(f"/pages/{path}") as f:
                    f.raise_for_status()
                    return await f.json()
        except ClientResponseError as e:
            raise ServiceError(
                message="Failed to fetch data from EDHREC",
                url=e.request_info.real_url,
                status=e.status,
            )

    async def _get_page(
        self, path, tag: str = None, related=False
    ) -> AsyncGenerator[Tuple[str, int, int, dict], None]:
        """
        Read a EDHREC page data, and return it as a tuple:
        - tag as string
        - page
        - index
        - the payload itself
        """
        data = await self._get_static_page(path)
        page = 1

        if related:
            iterator = [
                {"tag": tag, "cardviews": data.get("relatedinfo", {}).get(tag, [])}
            ]
        else:
            iterator = (
                data.get("container", {}).get("json_dict", {}).get("cardlists", [])
            )

        for item_list in iterator:
            current_tag = item_list.get("tag", "")
            if tag is not None and str(tag) != current_tag:
                continue

            for index, item in enumerate(item_list.get("cardviews", [])):
                yield current_tag, page, index, item,

            while item_list.get("more"):
                data = await self._get_static_page(f"/pages/{item_list.get('more')}")
                page += 1
                for index, item in enumerate(data.get("cardviews", [])):
                    yield current_tag, page, index, item


def slugify(string: Optional[str]):
    import slugify

    if string is None:
        return None
    return slugify.slugify(
        string, separator="-", replacements=[("'", ""), ("+", "plus-")]
    )


if __name__ == "__main__":

    async def main():
        # from aiostream import pipe, stream

        logging.basicConfig(level=logging.DEBUG)

    # rec = EdhRecStatic()
    # s = stream.preserve(rec.tribes()) | pipe.print()
    # s = stream.preserve(rec.tribes("brg")) | pipe.print()
    # s = stream.preserve(rec.themes()) | pipe.print()
    # s = stream.preserve(rec.themes("brg")) | pipe.print()
    # s = stream.preserve(rec.themes(commander="gyruda-doom-of-depths")) | pipe.print()
    # s = (stream.preserve(rec.top_cards(period=EdhRecPeriod.PAST_MONTH))| pipe.print())
    # s = stream.preserve(rec.tribes(identity="ub")) | pipe.print()
    # s = stream.preserve(rec.themes(identity="ub")) | pipe.print()
    # s = stream.preserve(rec.themes()) | pipe.print()
    # s = stream.preserve(rec.sets()) | pipe.print()
    # s = stream.preserve(rec.salt(2021)) | pipe.print()
    # s = stream.preserve(rec.top_cards(period=EdhRecPeriod.PAST_2YEAR)) | pipe.print()
    # s = stream.preserve(rec.top_cards(EdhRecType.LAND_FIXING,
    # EdhRecPeriod.PAST_2YEAR)) | pipe.print()
    # s = stream.preserve(rec.cards(theme="treasure", identity="gu")) | pipe.print()
    # s = stream.preserve(rec.cards(set="FUT", category="commanders")) | pipe.print()
    # s = stream.preserve(rec.companions()) | pipe.print()
    # s = stream.preserve(rec.partners()) | pipe.print()
    # s = stream.preserve(rec.commanders("ub")) | pipe.print()
    # s = stream.preserve(rec.commanders()) | pipe.print()
    # s = stream.preserve(rec.combos("ub")) | pipe.print()
    # s = stream.preserve(rec.combo("ub", 833)) | pipe.print()
    # | pipe.filter(lambda x: x["sanitized"] != x["slug"])\
    # await s
    # commander = await rec.commander("gyruda-doom-of-depths", "budget")
    # print(commander.dict())
    # rec = EdhRecApi()
    # commander = await rec.filter("gyruda-doom-of-depths",
    # EdhRecFilterQuery().parse_obj({
    #     "card_in": ["Sol Ring"],
    #     "card_out": ["Rampant Growth"],
    #     "count": {EdhRecFilterType.INSTANT:
    #     {"gt": 2}, EdhRecFilterType.PRICE: {"lt": 4321}},
    # }))
    # print(commander.json())
    # #

    asyncio_run(main())

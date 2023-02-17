import logging
import re
from enum import Enum
from pathlib import Path
from typing import AsyncGenerator, Dict, List, Optional, Tuple, Union

import asyncstdlib
from aiohttp import ClientResponseError
from pydantic.error_wrappers import ValidationError
from pydantic.fields import Field

from mightstone.core import MightstoneModel
from mightstone.services import MightstoneHttpClient, ServiceError

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

    combos: bool = None
    label: str = None
    legal_commander: bool = None

    image_uris: List[dict]
    is_commander: bool = None
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
    slug: str
    url: Path
    label: str = None
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


class EdhRecRecs(MightstoneModel):
    commanders: List[EdhRecCard] = []
    inRecs: List[EdhRecCard] = []
    outRecs: List[EdhRecCard] = []


class EdhRecApi(MightstoneHttpClient):
    """
    HTTP client for dynamic data hosted at https://edhrec.com/api/
    """

    base_url = "https://edhrec.com"

    async def recs(self, commanders: List[str], cards: List[str]):
        """
        Obtain EDHREC recommendations for a given commander (or partners duo)
        for a given set of cards in the deck.

        Returns a list of 99 suggested cards not contained in the list
        :param commanders: A list of one or two commander card name
        :param cards: A list of card name
        :exception ClientResponseError
        :returns An EdhRecRecs object
        """
        try:
            session = await self._build_session()
            async with session.post(
                "/api/recs/",
                json={"cards": cards, "commanders": commanders},
            ) as f:
                f.raise_for_status()
                data = await f.json()

                if data.get("errors"):
                    raise ServiceError(
                        message=data.get("errors")[0],
                        data=data,
                        url=f.request_info.real_url,
                        status=f.status,
                    )

                return EdhRecRecs.parse_obj(data)

        except ClientResponseError as e:
            raise ServiceError(
                message="Failed to fetch data from EDHREC",
                url=e.request_info.real_url,
                status=e.status,
            )

    async def filter(self, commander: str, query: EdhRecFilterQuery) -> EdhRecCommander:
        """
        Read Commander related information, and return an EdhRecCommander object

        :param commander: Commander name or slug
        :param query: An EdhRecFilterQuery object describing the request
        :return: An EdhRecCommander representing answer
        """
        try:
            session = await self._build_session()
            async with session.get(
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


class EdhRecStatic(MightstoneHttpClient):
    """
    HTTP client for static JSON data hosted at https://json.edhrec.com
    """

    base_url = "https://json.edhrec.com"

    async def commander(self, name: str, sub: str = None) -> EdhRecCommander:
        """

        :param name: Commander
        :param sub:
        :return:
        """
        path = f"commanders/{slugify(name)}.json"
        if sub:
            path = f"commanders/{slugify(name)}/{slugify(sub)}.json"

        data = await self._get_static_page(path)

        return EdhRecCommander.parse_payload(data)

    async def tribes(
        self, identity: Union[EdhRecIdentity, str] = None, limit: int = None
    ) -> AsyncGenerator[EdhRecCardItem, None]:
        if identity:
            identity = EdhRecIdentity(identity)
            async for item in self._page_item_generator(
                f"commanders/{identity.value}.json",
                EdhRecTag.TRIBES,
                related=True,
                limit=limit,
            ):
                yield item
        else:
            async for item in self._page_item_generator(
                "tribes.json", EdhRecTag.TRIBES, limit=limit
            ):
                yield item

    async def themes(
        self, identity: Union[EdhRecIdentity, str] = None, limit: int = None
    ) -> AsyncGenerator[EdhRecCardItem, None]:
        if identity:
            identity = EdhRecIdentity(identity)
            async for item in self._page_item_generator(
                f"commanders/{identity.value}.json",
                EdhRecTag.THEME,
                related=True,
                limit=limit,
            ):
                yield item
        else:
            async for item in self._page_item_generator(
                "themes.json", EdhRecTag.THEME_POPULARITY, limit=limit
            ):
                yield item

    async def sets(self, limit: int = None) -> AsyncGenerator[dict, None]:
        async for item in self._page_item_generator(
            "sets.json", EdhRecTag.SET, limit=limit
        ):
            yield item

    async def salt(
        self, year: int = None, limit: int = None
    ) -> AsyncGenerator[EdhRecCardItem, None]:
        path = "top/salt.json"
        if year:
            path = f"top/salt-{year}.json"
        async for item in self._page_item_generator(path, limit=limit):
            yield item

    async def top_cards(
        self,
        type: EdhRecType = None,
        period: EdhRecPeriod = EdhRecPeriod.PAST_WEEK,
        limit: int = None,
    ) -> AsyncGenerator[EdhRecCardItem, None]:
        period = EdhRecPeriod(period)
        if type:
            type = EdhRecType(type)
            async for item in self._page_item_generator(
                f"top/{type.value}.json", period, limit=limit
            ):
                yield item
            return

        if period == EdhRecPeriod.PAST_WEEK:
            path = "top/week.json"
        elif period == EdhRecPeriod.PAST_MONTH:
            path = "top/month.json"
        else:
            path = "top/year.json"
        async for item in self._page_item_generator(path, limit=limit):
            yield item

    async def cards(
        self,
        theme: str = None,
        commander: str = None,
        identity: Union[EdhRecIdentity, str] = None,
        set: str = None,
        category: EdhRecCategory = None,
        limit: int = None,
    ) -> AsyncGenerator[EdhRecCardItem, None]:
        if category:
            category = EdhRecCategory(category)

        if not theme and not commander and not set:
            raise ValueError("You must either provide a theme, commander or set")

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
            async for item in self._page_item_generator(path, category, limit=limit):
                yield item

            return

        if set:
            if theme:
                raise ValueError("set and theme options are mutually exclusive")
            if identity:
                raise ValueError("set and identity options are mutually exclusive")
            async for item in self._page_item_generator(
                f"sets/{slugify(set)}.json", category, limit=limit
            ):
                yield item
            return

        if identity and not theme:
            raise ValueError("you must specify a theme to search by color identity")

        path = f"themes/{slugify(theme)}.json"
        if identity:
            identity = EdhRecIdentity(identity)
            path = f"themes/{slugify(theme)}/{identity.value}.json"
        async for item in self._page_item_generator(path, category, limit=limit):
            yield item

    async def companions(
        self, limit: int = None
    ) -> AsyncGenerator[EdhRecCardItem, None]:
        async for item in self._page_item_generator(
            "companions.json", EdhRecTag.COMPANION, limit=limit
        ):
            yield item

    async def partners(
        self, identity: Union[EdhRecIdentity, str] = None, limit: int = None
    ) -> AsyncGenerator[EdhRecCardItem, None]:
        path = "partners.json"
        if identity:
            identity = EdhRecIdentity(identity)
            path = f"partners/{identity.value}.json"
        async for item in self._page_item_generator(path, limit=limit):
            yield item

    async def commanders(
        self, identity: Union[EdhRecIdentity, str] = None, limit: int = None
    ) -> AsyncGenerator[EdhRecCardItem, None]:
        path = "commanders.json"
        if identity:
            identity = EdhRecIdentity(identity)
            path = f"commanders/{identity.value}.json"
        async for item in self._page_item_generator(path, limit=limit):
            yield item

    async def combos(
        self, identity: Union[EdhRecIdentity, str], limit: int = None
    ) -> AsyncGenerator[EdhRecCardItem, None]:
        identity = EdhRecIdentity(identity)
        async for item in self._page_item_generator(
            f"combos/{identity.value}.json", limit=limit
        ):
            yield item

    async def combo(
        self, identity: str, identifier: Union[EdhRecIdentity, str], limit: int = None
    ) -> AsyncGenerator[EdhRecCardItem, None]:
        identity = EdhRecIdentity(identity)
        async for item in self._page_item_generator(
            f"combos/{identity.value}/{int(identifier)}.json", limit=limit
        ):
            yield item

    async def _page_item_generator(
        self,
        path,
        tag: Union[EdhRecTag, EdhRecType, EdhRecPeriod, EdhRecCategory] = None,
        related=False,
        limit: int = None,
    ) -> AsyncGenerator[EdhRecCardItem, None]:
        """
        Async generator that will wrap Pydantic validation
        and ensure that no validation error are raised
        """
        if tag:
            tag = tag.value

        enumerator = asyncstdlib.enumerate(self._get_page(path, tag, related))
        async with asyncstdlib.scoped_iter(enumerator) as protected_enumerator:
            async for i, (tag, page, index, item) in protected_enumerator:
                if limit and i == limit:
                    logging.debug(f"Reached limit of {limit}, stopping iteration")
                    return

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
                item_list = await self._get_static_page(f"{item_list.get('more')}")
                page += 1
                for index, item in enumerate(item_list.get("cardviews", [])):
                    yield current_tag, page, index, item


def slugify(string: Optional[str]):
    import slugify

    if string is None:
        return None
    return slugify.slugify(
        string, separator="-", replacements=[("'", ""), ("+", "plus-")]
    )

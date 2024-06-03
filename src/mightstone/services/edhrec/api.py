import logging
from enum import Enum
from typing import AsyncGenerator, List, Optional, Tuple, Union

import asyncstdlib
from httpx import HTTPStatusError
from pydantic import ValidationError

from mightstone.ass import sync_generator, synchronize
from mightstone.services import MightstoneHttpClient, ServiceError
from mightstone.services.edhrec.models import (
    EdhRecCardItem,
    EdhRecCategory,
    EdhRecCommander,
    EdhRecFilterQuery,
    EdhRecPeriod,
    EdhRecRecs,
    slugify,
)

logger = logging.getLogger("mightstone")


class EdhRecIdentity(str, Enum):
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


class EdhRecTag(str, Enum):
    TRIBES = "tribes"
    SET = "sets"
    NONE = ""
    THEME_POPULARITY = "themesbypopularitysort"
    THEME = "themes"
    COMMANDER = "topcommanders"
    COMPANION = "companions"


class EdhRecType(str, Enum):
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


class EdhRecApi(MightstoneHttpClient):
    """
    HTTP client for dynamic data hosted at https://edhrec.com/api/
    """

    base_url = "https://edhrec.com"

    async def recommendations_async(self, commanders: List[str], cards: List[str]):
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
            session = self.client
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

                return EdhRecRecs.model_validate(data)

        except HTTPStatusError as e:
            raise ServiceError(
                message="Failed to fetch data from EDHREC",
                url=e.request.url,
                status=e.response.status_code,
            )

    recommendations = synchronize(recommendations_async)

    async def filter_async(
        self, commander: str, query: EdhRecFilterQuery
    ) -> EdhRecCommander:
        """
        Read Commander related information, and return an EdhRecCommander object

        :param commander: Commander name or slug
        :param query: An EdhRecFilterQuery object describing the request
        :return: An EdhRecCommander representing answer
        """
        try:
            session = await self.client
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

        except HTTPStatusError as e:
            raise ServiceError(
                message="Failed to fetch data from EDHREC",
                url=e.request.url,
                status=e.response.status_code,
            )

    filter = synchronize(filter_async)


class EdhRecStatic(MightstoneHttpClient):
    """
    HTTP client for static JSON data hosted at https://json.edhrec.com
    """

    base_url = "https://json.edhrec.com"

    async def commander_async(
        self, name: str, sub: Optional[str] = None
    ) -> EdhRecCommander:
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

    commander = synchronize(commander_async)

    async def tribes_async(
        self,
        identity: Optional[Union[EdhRecIdentity, str]] = None,
        limit: Optional[int] = None,
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

    tribes = sync_generator(tribes_async)

    async def themes_async(
        self,
        identity: Optional[Union[EdhRecIdentity, str]] = None,
        limit: Optional[int] = None,
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

    themes = sync_generator(themes_async)

    async def sets_async(
        self, limit: Optional[int] = None
    ) -> AsyncGenerator[EdhRecCardItem, None]:
        async for item in self._page_item_generator(
            "sets.json", EdhRecTag.SET, limit=limit
        ):
            yield item

    sets = sync_generator(sets_async)

    async def salt_async(
        self, year: Optional[int] = None, limit: Optional[int] = None
    ) -> AsyncGenerator[EdhRecCardItem, None]:
        path = "top/salt.json"
        if year:
            path = f"top/salt-{year}.json"
        async for item in self._page_item_generator(path, limit=limit):
            yield item

    salt = sync_generator(salt_async)

    async def top_cards_async(
        self,
        type: Optional[EdhRecType] = None,
        period: EdhRecPeriod = EdhRecPeriod.PAST_WEEK,
        limit: Optional[int] = None,
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

    top_cards = sync_generator(top_cards_async)

    async def cards_async(
        self,
        theme: Optional[str] = None,
        commander: Optional[str] = None,
        identity: Optional[Union[EdhRecIdentity, str]] = None,
        set: Optional[str] = None,
        category: Optional[EdhRecCategory] = None,
        limit: Optional[int] = None,
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

    cards = sync_generator(cards_async)

    async def companions_async(
        self, limit: Optional[int] = None
    ) -> AsyncGenerator[EdhRecCardItem, None]:
        async for item in self._page_item_generator(
            "companions.json", EdhRecTag.COMPANION, limit=limit
        ):
            yield item

    companions = sync_generator(companions_async)

    async def partners_async(
        self,
        identity: Optional[Union[EdhRecIdentity, str]] = None,
        limit: Optional[int] = None,
    ) -> AsyncGenerator[EdhRecCardItem, None]:
        path = "partners.json"
        if identity:
            identity = EdhRecIdentity(identity)
            path = f"partners/{identity.value}.json"
        async for item in self._page_item_generator(path, limit=limit):
            yield item

    partners = sync_generator(partners_async)

    async def commanders_async(
        self,
        identity: Optional[Union[EdhRecIdentity, str]] = None,
        limit: Optional[int] = None,
    ) -> AsyncGenerator[EdhRecCardItem, None]:
        path = "commanders.json"
        if identity:
            identity = EdhRecIdentity(identity)
            path = f"commanders/{identity.value}.json"
        async for item in self._page_item_generator(path, limit=limit):
            yield item

    commanders = sync_generator(commanders_async)

    async def combos_async(
        self, identity: Union[EdhRecIdentity, str], limit: Optional[int] = None
    ) -> AsyncGenerator[EdhRecCardItem, None]:
        identity = EdhRecIdentity(identity)
        async for item in self._page_item_generator(
            f"combos/{identity.value}.json", limit=limit
        ):
            yield item

    combos = sync_generator(combos_async)

    async def combo_async(
        self,
        identity: str,
        identifier: Union[EdhRecIdentity, str],
        limit: Optional[int] = None,
    ) -> AsyncGenerator[EdhRecCardItem, None]:
        identity = EdhRecIdentity(identity)
        async for item in self._page_item_generator(
            f"combos/{identity.value}/{int(identifier)}.json", limit=limit
        ):
            yield item

    combo = sync_generator(combo_async)

    async def _page_item_generator(
        self,
        path,
        tag: Optional[
            Union[EdhRecTag, EdhRecType, EdhRecPeriod, EdhRecCategory]
        ] = None,
        related=False,
        limit: Optional[int] = None,
    ) -> AsyncGenerator[EdhRecCardItem, None]:
        """
        Async generator that will wrap Pydantic validation
        and ensure that no validation error are raised
        """
        ttag: Optional[str] = None
        if tag:
            ttag = tag.value

        enumerator = asyncstdlib.enumerate(self._get_page(path, ttag, related))
        async with asyncstdlib.scoped_iter(enumerator) as protected_enumerator:
            async for i, (ttag, page, index, item) in protected_enumerator:
                if limit and i == limit:
                    logger.debug(f"Reached limit of {limit}, stopping iteration")
                    return

                try:
                    yield EdhRecCardItem.parse_payload(item, ttag)
                except ValidationError as e:
                    logger.warning(
                        "Failed to parse an EDHREC item from %s at page %d, index %d",
                        path,
                        page,
                        index,
                    )
                    logger.debug(e.json())

    async def _get_static_page(self, path) -> dict:
        try:
            f = await self.client.get(f"/pages/{path}")
            f.raise_for_status()
            return f.json()
        except HTTPStatusError as e:
            raise ServiceError(
                message="Failed to fetch data from EDHREC",
                url=e.request.url,
                status=e.response.status_code,
            )

    async def _get_page(
        self, path, tag: Optional[str] = None, related=False
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
                yield (
                    current_tag,
                    page,
                    index,
                    item,
                )

            while item_list.get("more"):
                item_list = await self._get_static_page(f"{item_list.get('more')}")
                page += 1
                for index, item in enumerate(item_list.get("cardviews", [])):
                    yield current_tag, page, index, item

import asyncio
import logging
import re
from enum import Enum
from functools import lru_cache
from typing import (
    Any,
    AsyncGenerator,
    Callable,
    Iterable,
    Iterator,
    List,
    Optional,
    Type,
    TypeVar,
    Union,
)

from asyncstdlib.itertools import islice
from httpx import Client, HTTPStatusError, Timeout

from mightstone.ass import synchronize
from mightstone.services import MightstoneHttpClient, ServiceError
from mightstone.services.edhrec.models import (
    Collection,
    CollectionItem,
    DeckItem,
    EnumPeriod,
    EnumType,
    FilterQuery,
    Page,
    PageAverageDeck,
    PageBackground,
    PageBackgrounds,
    PageCard,
    PageCombo,
    PageCombos,
    PageCommander,
    PageCommanders,
    PageCompanions,
    PageDeck,
    PageDecks,
    PagePartner,
    PagePartners,
    PageSalts,
    PageSet,
    PageStaples,
    PageTheme,
    PageThemes,
    PageTopCards,
    PageTypal,
    PageTypals,
    Recommendations,
    slugify,
)

PROXY_INSTANCE_RE = re.compile(r"/_next/static/(?P<instance>[a-zA-Z0-9_-]{20,}?)/")

logger = logging.getLogger("mightstone")

P = TypeVar("P", bound=Page)
MatcherType = Optional[Callable[[P], bool]]


class EnumCost(str, Enum):
    BUDGET = "budget"
    EXPENSIVE = "expensive"


class EnumColor(str, Enum):
    COLORLESS = "colorless"
    W = "w"
    U = "u"
    B = "b"
    R = "r"
    G = "g"
    MULTICOLOR = "multi"


class EnumIdentity(str, Enum):
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


class MutuallyExclusiveError(ServiceError): ...


class EdhRecApi(MightstoneHttpClient):
    """
    HTTP client for dynamic data hosted at https://edhrec.com/api/
    """

    base_url = "https://edhrec.com"
    timeout = Timeout(timeout=5, read=20)  # Edhrec is rather slow to respond

    async def recommendations_async(
        self, commanders: List[str], cards: List[str]
    ) -> Recommendations:
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
            response = await self.client.post(
                "/api/recs/",
                json={"cards": cards, "commanders": commanders},
            )
            response.raise_for_status()
            data = response.json()

            if data.get("errors"):
                raise ServiceError(
                    message=data.get("errors")[0],
                    data=data,
                    url=response.request.url,
                    status=response.status_code,
                )

            return Recommendations.model_validate(data)

        except HTTPStatusError as e:
            raise ServiceError(
                message="Failed to fetch data from EDHREC",
                url=e.request.url,
                status=e.response.status_code,
            )

    recommendations = synchronize(recommendations_async)

    async def filter_async(self, commander: str, query: FilterQuery) -> PageCommander:
        """
        Read Commander related information, and return an EdhRecCommander object

        :param commander: Commander name or slug
        :param query: An EdhRecFilterQuery object describing the request
        :return: An EdhRecCommander representing answer
        """
        try:
            f = await self.client.get(
                "/api/filters/",
                params={
                    "f": str(query),
                    "dir": "commanders",
                    "cmdr": slugify(commander),
                },
            )
            f.raise_for_status()
            return PageCommander.model_validate(f.json())

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

    This client is faster than ``EdhRecProxiedStatic`` but will not support all
    features since Mightstone failed to reverse engineer some stored information
    on json.edhrec.com
    """

    base_url = "https://json.edhrec.com/pages"

    async def typal_async(self, name, identity: Optional[EnumIdentity] = None):
        """
        Obtain a representation of a typal (previously known as tribe) for example: elves, zombies

        :param name: The name of the typal
        :param identity: Optional, include only cards for a given color identity
        :return: Page representation
        """
        p = f"typal/{slugify(name)}.json"
        if identity:
            p = f"typal/{slugify(name)}/{slugify(identity)}.json"

        return await self.page_async(p, cls=PageTypal)

    typal = synchronize(typal_async)

    async def typals_async(
        self,
    ) -> Page:
        """
        Obtain a representation of all deck typals (previously known as tribes)

        :return: Page representation
        """
        return await self.page_async("typal.json", cls=PageTypals)

    typals = synchronize(typals_async)

    async def typals_stream_async(
        self, matcher: MatcherType = None, start=0, stop=None, step=1, parallel=5
    ) -> AsyncGenerator[PageTypal, None]:
        """
        Streams typal pages as an async generator

        :param matcher: Optional. A matcher function that validates collection item, useful for filtering. Applied after slicing.
        :param start: Optional. An integer number specifying at which position to start the slicing. Default is 0
        :param stop: Optional. An integer number specifying at which position to end the slicing
        :param step: Optional. An integer number specifying the step of the slicing. Default is 1
        :param parallel: Allow X parallel HTTP calls at once
        :return: All matching typal pages
        """
        item: PageTypal
        async for item in self.stream_page_items(
            await self.typals_async(),
            None,
            PageTypal,
            matcher,
            start,
            stop,
            step,
            parallel,
        ):
            yield item

    typals_stream = synchronize(typals_stream_async)

    async def themes_async(
        self,
    ) -> PageThemes:
        """
        Obtain a representation of all deck themes

        :return: Page representation
        """
        return await self.page_async("themes.json", cls=PageThemes)

    themes = synchronize(themes_async)

    async def themes_stream_async(
        self, matcher: MatcherType = None, start=0, stop=None, step=1, parallel=5
    ) -> AsyncGenerator[PageTheme, None]:
        """
        Streams theme pages as an async generator

        :param matcher: Optional. A matcher function that validates collection item, useful for filtering. Applied after slicing.
        :param start: Optional. An integer number specifying at which position to start the slicing. Default is 0
        :param stop: Optional. An integer number specifying at which position to end the slicing
        :param step: Optional. An integer number specifying the step of the slicing. Default is 1
        :param parallel: Allow X parallel HTTP calls at once
        :return: All matching theme pages
        """
        item: PageTheme
        async for item in self.stream_page_items(
            await self.themes_async(),
            None,
            PageTheme,
            matcher,
            start,
            stop,
            step,
            parallel,
        ):
            yield item

    themes_stream = synchronize(themes_stream_async)

    async def theme_async(
        self, name, identity: Optional[EnumIdentity] = None
    ) -> PageTheme:
        """
        Obtain a representation of a deck theme (sacrifice, lifegain...)

        :param name: The name of the theme
        :param identity: Optional, include only cards for a given color identity
        :return: Page representation
        """
        p = f"themes/{slugify(name)}.json"
        if identity:
            p = f"themes/{slugify(name)}/{slugify(identity)}.json"

        return await self.page_async(p, cls=PageTheme)

    theme = synchronize(theme_async)

    async def set_async(self, code) -> PageSet:
        """
        Obtain a representation of cards in a given set

        :param code: The set code (ex: RNA for Ravnica Allegiance)
        :return: Page representation
        """
        return await self.page_async(f"sets/{slugify(code)}.json", cls=PageSet)

    set = synchronize(set_async)

    async def salt_async(self, year: Optional[int] = None) -> PageSalts:
        """
        Obtain a representation of top salt cards by year

        :param year: Optional, the year of the salt
        :return: Page representation
        """
        path = "top/salt.json"
        if year:
            path = f"top/salt/{year}.json"
        return await self.page_async(path, cls=PageSalts)

    salt = synchronize(salt_async)

    async def salt_stream_async(
        self,
        year: Optional[int] = None,
        matcher: MatcherType = None,
        start=0,
        stop=None,
        step=1,
        parallel=5,
    ) -> AsyncGenerator[PageCard, None]:
        """
        Streams salt pages as an async generator

        :param year: Optional. The year to observe
        :param matcher: Optional. A matcher function that validates collection item, useful for filtering. Applied after slicing.
        :param start: Optional. An integer number specifying at which position to start the slicing. Default is 0
        :param stop: Optional. An integer number specifying at which position to end the slicing
        :param step: Optional. An integer number specifying the step of the slicing. Default is 1
        :param parallel: Allow X parallel HTTP calls at once
        :return: All matching theme pages
        """
        item: PageCard
        async for item in self.stream_page_items(
            await self.salt_async(year),
            None,
            PageCard,
            matcher,
            start,
            stop,
            step,
            parallel,
        ):
            yield item

    salt_stream = synchronize(salt_stream_async)

    async def top_cards_async(
        self,
        color: Optional[EnumColor] = None,
        period: Optional[EnumPeriod] = None,
        type: Optional[EnumType] = None,
    ) -> PageTopCards:
        """
        Obtain a representation of a list of card matching one of the following selector:
         * color
         * period
         * type

        :param color: The color of the card (ex: w, u, multi...)
        :param period: The period of observation (week, month, years)
        :param type: The type of card (ex: sorcery, instant...)
        :return: Page representation
        """
        if len([item for item in [color, period, type] if item]) > 1:
            raise MutuallyExclusiveError(
                "period, color and type parameters are mutually exclusives"
            )
        elif period == EnumPeriod.PAST_WEEK:
            path = "top/week.json"
        elif period == EnumPeriod.PAST_MONTH:
            path = "top/month.json"
        elif period == EnumPeriod.PAST_2YEAR:
            path = "top/year.json"
        elif type:
            path = f"top/{type.value}.json"
        elif color:
            path = f"top/{color.value}.json"
        else:
            path = "top/week.json"

        return await self.page_async(path, cls=PageTopCards)

    top_cards = synchronize(top_cards_async)

    async def top_cards_stream_async(
        self,
        color: Optional[EnumColor] = None,
        period: Optional[EnumPeriod] = EnumPeriod.PAST_WEEK,
        type: Optional[EnumType] = None,
        matcher: MatcherType = None,
        start=0,
        stop=None,
        step=1,
        parallel=5,
    ) -> AsyncGenerator[PageCard, None]:
        """
        Streams salt pages as an async generator

        :param color: The color of the card (ex: w, u, multi...)
        :param period: The period of observation (week, month, years)
        :param type: The type of card (ex: sorcery, instant...)
        :param matcher: Optional. A matcher function that validates collection item, useful for filtering. Applied after slicing.
        :param start: Optional. An integer number specifying at which position to start the slicing. Default is 0
        :param stop: Optional. An integer number specifying at which position to end the slicing
        :param step: Optional. An integer number specifying the step of the slicing. Default is 1
        :param parallel: Allow X parallel HTTP calls at once
        :return: All matching theme pages
        """
        item: PageCard
        async for item in self.stream_page_items(
            await self.top_cards_async(color, period, type),
            None,
            PageCard,
            matcher,
            start,
            stop,
            step,
            parallel,
        ):
            yield item

    top_cards_stream = synchronize(top_cards_stream_async)

    async def companions_async(self) -> PageCompanions:
        """
        Obtain a list of companions

        :return: Page representation
        """
        return await self.page_async("companions.json", cls=PageCompanions)

    companions = synchronize(companions_async)

    async def companion_async(self, name: str) -> PageTheme:
        """
        Obtain a complete representation of a card as a deck companion
        EDHREC describes a companion as a theme.

        Use ``card_async``, ``commander_async``, ``background_async``, ``partner_async`` for deck card, commander, background and partner context.

        :param name: The card name

        :return: Page representation
        """
        slug = slugify(name).split("-", 1)[0]
        return await self.page_async(
            f"/themes/{slug}-companion.json",
            cls=PageTheme,
        )

    companion = synchronize(companion_async)

    async def companions_stream_async(
        self,
        matcher: MatcherType = None,
        start=0,
        stop=None,
        step=1,
        parallel=5,
    ) -> AsyncGenerator[PageTheme, None]:
        """
        Streams companion pages as an async generator

        :param matcher: Optional. A matcher function that validates collection item, useful for filtering. Applied after slicing.
        :param start: Optional. An integer number specifying at which position to start the slicing. Default is 0
        :param stop: Optional. An integer number specifying at which position to end the slicing
        :param step: Optional. An integer number specifying the step of the slicing. Default is 1
        :param parallel: Allow X parallel HTTP calls at once
        :return: All matching theme pages
        """
        item: PageTheme
        async for item in self.stream_page_items(
            await self.companions_async(),
            None,
            PageTheme,
            matcher,
            start,
            stop,
            step,
            parallel,
        ):
            yield item

    companions_stream = synchronize(companions_stream_async)

    async def partners_async(
        self,
    ) -> PagePartners:
        """
        Obtain a list of partners

        :return: Page representation
        """
        return await self.page_async("partners.json", cls=PagePartners)

    partners = synchronize(partners_async)

    async def partner_async(
        self,
        name: str,
    ) -> PagePartner:
        """
        Obtain a complete representation of a card as a deck partner

        Use ``card_async``, ``commander_async``, ``background_async`` for deck card, commander and background context.
        Companions are described as a theme, and provided with ``companion_async``

        :param name: The card name

        :return: Page representation
        """
        return await self.page_async(f"partners/{slugify(name)}.json", cls=PagePartner)

    partner = synchronize(partners_async)

    async def partners_stream_async(
        self,
        collection: Optional[str] = None,
        matcher: MatcherType = None,
        start=0,
        stop=None,
        step=1,
        parallel=5,
    ) -> AsyncGenerator[PagePartner, None]:
        """
        Streams partners pages as an async generator

        :param collection: Optional. Use the named collection. Either: ``Doctors`, ``Friends Forever`` or ``Partners``
        :param matcher: Optional. A matcher function that validates collection item, useful for filtering. Applied after slicing.
        :param start: Optional. An integer number specifying at which position to start the slicing. Default is 0
        :param stop: Optional. An integer number specifying at which position to end the slicing
        :param step: Optional. An integer number specifying the step of the slicing. Default is 1
        :param parallel: Allow X parallel HTTP calls at once
        :return: All matching theme pages
        """
        item: PagePartner
        async for item in self.stream_page_items(
            await self.partners_async(),
            collection,
            PagePartner,
            matcher,
            start,
            stop,
            step,
            parallel,
        ):
            yield item

    async def commanders_async(
        self,
        identity: Optional[EnumIdentity] = None,
        period: Optional[EnumPeriod] = None,
    ) -> PageCommanders:
        """
        Obtain a list of commanders for a period or a color identity.

        :param period: The period observed (last week, last month, last 2 years)
        :param identity: The color identity of the commanders
        :return: Page representation
        """
        if period and identity:
            raise MutuallyExclusiveError(
                "period and identity parameters are mutually exclusives"
            )
        elif period == EnumPeriod.PAST_WEEK:
            path = "commanders/week.json"
        elif period == EnumPeriod.PAST_MONTH:
            path = "commanders/month.json"
        elif period == EnumPeriod.PAST_2YEAR:
            path = "commanders/year.json"
        elif identity:
            path = f"commanders/{identity.value}.json"
        else:
            path = "commanders/week.json"

        return await self.page_async(path, cls=PageCommanders)

    commanders = synchronize(commanders_async)

    async def commander_async(
        self,
        name: str,
        background: Optional[str] = None,
        partner: Optional[str] = None,
        subtype: Optional[str] = None,
        cost: Optional[EnumCost] = None,
    ) -> PageCommander:
        """
        Obtain a complete representation of a card as a deck commander

        Use ``card_async``, ``partner_async``, ``background_async`` for deck card, partner and background context.
        Companions are described as a theme, and provided with ``companion_async``

        :param name: The card name
        :param background: Optional, specify a background as partner (ex: ``Raised by Giants``)
        :param partner: Optional, specify a partner  (ex: ``Rograkh, Son of Rohgahh``)
        :param subtype: Optional, filter by theme or typal (ex: ``elves``, ``sacrifice``)
        :param cost: Optional, the price range of the deck
        :return: Page representation
        """
        if background is None and partner is not None:
            raise MutuallyExclusiveError(
                "background and partner parameters are mutually exclusives"
            )
        elif background:
            name = " ".join(sorted([name, background]))
        elif partner:
            name = " ".join(sorted([name, partner]))

        slug = slugify(name)
        path = f"commanders/{slug}.json"
        if subtype and cost:
            path = f"commanders/{slug}/{slugify(subtype)}/{cost.value}.json"

        elif subtype:
            path = f"commanders/{slug}/{slugify(subtype)}.json"
        elif cost:
            path = f"commanders/{slug}/{cost.value}.json"

        return await self.page_async(path, cls=PageCommander)

    commander = synchronize(commander_async)

    async def commanders_stream_async(
        self,
        identity: Optional[EnumIdentity] = None,
        period: Optional[EnumPeriod] = EnumPeriod.PAST_WEEK,
        matcher: MatcherType = None,
        start=0,
        stop=None,
        step=1,
        parallel=5,
    ) -> AsyncGenerator[PageCommander, None]:
        """
        Streams commanders pages as an async generator

        :param period: The period observed (last week, last month, last 2 years)
        :param identity: The color identity of the commanders
        :param matcher: Optional. A matcher function that validates collection item, useful for filtering. Applied after slicing.
        :param start: Optional. An integer number specifying at which position to start the slicing. Default is 0
        :param stop: Optional. An integer number specifying at which position to end the slicing
        :param step: Optional. An integer number specifying the step of the slicing. Default is 1
        :param parallel: Allow X parallel HTTP calls at once
        :return: All matching commander pages
        """
        item: PageCommander
        async for item in self.stream_page_items(
            await self.commanders_async(identity, period),
            None,
            PageCommander,
            matcher,
            start,
            stop,
            step,
            parallel,
        ):
            yield item

    commanders_stream = synchronize(commanders_stream_async)

    async def combos_async(self, identity: Optional[EnumIdentity] = None) -> PageCombos:
        """
        Obtain a representation of a list of combos for a given color

        :param identity: The color identity of the combos
        :return: Page representation
        """
        path = "combos.json"
        if identity:
            path = f"combos/{identity.value}.json"
        return await self.page_async(path, cls=PageCombos)

    combos = synchronize(combos_async)

    async def combo_async(
        self,
        combo_id: str,
        identity: EnumIdentity,
    ) -> PageCombo:
        """
        Obtain a representation of a combo (recursive behavior that can win a game).
        Is requires both color identity and unique identifier due to API limitation

        :param combo_id: The combo unique id (ex: ``1478-3293``)
        :param identity: The color identity of the combo
        :return: Page representation
        """
        return await self.page_async(
            f"combos/{identity.value}/{combo_id}.json",
            cls=PageCombo,
        )

    combo = synchronize(combo_async)

    async def combos_stream_async(
        self,
        identity: Optional[EnumIdentity] = None,
        matcher: MatcherType = None,
        start=0,
        stop=None,
        step=1,
        parallel=5,
    ) -> AsyncGenerator[PageCombo, None]:
        """
        Streams commanders pages as an async generator

        :param identity: The color identity of the commanders
        :param matcher: Optional. A matcher function that validates collection item, useful for filtering. Applied after slicing.
        :param start: Optional. An integer number specifying at which position to start the slicing. Default is 0
        :param stop: Optional. An integer number specifying at which position to end the slicing
        :param step: Optional. An integer number specifying the step of the slicing. Default is 1
        :param parallel: Allow X parallel HTTP calls at once
        :return: All matching commander pages
        """
        item: PageCombo
        async for item in self.stream_page_items(
            await self.combos_async(identity),
            None,
            PageCombo,
            matcher,
            start,
            stop,
            step,
            parallel,
        ):
            yield item

    combos_stream = synchronize(combos_stream_async)

    async def backgrounds_async(self) -> PageBackgrounds:
        """
        Obtain a representation of all background cards.

        :return: Page representation
        """
        return await self.page_async("backgrounds.json", cls=PageBackgrounds)

    backgrounds = synchronize(backgrounds_async)

    async def background_async(self, name: str) -> PageBackground:
        """
        Obtain a representation of a background card

        :param name: The card name
        :return: Page representation
        """
        return await self.page_async(
            f"backgrounds/{slugify(name)}.json",
            cls=PageBackground,
        )

    background = synchronize(background_async)

    async def backgrounds_stream_async(
        self,
        collection: Optional[str] = None,
        matcher: MatcherType = None,
        start=0,
        stop=None,
        step=1,
        parallel=5,
    ) -> AsyncGenerator[PageTypal, None]:
        """
        Streams backgrounds pages as an async generator

        :param collection: Optional. Use the named collection. Either: ``Commanders`` or ``Backgrounds``
        :param matcher: Optional. A matcher function that validates collection item, useful for filtering. Applied after slicing.
        :param start: Optional. An integer number specifying at which position to start the slicing. Default is 0
        :param stop: Optional. An integer number specifying at which position to end the slicing
        :param step: Optional. An integer number specifying the step of the slicing. Default is 1
        :param parallel: Allow X parallel HTTP calls at once
        :return: All matching commander pages
        """
        item: PageBackground
        async for item in self.stream_page_items(
            await self.backgrounds_async(),
            collection,
            PageBackground,
            matcher,
            start,
            stop,
            step,
            parallel,
        ):
            yield item

    backgrounds_stream = synchronize(backgrounds_stream_async)

    async def average_deck_async(
        self,
        commander,
        theme: Optional[str] = None,
        cost: Optional[EnumCost] = None,
    ) -> PageAverageDeck:
        """
        Obtain a representation of an average deck for a given commander.
        Optionally, filter result by a price range (cheap or expansive)

        :param commander: The commander name
        :param theme: Optional, the theme or tribe (ex: elves, sacrifice)
        :param cost: Optional, the price range of the deck
        :return: Page representation
        """
        if theme and cost:
            p = f"average-decks/{slugify(commander)}/{slugify(theme)}/{cost.value}.json"
        elif theme:
            p = f"average-decks/{slugify(commander)}/{slugify(theme)}.json"
        elif cost:
            p = f"average-decks/{slugify(commander)}/{cost.value}.json"
        else:
            p = f"average-decks/{slugify(commander)}.json"

        return await self.page_async(p, cls=PageAverageDeck)

    average_deck = synchronize(average_deck_async)

    async def decks_async(
        self,
        commander,
        theme: Optional[str] = None,
        cost: Optional[EnumCost] = None,
    ) -> PageDecks:
        """
        Obtain a list of decks references for a given commander
        Optionally, filter result by a price range (cheap or expansive)

        :param commander: The commander name
        :param theme: Optional, the theme or tribe (ex: elves, sacrifice)
        :param cost: Optional, the price range of the deck
        :return: Page representation
        """
        if theme and cost:
            p = f"decks/{slugify(commander)}/{slugify(theme)}/{cost.value}.json"
        elif theme:
            p = f"decks/{slugify(commander)}/{slugify(theme)}.json"
        elif cost:
            p = f"decks/{slugify(commander)}/{cost.value}.json"
        else:
            p = f"decks/{slugify(commander)}.json"

        return await self.page_async(p, cls=PageDecks)

    decks = synchronize(decks_async)

    async def staples_async(self, identity: EnumIdentity) -> PageStaples:
        """
        Obtain a list of staple card references for a color identity

        :param identity: The color identity
        :return: Page representation
        """
        path = f"commanders/{identity.value}/staples.json"

        return await self.page_async(path, cls=PageStaples)

    staples = synchronize(staples_async)

    async def staples_stream_async(
        self,
        identity: EnumIdentity,
        matcher: MatcherType = None,
        start=0,
        stop=None,
        step=1,
        parallel=5,
    ) -> AsyncGenerator[PageCard, None]:
        """
        Streams staples pages as an async generator

        :param identity: The color identity
        :param matcher: Optional. A matcher function that validates collection item, useful for filtering. Applied after slicing.
        :param start: Optional. An integer number specifying at which position to start the slicing. Default is 0
        :param stop: Optional. An integer number specifying at which position to end the slicing
        :param step: Optional. An integer number specifying the step of the slicing. Default is 1
        :param parallel: Allow X parallel HTTP calls at once
        :return: All matching staple pages
        """
        item: PageCard
        async for item in self.stream_page_items(
            await self.staples_async(identity),
            None,
            PageCard,
            matcher,
            start,
            stop,
            step,
            parallel,
        ):
            yield item

    staples_stream = synchronize(staples_stream_async)

    async def mana_staples_async(self, identity: EnumIdentity):
        """
        Obtain a list of staple mana card references for a color identity

        :param identity: The color identity
        :return: Page representation
        """
        path = f"commanders/{identity.value}/mana-staples.json"

        return await self.page_async(path, cls=PageStaples)

    mana_staples = synchronize(mana_staples_async)

    async def mana_staples_stream_async(
        self,
        identity: EnumIdentity,
        matcher: MatcherType = None,
        start=0,
        stop=None,
        step=1,
        parallel=5,
    ) -> AsyncGenerator[PageCard, None]:
        """
        Streams staples pages as an async generator

        :param identity: The color identity
        :param matcher: Optional. A matcher function that validates collection item, useful for filtering. Applied after slicing.
        :param start: Optional. An integer number specifying at which position to start the slicing. Default is 0
        :param stop: Optional. An integer number specifying at which position to end the slicing
        :param step: Optional. An integer number specifying the step of the slicing. Default is 1
        :param parallel: Allow X parallel HTTP calls at once
        :return: All matching staple pages
        """
        item: PageCard
        async for item in self.stream_page_items(
            await self.mana_staples_async(identity),
            None,
            PageCard,
            matcher,
            start,
            stop,
            step,
            parallel,
        ):
            yield item

    mana_staples_stream = synchronize(mana_staples_stream_async)

    async def card_async(self, name: str):
        """
        Obtain a complete representation of a card as a deck member

        Use ``commander_async``, ``partner_async``, ``background_async`` for commander, partner and background context.
        Companions are described as a theme, and provided with ``companion_async``

        :param name: The card name
        :return: Page representation
        """
        path = f"card/{slugify(name)}.json"

        return await self.page_async(path, cls=PageCard)

    card = synchronize(card_async)

    async def _get_raw_static_page(self, path: str) -> dict:
        try:
            f = await self.client.get(path)
            f.raise_for_status()
            return f.json()
        except HTTPStatusError as e:
            raise ServiceError(
                message="Failed to fetch data from EDHREC",
                url=e.request.url,
                status=e.response.status_code,
            )

    async def page_async(
        self,
        path: str,
        cls: Type[P],
    ) -> P:
        """
        :param cls: The class to use (must extend EdhRecPage)
        :param path: The page path
        :return: A page instance with un-paginated items
        """
        return cls.model_validate(await self._get_raw_static_page(path))

    page = synchronize(page_async)

    async def stream_page_items(
        self,
        page: Page,
        collection: Optional[str] = None,
        cls=Type[P],
        matcher=Type[MatcherType],
        start=0,
        stop=None,
        step=1,
        parallel=5,
    ) -> AsyncGenerator[P, None]:
        """
        An async generator that return each item from a page as a page (for instance each ``PageCommander`` from a ``PageCommanders``)

        ``start``, ``stop``, ``step`` parameters works as a standard python slice.
        ``matcher`` function is applied after slicing through ``start``, ``stop``, ``step`` parameters

        :param page: The page to scan
        :param collection: Use the named collection located in ``page.container.iterable.collections`` instead of ``page.items``
        :param cls: The collection item type (must inherit from ``Page``)
        :param matcher: Optional. A matcher function that validates collection item, useful for filtering
        :param start: Optional. An integer number specifying at which position to start the slicing. Default is 0
        :param stop: Optional. An integer number specifying at which position to end the slicing
        :param step: Optional. An integer number specifying the step of the slicing. Default is 1
        :param parallel: Allow X parallel HTTP calls at once
        :return: An async generator of `item_class`
        """
        if not page.items:
            return

        if collection is not None:
            iterable = islice(
                self._unpaginate_cardviews(page.get_collection(collection)),
                start,
                stop,
                step,
            )
        else:
            iterable = islice(page.items, start, stop, step)

        while chunk := [item async for item in islice(iterable, parallel)]:
            for coro in asyncio.as_completed(
                [self.page_async(f"{item.url}.json", cls=cls) for item in chunk]
            ):
                result = await coro
                if matcher is None or matcher(result):
                    yield result

    async def _unpaginate_cardviews(
        self, collection: Collection
    ) -> AsyncGenerator[Union[CollectionItem, DeckItem], None]:
        for item in collection.items:
            yield item

        while collection.more:
            collection = Collection.model_validate(
                await self._get_raw_static_page(
                    f"https://json.edhrec.com/pages/{collection.more}"
                )
            )
            for item in collection.items:
                yield item


class EdhRecProxiedStatic(EdhRecStatic):
    """
    HTTP client for static JSON data hosted at https://edhrec.com/_next/data

    Please prefer the ``EdhRecStatic`` instead if you need better performances and don’t need to scrap individual decks
    """

    @property
    def base_url(self):
        return f"https://edhrec.com/_next/data/{self._get_proxy_instance()}"

    async def deck_async(self, deck_id: str) -> PageDeck:
        # Path on json.edhrec.com is unknown yet
        return await self.page_async(
            f"/deckpreview/{deck_id}.json",
            cls=PageDeck,
        )

    deck = synchronize(deck_async)

    async def decks_stream_async(
        self,
        commander,
        theme: Optional[str] = None,
        cost: Optional[EnumCost] = None,
        matcher: MatcherType = None,
        start=0,
        stop=None,
        step=1,
        parallel=5,
    ) -> AsyncGenerator[PageTypal, None]:
        """
        Streams backgrounds pages as an async generator

        :param commander: The commander name
        :param theme: Optional, the theme or tribe (ex: elves, sacrifice)
        :param cost: Optional, the price range of the deck
        :param matcher: Optional. A matcher function that validates collection item, useful for filtering. Applied after slicing.
        :param start: Optional. An integer number specifying at which position to start the slicing. Default is 0
        :param stop: Optional. An integer number specifying at which position to end the slicing
        :param step: Optional. An integer number specifying the step of the slicing. Default is 1
        :param parallel: Allow X parallel HTTP calls at once
        :return: All matching commander pages
        """
        item: PageCard
        async for item in self.stream_page_items(
            await self.decks_async(commander, theme, cost),
            None,
            PageCard,
            matcher,
            start,
            stop,
            step,
            parallel,
        ):
            yield item

    decks_stream = synchronize(decks_stream_async)

    async def _get_raw_static_page(self, path: str) -> dict:
        payload = await super()._get_raw_static_page(path)
        if path.startswith("https://json.edhrec.com"):
            return payload
        return payload.get("pageProps", {}).get("data", {})

    @lru_cache(maxsize=1)
    def _get_proxy_instance(self) -> Optional[str]:
        res = Client().get("https://edhrec.com")
        match = PROXY_INSTANCE_RE.search(res.text)
        if not match:
            return None
        return match.group("instance")

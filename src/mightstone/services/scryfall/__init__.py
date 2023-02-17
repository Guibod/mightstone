"""
Scryfall.com support classes
"""

from typing import Any, List, Union

import ijson
from aiohttp import ClientResponseError
from pydantic.error_wrappers import ValidationError
from typing_extensions import AsyncGenerator, TypeVar

from mightstone.services import MightstoneHttpClient, ServiceError
from mightstone.services.scryfall.models import (
    BulkTagType,
    Card,
    CardIdentifierPath,
    Catalog,
    CatalogType,
    DirectionStrategy,
    Error,
    IdentifierCollectorNumberSet,
    IdentifierId,
    IdentifierIllustrationId,
    IdentifierMtgId,
    IdentifierMultiverseId,
    IdentifierName,
    IdentifierNameSet,
    IdentifierOracleId,
    ManaCost,
    Migration,
    Ruling,
    RulingIdentifierPath,
    ScryfallList,
    Set,
    SortStrategy,
    Symbol,
    Tag,
    UniqueStrategy,
)

T = TypeVar("T")


class Scryfall(MightstoneHttpClient):
    """
    Scryfall API client
    """

    base_url = "https://api.scryfall.com"

    async def get_bulk_tags(self, tag_type: BulkTagType) -> AsyncGenerator[Tag, None]:
        """
        Access the private tag repository

        This is an alpha feature, and could be removed later.
        :param tag_type: The tag type either oracle or illustration
        :return: A scryfall `Tag` instance async generator
        """
        tag_type = BulkTagType(tag_type)
        async with self.session.get(f"/private/tags/{tag_type}") as f:
            f.raise_for_status()
            async for current_tag in ijson.items_async(f.content, "data.item"):
                yield Tag.parse_obj(current_tag)

    async def get_bulk_data(self, bulk_type: str) -> AsyncGenerator[Card, None]:
        """
        Access the bulk cards
        This script uses ijson and should stream data on the fly

        See https://scryfall.com/docs/api/bulk-data for more informations
        :param bulk_type: A string describing the bulk export name
        :return:
        """
        bulk_types = []
        bulk = None
        async with self.session.get("/bulk-data") as f:
            f.raise_for_status()
            async for current_bulk in ijson.items_async(f.content, "data.item"):
                bulk_types.append(current_bulk.get("type"))
                if current_bulk.get("type") == bulk_type:
                    bulk = current_bulk

        if not bulk:
            raise IndexError(f"{bulk_type} bulk type not found in {bulk_types}")

        async with self.session.get(bulk.get("download_uri")) as f:
            f.raise_for_status()
            async for current_card in ijson.items_async(f.content, "item"):
                yield Card.parse_obj(current_card)

    async def card(
        self, id: str, type: CardIdentifierPath = CardIdentifierPath.SCRYFALL
    ) -> Card:
        """
        Returns a single card with a given ID, or by its code set / collector number

        Depending on the `type` value, one of the following endpoint will be reached:
         * /cards/:id
         * /cards/tcgplayer/:id
         * /cards/multiverse/:id
         * /cards/mtgo/:id
         * /cards/arena/:id
         * /cards/cardmarket/:id
         * /cards/:code/:number

        :param id: The requested `Card` identifier string, for code-number, please
        use / as separator (dmu/123) :param type: The card identifier, please refer
        to `CardIdentifierPath` enum :return A scryfall `Card` instance
        """
        type = CardIdentifierPath(type)
        path = f"/cards/{id}"
        if type.value and type != CardIdentifierPath.CODE_NUMBER:
            path = f"/cards/{type.value}/{id}"
        return await self._get_item(path, Card)

    async def random(self, q: str = None) -> Card:
        """
        Returns a single random Card object.

        This method will use:
        - /cards/random

        :param q: The optional parameter q supports the same fulltext search system
        that the main site uses. Providing q will filter the pool of cards before
        returning a random entry. :return A scryfall `Card` instance
        """
        params = {}
        if q:
            params["q"] = q
        return await self._get_item("/cards/random", Card, params=params)

    async def search(
        self,
        q: str,
        unique: UniqueStrategy = UniqueStrategy.CARDS,
        order: SortStrategy = SortStrategy.NAME,
        dir: DirectionStrategy = DirectionStrategy.AUTO,
        include_extras=False,
        include_multilingual=False,
        include_variations=False,
        limit: int = 100,
    ) -> AsyncGenerator[Card, None]:
        """
        Returns a List object containing Cards found using a fulltext search string.
        This string supports the same fulltext search system that the main site uses.

        :param unique: The strategy for omitting similar cards.
        :param order: The method to sort returned cards.
        :param dir: The direction to sort cards.
        :param include_extras: If true, extra cards (tokens, planes, etc) will be
               included. Equivalent to adding include:extras to the fulltext search.
        :param include_multilingual: If true, cards in every language supported by
               Scryfall will be included.
        :param include_variations: If true, rare care variants will be included,
        like the Hairy Runesword.
        :param q: A fulltext search query.
        :param limit: The number of item to return, please note that Mightstone
        wraps Scryfall pagination and streams the results
        :return A scryfall `Card` instance async generator
        """
        params = {
            "unique": UniqueStrategy(unique).value,
            "order": SortStrategy(order).value,
            "dir": DirectionStrategy(dir).value,
            "include_extras": str(include_extras),
            "include_multilingual": str(include_multilingual),
            "include_variations": str(include_variations),
            "q": q,
        }
        async for item in self._list(
            "/cards/search", params=params, model=Card, limit=limit
        ):
            yield item

    async def named(self, q: str, set: str = None, exact=True):
        """
        Returns a Card based on a name search string. This method is designed for
        building chat bots, forum bots, and other services that need card details
        quickly.

        If exact mode is on, a card with that exact name is returned. Otherwise,
        an Exception is raised because no card matches. If exact mode is off and a
        card name matches that string, then that card is returned. If not, a fuzzy
        search is executed for your card name. The server allows misspellings and
        partial words to be provided. For example: jac bele will match Jace Beleren.
        When fuzzy searching, a card is returned if the server is confident that you
        unambiguously identified a unique name with your string. Otherwise,
        an exception will be raised describing the problem: either more than 1 one
        card matched your search, or zero cards matched.

        Card names are case-insensitive and punctuation is optional (you can drop
        apostrophes and periods etc). For example: fIReBALL is the same as Fireball
        and smugglers copter is the same as Smuggler's Copter.

        :param q: The searched card name :param exact: Run a strict text research
        instead of a fuzzy search :param set: You may also provide a set code in the
        set parameter, in which case the name search and the returned card print will
        be limited to the specified set. :return A scryfall `Card` instance
        """
        params = {}
        if exact:
            params["exact"] = q
        else:
            params["fuzzy"] = q
        if set:
            params["set"] = set
        return await self._get_item("/cards/named", Card, params=params)

    async def autocomplete(self, q: str, include_extras=False):
        """
        Returns a Catalog object containing up to 20 full English card names that
        could be autocompletions of the given string parameter.

        This method is designed for creating assistive UI elements that allow users
        to free-type card names.
        The names are sorted with the nearest match first, highly favoring results
        that begin with your given string.

        Spaces, punctuation, and capitalization are ignored.

        If q is less than 2 characters long, or if no names match, the Catalog will
        contain 0 items (instead of returning any errors).

        :param q: The string to autocomplete.
        :param include_extras: If true, extra cards (tokens, planes, vanguards, etc)
               will be included.
        :return: A scryfall `Card` instance async generator
        """
        params = {"q": q}
        if include_extras:
            params["include_extras"] = include_extras
        return await self._get_item("/cards/autocomplete", Catalog, params=params)

    async def collection(
        self,
        identifiers: List[
            Union[
                IdentifierId,
                IdentifierName,
                IdentifierNameSet,
                IdentifierMtgId,
                IdentifierOracleId,
                IdentifierMultiverseId,
                IdentifierCollectorNumberSet,
                IdentifierIllustrationId,
            ]
        ],
    ):
        """
        Accepts a JSON array of card identifiers, and returns a List object with the
        collection of requested cards. A maximum of 75 card references may be
        submitted per request.

        :param identifiers: Each submitted card identifier must be a JSON object with
        one or more of the keys id, mtgo_id, multiverse_id, oracle_id,
        illustration_id, name, set, and collector_number :return: A scryfall `Card`
        instance async generator
        """
        async for item in self._list(
            "/cards/collection", Card, verb="POST", json={"identifiers": identifiers}
        ):
            yield item

    async def rulings(
        self,
        id: str,
        type: RulingIdentifierPath = RulingIdentifierPath.SCRYFALL,
        limit: int = None,
    ):
        """
        Returns a single card with the given ID.

        Depending on the `type` value, one of the following endpoint will be reached:
         * /cards/:id/rulings
         * /cards/multiverse/:id/rulings
         * /cards/mtgo/:id/rulings
         * /cards/arena/:id/rulings

        :param id: The requested `Card` identifier string. In the case of card-number,
        use set/number (separated by a slash, for instance dmu/123)
        :param type: The card identifier, please refer to `RulingIdentifierPath` enum
        :return A scryfall `Ruling` instance async generator
        """
        type = RulingIdentifierPath(type)
        path = f"/cards/{id}/rulings"
        if type.value and type != RulingIdentifierPath.CODE_NUMBER:
            path = f"/cards/{type.value}/{id}/rulings"

        async for item in self._list(path, Ruling, limit=limit):
            yield item

    async def symbols(self, limit: int = None):
        """
        Returns a List of all Card Symbols.

        :param limit: The number of item to return, please note that Mightstone
        wraps Scryfall pagination and streams the results
        :return: A scryfall `Symbol` instance async generator
        """
        async for item in self._list("/symbology", Symbol, limit=limit):
            yield item

    async def parse_mana(self, cost: str):
        """
        Parses the given mana cost parameter and returns Scryfall’s interpretation.

        The server understands most community shorthand for mana costs (such as 2WW
        for {2}{W}{W}). Symbols can also be out of order, lowercase, or have multiple
        colorless costs (such as 2{g}2 for {4}{G}).

        If part of the string could not be understood, the server will raise an Error
        object describing the problem.

        :return: A `ManaCost` instance
        """
        return await self._get_item(
            "/symbology/parse-mana", ManaCost, params={"cost": cost}
        )

    async def catalog(self, type: CatalogType):
        """
        A Catalog object contains an array of Magic datapoints (words, card values,
        etc). Catalog objects are provided by the API as aids for building other
        Magic software and understanding possible values for a field on Card objects.

        :param type: See `CatalogType` for more informations
        :return: A `Catalog` instance
        """
        type = CatalogType(type)
        return await self._get_item(f"/catalog/{type.value}", Catalog)

    async def migrations(self, limit: int = None):
        """
        For the vast majority of Scryfall’s database, Magic card entries are additive.
        We add new and upcoming cards as we learn about them and obtain images.

        In rare instances, Scryfall may discover that a card in our database does not
        really exist, or it has been deleted from a digital game permanently. In
        these situations, we provide endpoints to help you reconcile downstream data
        you may have synced or imported from Scryfall.

        Each migration has a provided migration_strategy:

        merge
        You should update your records to replace the given old Scryfall ID with the
        new ID. The old ID is being discarded, and an existing record should be
        used to replace all instances of it.

        delete
        The given UUID is being discarded, and no replacement data is being provided.
        This likely means the old records are fully invalid. This migration exists to
        provide evidence that cards were removed from Scryfall’s database.

        :param limit: The number of item to return, please note that Mightstone wraps
        Scryfall pagination and streams the results
        :return: A `Migration` instance async generator
        """
        async for item in self._list("/migrations", Migration, limit=limit):
            yield item

    async def migration(self, id: str):
        """
        Returns a single Card Migration with the given :id

        :return: A `Migration` instance
        """
        return await self._get_item(f"/migrations/{id}", Migration)

    async def sets(self, limit: int = None):
        """
        Returns a List object of all Sets on Scryfall.

        :param limit: The number of item to return, please note that Mightstone
        wraps Scryfall pagination and streams the results
        :return: A `Set` instance async generator
        """
        async for item in self._list("/sets", Set, limit=limit):
            yield item

    async def set(self, id_or_code: str = None) -> Set:
        """
        Returns a Set with the given set code.

        :param id_or_code: The code can be either the code or the mtgo_code or the
        scryfall UUID for the set.
        :return: A `Set` instance
        """
        return await self._get_item(f"/sets/{id_or_code}", Set)

    async def _get_item(self, path, model: T = None, **kwargs) -> Union[T, Any]:
        try:
            async with self.session.get(path, **kwargs) as f:
                if not f.ok:
                    error = Error.parse_obj(await f.json())
                    raise ServiceError(
                        message=error.details,
                        method=f.method,
                        url=f.real_url,
                        status=f.status,
                        data=error,
                    )
                data = await f.json()
                if model:
                    data = model.parse_obj(data)
                return data
        except ValidationError as e:
            raise ServiceError(
                message=f"Failed to validate {model} data, {e.errors()}",
                url=path,
                method="GET",
                status=None,
                data=e,
            )
        except ClientResponseError as e:
            raise ServiceError(
                message="Failed to fetch data from Scryfall",
                url=e.request_info.real_url,
                method=e.request_info.method,
                status=e.status,
                data=Error.parse_raw(e.message),
            )

    async def _list(
        self, path, model: T = None, verb="GET", limit=None, **kwargs
    ) -> AsyncGenerator[T, None]:
        i = 0
        try:
            while True:
                if verb == "POST":
                    context = self.session.post(path, **kwargs)
                else:
                    context = self.session.get(path, **kwargs)

                async with context as f:
                    if not f.ok:
                        raise ServiceError(
                            message="Failed to fetch data from Scryfall",
                            url=f.real_url,
                            status=f.status,
                            data=Error.parse_obj(await f.json()),
                        )

                    my_list = ScryfallList.parse_obj(await f.json())
                    for item in my_list.data:
                        if limit and i >= limit:
                            return
                        i += 1

                        if model:
                            yield model.parse_obj(item)
                        else:
                            yield item

                if not my_list.has_more:
                    return

                path = my_list.next_page.path + "?" + my_list.next_page.query
                await self._sleep()
        except ValidationError as e:
            raise ServiceError(
                message=f"Failed to validate {model} data for item #{i}, {e.errors()}",
                url=path,
                status=None,
                data=e,
            )
        except ClientResponseError as e:
            raise ServiceError(
                message="Failed to fetch data from Scryfall",
                url=e.request_info.real_url,
                status=e.status,
                data=Error.parse_obj(e),
            )

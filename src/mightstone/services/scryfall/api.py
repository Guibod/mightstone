"""
Scryfall.com support classes
"""

from typing import Dict, List, Optional, TypeVar, Union, cast

import ijson
from httpx import HTTPStatusError
from pydantic import ValidationError
from pydantic.networks import AnyUrl
from typing_extensions import AsyncGenerator, Type, overload

from mightstone.ass import compressor, sync_generator, synchronize
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
    ScryfallModel,
    Set,
    SortStrategy,
    Symbol,
    Tag,
    UniqueStrategy,
)

_T = TypeVar("_T", bound=ScryfallModel)


class Scryfall(MightstoneHttpClient):
    """
    Scryfall API client
    """

    base_url = "https://api.scryfall.com"

    async def get_bulk_tags_async(
        self, tag_type: BulkTagType
    ) -> AsyncGenerator[Tag, None]:
        """
        Access the private tag repository

        This is an alpha feature, and could be removed later.

        :param tag_type: The tag type either oracle or illustration
        :return: A scryfall `Tag` instance async generator
        """
        async with self.client.stream("GET", f"/private/tags/{tag_type.value}") as f:
            f.raise_for_status()
            async for current_tag in ijson.items_async(
                compressor.open(f.aiter_bytes()), "data.item"
            ):
                yield Tag.model_validate(current_tag)

    get_bulk_tags = sync_generator(get_bulk_tags_async)

    async def get_bulk_data_async(self, bulk_type: str) -> AsyncGenerator[Card, None]:
        """
        Access the bulk cards
        This script uses ijson and should stream data on the fly

        See https://scryfall.com/docs/api/bulk-data for more informations

        :param bulk_type: A string describing the bulk export name
        :return: An async iterator of ``Card``
        """
        bulk_types = []
        bulk = None
        async with self.client.stream("GET", "/bulk-data") as f:
            f.raise_for_status()

            async for current_bulk in ijson.items_async(
                compressor.open(f.aiter_bytes()), "data.item"
            ):
                bulk_types.append(current_bulk.get("type"))
                if current_bulk.get("type") == bulk_type:
                    bulk = current_bulk

        if not bulk:
            raise IndexError(f"{bulk_type} bulk type not found in {bulk_types}")

        async with self.client.stream("GET", bulk.get("download_uri")) as f:
            f.raise_for_status()
            async for current_card in ijson.items_async(
                compressor.open(f.aiter_bytes()), "item"
            ):
                yield Card.model_validate(current_card)

    get_bulk_data = sync_generator(get_bulk_data_async)

    async def card_async(
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
                   use / as separator (dmu/123)
        :param type: The card identifier, please refer to `CardIdentifierPath` enum
        :param type: Type of id researched
        :return: A scryfall `Card` instance
        """
        type = CardIdentifierPath(type)
        path = f"/cards/{id}"
        if type.value and type != CardIdentifierPath.CODE_NUMBER:
            path = f"/cards/{type.value}/{id}"
        return await self._get_item(path, Card)

    card = synchronize(card_async)

    async def random_async(self, q: Optional[str] = None) -> Card:
        """
        Returns a single random Card object.

        This method will use:
        - /cards/random

        :param q: The optional parameter q supports the same fulltext search system
                  that the main site uses. Providing q will filter the pool of cards
                  before returning a random entry.
        :return: A scryfall `Card` instance
        """
        params = {}
        if q:
            params["q"] = q
        return await self._get_item(
            "/cards/random", Card, params=params, headers={"cache-control": "no-cache"}
        )

    random = synchronize(random_async)

    async def search_async(
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
                               included. Equivalent to adding include:extras to the
                               fulltext search.
        :param include_multilingual: If true, cards in every language supported by
                                     Scryfall will be included.
        :param include_variations: If true, rare care variants will be included,
                                   like the Hairy Runesword.
        :param q: A fulltext search query.
        :param limit: The number of item to return, please note that Mightstone
                      wraps Scryfall pagination and streams the results
        :return: A scryfall `Card` instance async generator
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

    search = sync_generator(search_async)

    async def named_async(self, q: str, set: Optional[str] = None, exact=True) -> Card:
        """
        Returns a Card based on a name search string. This method is designed for
        building chatbots, forum bots, and other services that need card details
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

        :param q: The searched card name
        :param exact: Run a strict text research instead of a fuzzy search
        :param set: You may also provide a set code in the
                    set parameter, in which case the name search and the returned card
                    print will be limited to the specified set.
        :return: A scryfall `Card` instance
        """
        params = {}
        if exact:
            params["exact"] = q
        else:
            params["fuzzy"] = q
        if set:
            params["set"] = set
        return await self._get_item("/cards/named", Card, params=params)

    named = synchronize(named_async)

    async def autocomplete_async(self, q: str, include_extras=False) -> Catalog:
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

    autocomplete = synchronize(autocomplete_async)

    async def collection_async(
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
    ) -> AsyncGenerator[Card, None]:
        """
        Accepts a JSON array of card identifiers, and returns a List object with the
        collection of requested cards. A maximum of 75 card references may be
        submitted per request.

        :param identifiers: Each submitted card identifier must be a JSON object with
                            one or more of the keys id, mtgo_id, multiverse_id,
                            oracle_id, illustration_id, name, set, and collector_number
        :return: A scryfall `Card` instance async generator
        """
        async for item in self._list(
            "/cards/collection", Card, verb="POST", json={"identifiers": identifiers}
        ):
            yield item

    collection = sync_generator(collection_async)

    async def rulings_async(
        self,
        id: str,
        type: RulingIdentifierPath = RulingIdentifierPath.SCRYFALL,
        limit: Optional[int] = None,
    ) -> AsyncGenerator[Ruling, None]:
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
        :return: A scryfall `Ruling` instance async generator
        """
        type = RulingIdentifierPath(type)
        path = f"/cards/{id}/rulings"
        if type.value and type != RulingIdentifierPath.CODE_NUMBER:
            path = f"/cards/{type.value}/{id}/rulings"

        async for item in self._list(path, Ruling, limit=limit):
            yield item

    rulings = sync_generator(rulings_async)

    async def symbols_async(
        self, limit: Optional[int] = None
    ) -> AsyncGenerator[Symbol, None]:
        """
        Returns a List of all Card Symbols.

        :param limit: The number of item to return, please note that Mightstone
                      wraps Scryfall pagination and streams the results
        :return: A scryfall `Symbol` instance async generator
        """
        async for item in self._list("/symbology", Symbol, limit=limit):
            yield item

    symbols = sync_generator(symbols_async)

    async def parse_mana_async(self, cost: str) -> ManaCost:
        """
        Parses the given mana cost parameter and returns Scryfall’s interpretation.

        The server understands most community shorthand for mana costs (such as 2WW
        for {2}{W}{W}). Symbols can also be out of order, lowercase, or have multiple
        colorless costs (such as 2{g}2 for {4}{G}).

        If part of the string could not be understood, the server will raise an Error
        object describing the problem.

        :param cost: A mana cost string
        :return: A `ManaCost` instance
        """
        return await self._get_item(
            "/symbology/parse-mana", ManaCost, params={"cost": cost}
        )

    parse_mana = synchronize(parse_mana_async)

    async def catalog_async(self, type: CatalogType) -> Catalog:
        """
        A Catalog object contains an array of Magic datapoints (words, card values,
        etc). Catalog objects are provided by the API as aids for building other
        Magic software and understanding possible values for a field on Card objects.

        :param type: See `CatalogType` for more informations
        :return: A `Catalog` instance
        """
        type = CatalogType(type)
        return await self._get_item(f"/catalog/{type.value}", Catalog)

    catalog = synchronize(catalog_async)

    async def migrations_async(
        self, limit: Optional[int] = None
    ) -> AsyncGenerator[Migration, None]:
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

    migrations = sync_generator(migrations_async)

    async def migration_async(self, id: str) -> Migration:
        """
        Returns a single Card Migration with the given :id

        :return: A `Migration` instance
        """
        return await self._get_item(f"/migrations/{id}", Migration)

    migration = synchronize(migration_async)

    async def sets_async(
        self, limit: Optional[int] = None
    ) -> AsyncGenerator[Set, None]:
        """
        Returns a List object of all Sets on Scryfall.

        :param limit: The number of item to return, please note that Mightstone
                      wraps Scryfall pagination and streams the results
        :return: A `Set` instance async generator
        """
        async for item in self._list("/sets", Set, limit=limit):
            yield item

    sets = sync_generator(sets_async)

    async def set_async(self, id_or_code: Optional[str] = None) -> Set:
        """
        Returns a Set with the given set code.

        :param id_or_code: The code can be either the code or the mtgo_code or the
                           scryfall UUID for the set.
        :return: A `Set` instance
        """
        return await self._get_item(f"/sets/{id_or_code}", Set)

    set = sync_generator(sets_async)

    @overload
    async def _get_item(self, path: str, model: None, **kwargs) -> Dict: ...

    @overload
    async def _get_item(self, path: str, model: Type[_T], **kwargs) -> _T: ...

    async def _get_item(
        self, path: str, model: Optional[Type[_T]] = None, **kwargs
    ) -> Union[_T, Dict]:
        try:
            response = await self.client.get(path, **kwargs)
            if not response.is_success:
                error = Error.model_validate(response.json())
                raise ServiceError(
                    message=error.details,
                    method=response.request.method,
                    url=response.request.url,
                    status=response.status_code,
                    data=error,
                )
            data = response.json()
            if model:
                data = model.model_validate(data)
            return data
        except ValidationError as e:
            raise ServiceError(
                message=f"Failed to validate {model} data, {e.errors()}",
                url=path,
                method="GET",
                status=None,
                data=e,
            )
        except HTTPStatusError as e:
            raise ServiceError(
                message="Failed to fetch data from Scryfall",
                url=e.request.url,
                method=e.request.method,
                status=e.response.status_code,
                data=Error.model_validate_json(e.response.content),
            )

    @overload
    def _list(self, path: str, model: None, **kwargs) -> AsyncGenerator[Dict, None]: ...

    @overload
    def _list(
        self, path: str, model: Type[_T], **kwargs
    ) -> AsyncGenerator[_T, None]: ...

    async def _list(
        self, path, model: Optional[Type[_T]] = None, verb="GET", limit=None, **kwargs
    ) -> AsyncGenerator[Union[_T, Dict], None]:
        i = 0
        try:
            while True:
                response = await self.client.request(verb, path, **kwargs)
                if response.is_error:
                    raise ServiceError(
                        message="Failed to fetch data from Scryfall",
                        url=response.request.url,
                        status=response.status_code,
                        data=Error.model_validate(response.json()),
                    )

                my_list = ScryfallList.model_validate(response.json())
                if my_list is None:
                    return

                for item in my_list.data:
                    if limit and i >= limit:
                        return
                    i += 1

                    if model:
                        yield model.model_validate(item)
                    else:
                        yield item

                if not my_list.has_more:
                    return

                next_page = cast(AnyUrl, my_list.next_page)
                path = f"{next_page.path}?{next_page.query}"
                await self._sleep()
        except ValidationError as e:
            raise ServiceError(
                message=f"Failed to validate {model} data for item #{i}, {e.errors()}",
                url=path,
                status=None,
                data=e,
            )
        except HTTPStatusError as e:
            raise ServiceError(
                message="Failed to fetch data from Scryfall",
                url=e.request.url,
                status=e.response.status_code,
                data=Error.model_validate(e),
            )

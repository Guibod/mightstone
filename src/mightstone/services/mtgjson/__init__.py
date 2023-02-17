"""
MTGJSON support core
"""

import json
from enum import Enum
from typing import Any, AsyncGenerator, List, Optional, Tuple, Type, TypeVar, Union

from aiohttp import ClientResponseError
from aiostream.stream import enumerate as aenumerate
from pydantic.error_wrappers import ValidationError

from mightstone import logger
from mightstone.ass import compressor
from mightstone.services import MightstoneHttpClient, ServiceError
from mightstone.services.mtgjson.models import (
    Card,
    CardAtomic,
    CardAtomicGroup,
    CardPrices,
    CardSet,
    CardTypes,
    Deck,
    DeckList,
    Keywords,
    Meta,
    Set,
    SetList,
    TcgPlayerSKU,
    TcgPlayerSKUs,
)


class MtgJsonMode(Enum):
    """
    Available data parse mode

    MTGJSON model is not consistent, this enum describe the expected data structure
    of a MTGJSON response
    """

    LIST_OF_MODEL = 0
    """
    In this mode, we expect a structure similar to
     .. code-block:: json
     {"data": [{"prop": 1}, "b": {"prop": 2}]}
    """
    DICT_OF_MODEL = 1
    """
    In this mode, we expect a structure similar to
     .. code-block:: json
     {"data": {"a": {"prop": 1}, "b": {"prop": 2}}}
    """
    DICT_OF_LIST_OF_MODEL = 2
    """
    In this mode, we expect a structure similar to
     .. code-block:: json
     {"data": {"a": [{"prop": 1}], "b": [{"prop": 2}]}}
    """


class MtgJsonCompression(Enum):
    """
    Available compression mode enumerator

    MTGJSON provide 5 compression formats, Mightstone support 4 of them.
    """

    NONE = None
    """ No compression, use raw JSON """
    XZ = "xz"
    """ LZMA compression, use .xz files """
    ZIP = "zip"
    """ ZIP compression, use .zip files (not supported)"""
    GZIP = "gz"
    """ GZIP compression, use .gz files"""
    BZ2 = "bz2"
    """ BZIP2 compression, use .bz2 files"""

    def to_stream_compression(self):
        """
        Compute the compression type to a python module

        :return: the name of the python module
        """
        if self.value is None:
            return None
        elif self.value == "xz":
            return "lzma"
        elif self.value == "gz":
            return "gzip"
        elif self.value == "bz2":
            return "bzip2"
        raise ValueError(f"{self.name} compression protocol cannot be read as a stream")


T = TypeVar("T")


class MtgJson(MightstoneHttpClient):
    """
    MTGJSON client

    Supports compression and will get gzip versions by default.
    """

    base_url = "https://mtgjson.com"

    def __init__(
        self,
        compression: MtgJsonCompression = None,
        version: int = 5,
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.version = int(version)
        if not compression:
            compression = MtgJsonCompression.GZIP
        self.compression = MtgJsonCompression(compression)

    async def all_printings(self) -> AsyncGenerator[CardSet, None]:
        """
        all Card (Set) cards, including all printings and variations, categorized by
        set.

        :return: An async iterator of CardSet
        """
        async for k, item in self._iterate_model(
            kind="AllPrintings", model=Set, mode=MtgJsonMode.DICT_OF_MODEL
        ):
            yield item

    async def all_identifiers(self) -> AsyncGenerator[Card, None]:
        """
        all Card (Set) cards organized by card UUID.

        :return: An async iterator of Card object (either CardToken, or CardSet)
        """
        async for k, item in self._iterate_model(kind="AllIdentifiers", model=Card):
            yield item

    async def all_prices(self) -> AsyncGenerator[CardPrices, None]:
        """
        all prices of cards in various formats.

        :return: An async iterator of CardPrices
        """
        async for k, item in self._iterate_model(kind="AllPrices"):
            yield CardPrices(uuid=k, **item)

    async def atomic_cards(self) -> AsyncGenerator[CardAtomic, None]:
        """
        every Card (Atomic) card.

        :return: An async iterator of ``CardAtomicGroup``
        """
        async for item in self._atomic(kind="AtomicCards"):
            yield item

    async def card_types(self) -> CardTypes:
        """
        every card type of any type of card.

        :return: A ``CardTypes`` object
        """
        return await self._get_item("CardTypes", model=CardTypes)

    async def compiled_list(self) -> List[str]:
        """
        all individual outputs from MTGJSON, such as AllPrintings, CardTypes, etc.

        :return: A list of string
        """
        return await self._get_item("CompiledList", model=list)

    async def deck_list(self) -> AsyncGenerator[DeckList, None]:
        """
        all individual Deck data.

        :return: An async iterator of DeckList
        """
        async for i, item in self._iterate_model(
            kind="DeckList", model=DeckList, mode=MtgJsonMode.LIST_OF_MODEL
        ):
            yield item

    async def deck(self, file_name: str) -> Deck:
        """
        Recovers a deck data

        :param file_name: the deck file_name
        :return: A ``Deck`` object
        """
        return await self._get_item(f"decks/{file_name}", model=Deck)

    async def enum_values(self) -> dict:
        """
        All known property values for various Data Models.

        :return: a ``dict`` object
        """
        return await self._get_item("EnumValues", model=dict)

    async def keywords(self) -> Keywords:
        """
        a list of possible all keywords used on all cards.

        :return: A ``Keywords`` object
        """
        return await self._get_item("Keywords", model=Keywords)

    async def legacy(self) -> AsyncGenerator[Set, None]:
        """
        all Card (Set) cards organized by Set, restricted to sets legal in the
        Legacy format.

        :return: An async iterator of ``Set``
        """
        async for k, item in self._iterate_model(kind="Legacy", model=Set):
            yield item

    async def legacy_atomic(self) -> AsyncGenerator[CardAtomicGroup, None]:
        """
        all Card (Set) cards organized by Set, restricted to sets legal in the
        Legacy format.

        :return: An async iterator of ``CardAtomicGroup``
        """
        async for item in self._atomic(kind="LegacyAtomic"):
            yield item

    async def meta(self) -> Meta:
        """
        the metadata object with ISO 8601 dates for latest build and SemVer
        specifications of the MTGJSON release.

        :return: A Meta object
        """
        return await self._get_item("Meta", model=Meta)

    async def modern(self) -> AsyncGenerator[Set, None]:
        """
        all Card (Set) cards organized by Set, restricted to sets legal in the
        Modern format.

        :return: An async iterator of ``Set``
        """
        async for k, item in self._iterate_model(kind="Modern", model=Set):
            yield item

    async def modern_atomic(self) -> AsyncGenerator[CardAtomicGroup, None]:
        """
        all Card (Atomic) cards, restricted to cards legal in the Modern format.

        :return: An async iterator of ``CardAtomicGroup``
        """
        async for item in self._atomic(kind="ModernAtomic"):
            yield item

    async def pauper_atomic(self) -> AsyncGenerator[CardAtomicGroup, None]:
        """
        all Card (Atomic) cards, restricted to cards legal in the Pauper format.

        :return: An async iterator of ``CardAtomicGroup``
        """
        async for item in self._atomic(kind="PauperAtomic"):
            yield item

    async def pioneer(self) -> AsyncGenerator[Set, None]:
        """
        all Card (Set) cards organized by Set, restricted to cards legal in the
        Pioneer format.

        :return: An async iterator of ``Set``
        """
        async for k, item in self._iterate_model(kind="Pioneer", model=Set):
            yield item

    async def pioneer_atomic(self) -> AsyncGenerator[CardAtomicGroup, None]:
        """
        all Card (Atomic) cards, restricted to cards legal in the Pioneer format.

        :return: An async iterator of ``CardAtomicGroup``
        """
        async for item in self._atomic(kind="PioneerAtomic"):
            yield item

    async def set_list(self) -> AsyncGenerator[SetList, None]:
        """
        a list of meta data for all Set data.

        :return: An async iterator of ``SetList``
        """
        async for k, item in self._iterate_model(
            kind="SetList", model=SetList, mode=MtgJsonMode.LIST_OF_MODEL
        ):
            yield item

    async def set(self, code: str) -> SetList:
        """
        Get a Set data

        :param code: The set identifier, such as "IKO" for "Ikoria, lair of the
                     monsters"

        :return: The set representation
        """
        return await self._get_item(code, SetList)

    async def standard(self) -> AsyncGenerator[Set, None]:
        """
        all Card (Set) cards organized by Set, restricted to cards legal in the
        Standard format.

        :return: An async iterator of ``Set``
        """
        async for k, item in self._iterate_model(kind="Standard", model=Set):
            yield item

    async def standard_atomic(self) -> AsyncGenerator[CardAtomicGroup, None]:
        """
        all Card (Atomic) cards, restricted to cards legal in the Standard format.

        :return: An async iterator of ``CardAtomicGroup``
        """
        async for item in self._atomic(kind="StandardAtomic"):
            yield item

    async def tcg_player_skus(self) -> AsyncGenerator[TcgPlayerSKUs, None]:
        """
        TCGplayer SKU information based on card UUIDs.

        :return: an async iterator of ``TcgPlayerSKUs``
        """
        group: Optional[TcgPlayerSKUs] = None
        async for (k, i), item in self._iterate_model(
            kind="TcgplayerSkus",
            model=TcgPlayerSKU,
            mode=MtgJsonMode.DICT_OF_LIST_OF_MODEL,
        ):
            if not group or k != group.uuid:
                if group:
                    yield group
                group = TcgPlayerSKUs(uuid=k, skus=[])
            group.skus.append(item)

        yield group

    async def vintage(self) -> AsyncGenerator[Set, None]:
        """
        all Card (Set) cards organized by Set, restricted to sets legal in the
        Vintage format.

        :return: An async iterator of ``Set``
        """
        async for k, item in self._iterate_model(kind="Vintage", model=Set):
            yield item

    async def vintage_atomic(self) -> AsyncGenerator[CardAtomicGroup, None]:
        """
        all Card (Atomic) cards, restricted to sets legal in the Vintage format.

        :return: An async iterator of ``CardAtomicGroup``
        """
        async for item in self._atomic(kind="VintageAtomic"):
            yield item

    async def _atomic(self, kind: str) -> AsyncGenerator[CardAtomicGroup, None]:
        group: Optional[CardAtomicGroup] = None
        async for (k, i), item in self._iterate_model(
            kind=kind, model=CardAtomic, mode=MtgJsonMode.DICT_OF_LIST_OF_MODEL
        ):
            if not group or k != group.name:
                if group:
                    yield group
                group = CardAtomicGroup(name=k, prints=[])
            group.prints.append(item)

        yield group

    async def _get_item(
        self,
        kind: str,
        model: Type[T] = dict,
        **kwargs,
    ) -> T:
        path = f"/api/v{self.version}/{kind}.json"
        if self.compression != MtgJsonCompression.NONE:
            path += "." + self.compression.value

        try:
            async with self.session.get(path, **kwargs) as f:
                async with compressor.open(
                    f.content, compression=self.compression.to_stream_compression()
                ) as f2:
                    data = json.loads(await f2.read())
                    data = data.get("data")

                    try:
                        return model.parse_obj(data)
                    except AttributeError:
                        return model(data)
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
                message="Failed to fetch data from MTG Json",
                url=e.request_info.real_url,
                method=e.request_info.method,
                status=e.status,
                data=None,
            )

    async def _iterate_model(
        self, model: Type[T] = dict, error_threshold: int = 10, **kwargs
    ) -> AsyncGenerator[Tuple[Union[str, int, Tuple[str, int]], T], None]:
        error = 0
        async for k, v in self._iterate_raw(**kwargs):
            try:
                try:
                    yield k, model.parse_obj(v)
                except AttributeError:
                    yield k, model(v)

            except ValidationError as e:
                error += 1
                logger.warning(
                    "Failed to validate %s data, for item %s, %s", model, k, e.errors
                )

                if error > error_threshold:
                    raise RuntimeError(
                        "Too many model validation error, something is wrong"
                    )

    async def _iterate_raw(
        self,
        kind: str,
        ijson_path: str = None,
        mode: MtgJsonMode = MtgJsonMode.DICT_OF_MODEL,
    ) -> AsyncGenerator[Tuple[Union[str, int, Tuple[str, int]], Any], None]:
        path = f"/api/v{self.version}/{kind}.json"
        if self.compression != MtgJsonCompression.NONE:
            path += "." + self.compression.value

        logger.debug("Fetching %s", path)
        async with self.session.get(path) as f:
            try:
                f.raise_for_status()
                logger.debug("Reading %s", path)
                # TODO: also grab meta.version and meta.date
                async with compressor.open(
                    f.content, compression=self.compression.to_stream_compression()
                ) as f2:
                    if mode == MtgJsonMode.DICT_OF_MODEL:
                        if not ijson_path:
                            ijson_path = "data"
                        async for k, v in self.ijson.kvitems_async(f2, ijson_path):
                            yield k, v
                    elif mode == MtgJsonMode.LIST_OF_MODEL:
                        if not ijson_path:
                            ijson_path = "data.item"
                        async for i, v in aenumerate(
                            self.ijson.items_async(f2, ijson_path)
                        ):
                            yield i, v
                    elif mode == MtgJsonMode.DICT_OF_LIST_OF_MODEL:
                        if not ijson_path:
                            ijson_path = "data"
                        async for k, l in self.ijson.kvitems_async(f2, ijson_path):
                            for i, v in enumerate(l, start=1):
                                yield (k, i), v
                logger.debug("Done %s", path)
            except ClientResponseError as e:
                raise ServiceError(
                    message="Failed to fetch data from Mtg JSON",
                    url=e.request_info.real_url,
                    method=e.request_info.method,
                    status=e.status,
                    data=e.message,
                )

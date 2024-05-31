"""
MTGJSON support core
"""

import json
import logging
from enum import Enum
from typing import (
    Any,
    AsyncGenerator,
    Callable,
    Dict,
    List,
    Literal,
    Optional,
    Tuple,
    Type,
    TypeVar,
    Union,
    overload,
)

import asyncstdlib
from httpx import HTTPStatusError
from pydantic import ValidationError

from mightstone.ass import compressor, sync_generator, synchronize
from mightstone.core import MightstoneModel
from mightstone.services import MightstoneHttpClient, ServiceError
from mightstone.services.mtgjson.models import (
    Card,
    CardAtomic,
    CardFace,
    CardPrices,
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

DictOfListOfKey = Tuple[str, int]
DictOfListOfModel = Tuple[DictOfListOfKey, Any]
ListOfKey = int
ListOfModel = Tuple[ListOfKey, Any]
DictOfKey = str
DictOfModel = Tuple[DictOfKey, Any]
GeneratorModel = Union[DictOfListOfModel, ListOfModel, DictOfModel]
GeneratorKey = Union[DictOfListOfKey, ListOfKey, DictOfKey]

logger = logging.getLogger("mightstone")


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


class MtgJsonCompression(str, Enum):
    """
    Available compression mode enumerator

    MTGJSON provide 5 compression formats, Mightstone support 4 of them.
    """

    NONE = ""
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
        if self.value == "":
            return None
        elif self.value == "xz":
            return "lzma"
        elif self.value == "gz":
            return "gzip"
        elif self.value == "bz2":
            return "bzip2"
        raise ValueError(f"{self.name} compression protocol cannot be read as a stream")


_T = TypeVar("_T", bound=MightstoneModel)


class MtgJson(MightstoneHttpClient):
    """
    MTGJSON client

    Supports compression and will get gzip versions by default.
    """

    base_url = "https://mtgjson.com"

    def __init__(
        self,
        compression: Optional[MtgJsonCompression] = None,
        version: int = 5,
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.version = int(version)
        if compression is None:
            compression = MtgJsonCompression.GZIP
        self.compression = MtgJsonCompression(compression)

    def set_compression(self, compression=MtgJsonCompression):
        self.compression = MtgJsonCompression(compression)

    async def all_printings_async(self) -> AsyncGenerator[Set, None]:
        """
        all Card (Set) cards, including all printings and variations, categorized by
        set.

        :return: An async iterator of CardSet
        """
        async for k, item in self._iterate_model(
            kind="AllPrintings", model=Set, mode=MtgJsonMode.DICT_OF_MODEL
        ):
            yield item

    all_printings = sync_generator(all_printings_async)

    async def all_identifiers_async(self) -> AsyncGenerator[Card, None]:
        """
        all Card (Set) cards organized by card UUID.

        :return: An async iterator of Card object (either CardToken, or CardSet)
        """
        async for k, item in self._iterate_model(  # type: ignore # no-qa
            kind="AllIdentifiers", model=Card
        ):
            yield item

    all_identifiers = sync_generator(all_identifiers_async)

    async def all_prices_async(self) -> AsyncGenerator[CardPrices, None]:
        """
        all prices of cards in various formats.

        :return: An async iterator of CardPrices
        """
        async for k, item in self._iterate_model(kind="AllPrices"):
            yield CardPrices(uuid=k, **item)  # type: ignore

    all_prices = sync_generator(all_prices_async)

    async def atomic_cards_async(self) -> AsyncGenerator[CardAtomic, None]:
        """
        every Card (Atomic) card.

        :return: An async iterator of ``CardAtomic``
        """
        async for item in self._atomic(kind="AtomicCards"):
            yield item

    atomic_cards = sync_generator(atomic_cards_async)

    async def card_types_async(self) -> CardTypes:
        """
        every card type of any type of card.

        :return: A ``CardTypes`` object
        """
        return await self._get_item("CardTypes", model=CardTypes)

    card_types = synchronize(card_types_async)

    async def compiled_list_async(self) -> List[str]:
        """
        all individual outputs from MTGJSON, such as AllPrintings, CardTypes, etc.

        :return: A list of string
        """
        return await self._get_item("CompiledList", model=list)

    compiled_list = synchronize(compiled_list_async)

    async def deck_list_async(self) -> AsyncGenerator[DeckList, None]:
        """
        all individual Deck data.

        :return: An async iterator of DeckList
        """
        async for i, item in self._iterate_model(
            kind="DeckList", model=DeckList, mode=MtgJsonMode.LIST_OF_MODEL
        ):
            yield item

    deck_list = sync_generator(deck_list_async)

    async def deck_async(self, file_name: str) -> Deck:
        """
        Recovers a deck data

        :param file_name: the deck file_name
        :return: A ``Deck`` object
        """
        return await self._get_item(f"decks/{file_name}", model=Deck)

    deck = synchronize(deck_async)

    async def enum_values_async(self) -> dict:
        """
        All known property values for various Data Models.

        :return: a ``dict`` object
        """
        return await self._get_item("EnumValues", model=dict)

    enum_values = synchronize(enum_values_async)

    async def keywords_async(self) -> Keywords:
        """
        a list of possible all keywords used on all cards.

        :return: A ``Keywords`` object
        """
        return await self._get_item("Keywords", model=Keywords)

    keywords = synchronize(keywords_async)

    async def legacy_async(self) -> AsyncGenerator[Set, None]:
        """
        all Card (Set) cards organized by Set, restricted to sets legal in the
        Legacy format.

        :return: An async iterator of ``Set``
        """
        async for k, item in self._iterate_model(kind="Legacy", model=Set):
            yield item

    legacy = sync_generator(legacy_async)

    async def legacy_atomic_async(self) -> AsyncGenerator[CardAtomic, None]:
        """
        all Card (Set) cards organized by Set, restricted to sets legal in the
        Legacy format.

        :return: An async iterator of ``CardAtomic``
        """
        async for item in self._atomic(kind="LegacyAtomic"):
            yield item

    legacy_atomic = sync_generator(legacy_atomic_async)

    async def meta_async(self) -> Meta:
        """
        the metadata object with ISO 8601 dates for latest build and SemVer
        specifications of the MTGJSON release.

        :return: A Meta object
        """
        return await self._get_item("Meta", model=Meta)

    meta = synchronize(meta_async)

    async def modern_async(self) -> AsyncGenerator[Set, None]:
        """
        all Card (Set) cards organized by Set, restricted to sets legal in the
        Modern format.

        :return: An async iterator of ``Set``
        """
        async for k, item in self._iterate_model(kind="Modern", model=Set):
            yield item

    modern = sync_generator(modern_async)

    async def modern_atomic_async(self) -> AsyncGenerator[CardAtomic, None]:
        """
        all Card (Atomic) cards, restricted to cards legal in the Modern format.

        :return: An async iterator of ``CardAtomic``
        """
        async for item in self._atomic(kind="ModernAtomic"):
            yield item

    modern_atomic = sync_generator(modern_atomic_async)

    async def pauper_atomic_async(self) -> AsyncGenerator[CardAtomic, None]:
        """
        all Card (Atomic) cards, restricted to cards legal in the Pauper format.

        :return: An async iterator of ``CardAtomic``
        """
        async for item in self._atomic(kind="PauperAtomic"):
            yield item

    pauper_atomic = sync_generator(pauper_atomic_async)

    async def pioneer_async(self) -> AsyncGenerator[Set, None]:
        """
        all Card (Set) cards organized by Set, restricted to cards legal in the
        Pioneer format.

        :return: An async iterator of ``Set``
        """
        async for k, item in self._iterate_model(kind="Pioneer", model=Set):
            yield item

    pioneer = sync_generator(pioneer_async)

    async def pioneer_atomic_async(self) -> AsyncGenerator[CardAtomic, None]:
        """
        all Card (Atomic) cards, restricted to cards legal in the Pioneer format.

        :return: An async iterator of ``CardAtomic``
        """
        async for item in self._atomic(kind="PioneerAtomic"):
            yield item

    pioneer_atomic = sync_generator(pioneer_atomic_async)

    async def set_list_async(self) -> AsyncGenerator[SetList, None]:
        """
        a list of meta data for all Set data.

        :return: An async iterator of ``SetList``
        """
        async for k, item in self._iterate_model(
            kind="SetList", model=SetList, mode=MtgJsonMode.LIST_OF_MODEL
        ):
            yield item

    set_list = sync_generator(set_list_async)

    async def set_async(self, code: str) -> SetList:
        """
        Get a Set data

        :param code: The set identifier, such as "IKO" for "Ikoria, lair of the
                     monsters"

        :return: The set representation
        """
        return await self._get_item(code, SetList)

    set = synchronize(set_async)

    async def standard_async(self) -> AsyncGenerator[Set, None]:
        """
        all Card (Set) cards organized by Set, restricted to cards legal in the
        Standard format.

        :return: An async iterator of ``Set``
        """
        async for k, item in self._iterate_model(kind="Standard", model=Set):
            yield item

    standard = sync_generator(standard_async)

    async def standard_atomic_async(self) -> AsyncGenerator[CardAtomic, None]:
        """
        all Card (Atomic) cards, restricted to cards legal in the Standard format.

        :return: An async iterator of ``CardAtomic``
        """
        async for item in self._atomic(kind="StandardAtomic"):
            yield item

    standard_atomic = sync_generator(standard_atomic_async)

    async def tcg_player_skus_async(self) -> AsyncGenerator[TcgPlayerSKUs, None]:
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
                group = TcgPlayerSKUs(uuid=k, skus=[])  # type: ignore
            group.skus.append(item)

            yield group

    tcg_player_skus = sync_generator(tcg_player_skus_async)

    async def vintage_async(self) -> AsyncGenerator[Set, None]:
        """
        all Card (Set) cards organized by Set, restricted to sets legal in the
        Vintage format.

        :return: An async iterator of ``Set``
        """
        async for k, item in self._iterate_model(kind="Vintage", model=Set):
            yield item

    vintage = sync_generator(vintage_async)

    async def vintage_atomic_async(self) -> AsyncGenerator[CardAtomic, None]:
        """
        all Card (Atomic) cards, restricted to sets legal in the Vintage format.

        :return: An async iterator of ``CardAtomic``
        """
        async for item in self._atomic(kind="VintageAtomic"):
            yield item

    vintage_atomic = sync_generator(vintage_atomic_async)

    async def _atomic(self, kind: str) -> AsyncGenerator[CardAtomic, None]:
        card: Optional[CardAtomic] = None
        async for (k, i), item in self._iterate_model(
            kind=kind, model=CardFace, mode=MtgJsonMode.DICT_OF_LIST_OF_MODEL
        ):
            if not card or k != card.ascii_name:
                if card:
                    yield card
                card = CardAtomic(ascii_name=k, faces=[])  # type: ignore
            card.faces.append(item)

        if card:
            yield card

    async def _get_item(
        self,
        kind: str,
        model: Union[Type[_T], Type[Dict], Type[List]] = dict,
        **kwargs,
    ) -> _T:
        path = f"/api/v{self.version}/{kind}.json"
        if self.compression != MtgJsonCompression.NONE:
            path += "." + self.compression.value

        try:
            async with self.client.stream("GET", path, **kwargs) as f:
                async with compressor.open(
                    f.aiter_bytes(),
                    compression=self.compression.to_stream_compression(),
                ) as f2:
                    data = json.loads(await f2.read())
                    data = data.get("data")

                    if issubclass(model, MightstoneModel):
                        return model.model_validate(data)  # type: ignore

                    return model(data)  # type: ignore
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
                message="Failed to fetch data from MTG Json",
                url=e.request.url,
                method=e.request.method,
                status=e.response.status_code,
                data=None,
            )

    @overload
    def _iterate_model(
        self, kind: str
    ) -> AsyncGenerator[Tuple[DictOfKey, Dict], None]: ...

    @overload
    def _iterate_model(
        self, kind: str, model: None
    ) -> AsyncGenerator[Tuple[DictOfKey, Dict], None]: ...

    @overload
    def _iterate_model(
        self, kind: str, model: Type[_T]
    ) -> AsyncGenerator[Tuple[DictOfKey, _T], None]: ...

    @overload
    def _iterate_model(
        self, kind: str, model: None, mode: Literal[MtgJsonMode.DICT_OF_MODEL]
    ) -> AsyncGenerator[Tuple[DictOfKey, Dict], None]: ...

    @overload
    def _iterate_model(
        self, kind: str, model: Type[_T], mode: Literal[MtgJsonMode.DICT_OF_MODEL]
    ) -> AsyncGenerator[Tuple[DictOfKey, _T], None]: ...

    @overload
    def _iterate_model(
        self, kind: str, model: None, mode: Literal[MtgJsonMode.LIST_OF_MODEL]
    ) -> AsyncGenerator[Tuple[ListOfKey, Dict], None]: ...

    @overload
    def _iterate_model(
        self, kind: str, model: Type[_T], mode: Literal[MtgJsonMode.LIST_OF_MODEL]
    ) -> AsyncGenerator[Tuple[ListOfKey, _T], None]: ...

    @overload
    def _iterate_model(
        self, kind: str, model: None, mode: Literal[MtgJsonMode.DICT_OF_LIST_OF_MODEL]
    ) -> AsyncGenerator[Tuple[DictOfListOfKey, Dict], None]: ...

    @overload
    def _iterate_model(
        self,
        kind: str,
        model: Type[_T],
        mode: Literal[MtgJsonMode.DICT_OF_LIST_OF_MODEL],
    ) -> AsyncGenerator[Tuple[DictOfListOfKey, _T], None]: ...

    async def _iterate_model(
        self,
        kind: str,
        model: Optional[Type[_T]] = None,
        mode: MtgJsonMode = MtgJsonMode.DICT_OF_MODEL,
        error_threshold: int = 10,
        **kwargs,
    ) -> AsyncGenerator[Tuple[GeneratorKey, Union[_T, Dict]], None]:
        error = 0
        async for k, v in self._iterate_raw(kind, mode, **kwargs):
            try:
                if model:
                    yield k, model.model_validate(v)
                else:
                    yield k, dict(v)
            except ValidationError as e:
                error += 1
                logger.warning(
                    "Failed to validate %s data, for item %s, %s", model, k, e.errors
                )

                if error > error_threshold:
                    raise RuntimeError(
                        "Too many model validation error, something is wrong"
                    )

    # @overload
    # def _iterate_raw(
    #     self,
    #     kind: str,
    #     mode: Literal[MtgJsonMode.DICT_OF_MODEL],
    # ) -> AsyncGenerator[DictOfModel, None]: ...
    #
    # @overload
    # def _iterate_raw(
    #     self,
    #     kind: str,
    #     mode: Literal[MtgJsonMode.DICT_OF_MODEL],
    #     ijson_path: str
    # ) -> AsyncGenerator[DictOfModel, None]: ...
    #
    # @overload
    # def _iterate_raw(
    #     self,
    #     kind: str,
    #     mode: Literal[MtgJsonMode.DICT_OF_LIST_OF_MODEL],
    # ) -> AsyncGenerator[DictOfListOfModel, None]: ...
    #
    # @overload
    # def _iterate_raw(
    #     self,
    #     kind: str,
    #     mode: Literal[MtgJsonMode.DICT_OF_LIST_OF_MODEL],
    #     ijson_path: str
    # ) -> AsyncGenerator[DictOfListOfModel, None]: ...
    #
    # @overload
    # def _iterate_raw(
    #     self,
    #     kind: str,
    #     mode: Literal[MtgJsonMode.LIST_OF_MODEL],
    # ) -> AsyncGenerator[ListOfModel, None]: ...
    #
    # @overload
    # def _iterate_raw(
    #     self,
    #     kind: str,
    #     mode: Literal[MtgJsonMode.LIST_OF_MODEL],
    #     ijson_path: str
    # ) -> AsyncGenerator[ListOfModel, None]: ...

    async def _iterate_raw(
        self,
        kind: str,
        mode: MtgJsonMode,
        ijson_path: Optional[str] = None,
    ) -> AsyncGenerator[GeneratorModel, None]:
        path = f"/api/v{self.version}/{kind}.json"
        if self.compression != MtgJsonCompression.NONE:
            path += "." + self.compression.value

        compression = self.compression.to_stream_compression()

        generator: Callable[
            [Any, Any, Optional[str]], AsyncGenerator[GeneratorModel, None]
        ] = dict_of_model_generator
        if mode == MtgJsonMode.LIST_OF_MODEL:
            generator = list_of_model_generator
        elif mode == MtgJsonMode.DICT_OF_LIST_OF_MODEL:
            generator = dict_of_list_of_model_generator

        async with self.client.stream("GET", path) as f:
            try:
                f.raise_for_status()
            except HTTPStatusError as e:
                raise ServiceError(
                    message="Failed to fetch data from Mtg JSON",
                    url=e.request.url,
                    method=e.request.method,
                    status=e.response.status_code,
                    data=e.response.content,
                )

            async with compressor.open(f.aiter_bytes(), compression=compression) as bit:
                async for item in generator(self.ijson, bit, ijson_path):
                    yield item


async def dict_of_list_of_model_generator(
    ijson, bytes_iterator, ijson_path=None
) -> AsyncGenerator[DictOfListOfModel, None]:
    if not ijson_path:
        ijson_path = "data"
    async for k, l in ijson.kvitems_async(bytes_iterator, ijson_path):
        for i, v in enumerate(l, start=1):
            yield (k, i), v


async def list_of_model_generator(
    ijson, bytes_iterator, ijson_path=None
) -> AsyncGenerator[ListOfModel, None]:
    if not ijson_path:
        ijson_path = "data.item"
    async for i, v in asyncstdlib.enumerate(
        ijson.items_async(bytes_iterator, ijson_path)
    ):
        yield i, v


async def dict_of_model_generator(
    ijson, bytes_iterator, ijson_path=None
) -> AsyncGenerator[DictOfModel, None]:
    if not ijson_path:
        ijson_path = "data"
    async for k, v in ijson.kvitems_async(bytes_iterator, ijson_path):
        yield k, v

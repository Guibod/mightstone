import logging
import os
import pathlib
from typing import Callable, Union

import beanie as beanie
import httpx_cache
import motor.motor_asyncio
from appdirs import AppDirs
from dependency_injector import containers, providers

from .config import DbImplem
from .core import get_documents
from .services.cardconjurer import CardConjurer
from .services.edhrec import EdhRecApi, EdhRecStatic
from .services.mtgjson import MtgJson
from .services.scryfall import Scryfall
from .services.wotc import RuleExplorer
from .storage import DatabaseDispatcher, Mongod

logger = logging.getLogger("mightstone")


def build_http_cache_backend(
    container=containers.DeclarativeContainer,
) -> Union[httpx_cache.FileCache, httpx_cache.DictCache]:
    persist_accessor: Callable = container.config.cache.persist.required()
    directory_accessor: Callable = container.config.cache.directory.required()

    if not persist_accessor():
        return httpx_cache.DictCache()

    directory = directory_accessor()
    if not directory:
        logger.debug(
            "http cache directory is not defined, using mightstone cache directory"
        )
        directory = pathlib.Path(container.appdirs().user_cache_dir).joinpath("http")
        container.config.directory.from_value(directory)
        # Also update the global config
        container.parent.config.directory.from_value(directory)

    if not directory.exists():
        logger.warning(
            "http cache directory %s does not exist yet, attempting to create it",
            directory,
        )
        os.makedirs(directory)

    return httpx_cache.FileCache(cache_dir=directory)


def build_storage_client_provider(
    container=containers.DeclarativeContainer,
) -> motor.motor_asyncio.AsyncIOMotorClient:
    if container.config.implementation.required()() == DbImplem.MOTOR:
        return motor.motor_asyncio.AsyncIOMotorClient(container.config.uri.required()())

    return motor.motor_asyncio.AsyncIOMotorClient(container.mongod().connection_string)


def build_storage_database(container=containers.DeclarativeContainer):
    client = container.client()
    dbname = container.config.database.required()()
    return client[dbname]


class Storage(containers.DeclarativeContainer):
    __self__ = providers.Self()  # type: ignore
    config = providers.Configuration()
    appdirs = providers.Dependency(instance_of=AppDirs)

    client: providers.Singleton[motor.motor_asyncio.AsyncIOMotorClient] = (
        providers.Singleton(build_storage_client_provider, __self__)
    )

    dispatcher: providers.Singleton[DatabaseDispatcher] = providers.Singleton(
        DatabaseDispatcher, __self__
    )

    database: providers.Singleton[motor.motor_asyncio.AsyncIOMotorDatabase] = (
        providers.Singleton(dispatcher.provided.get_database.call())
    )

    mongod: providers.Resource[Union[Mongod, None]] = providers.Resource(
        Mongod.generator,
        appdirs.provided.user_data_dir,
        appdirs.provided.user_cache_dir,
        config.directory(),
    )

    up = providers.Callable(__self__.provided.mongod.start.call())


class Beanie(containers.DeclarativeContainer):
    __self__ = providers.Self()  # type: ignore
    storage = providers.DependenciesContainer()
    documents = providers.Callable(get_documents)

    beanie = providers.Resource(
        beanie.init_beanie,
        storage.provided.database.call(),
        document_models=documents,
    )


class Httpx(containers.DeclarativeContainer):
    __self__ = providers.Self()  # type: ignore
    appdirs = providers.Dependency(instance_of=AppDirs)
    config = providers.Configuration()

    cache_backend: providers.Provider[
        Union[httpx_cache.FileCache, httpx_cache.DictCache]
    ] = providers.Singleton(
        build_http_cache_backend,
        __self__,
    )

    cache_transport: providers.Provider[httpx_cache.AsyncCacheControlTransport] = (
        providers.Singleton(
            httpx_cache.AsyncCacheControlTransport,
            cache=cache_backend,
            cacheable_methods=config.cache.methods.required(),
            cacheable_status_codes=config.cache.status.required(),
        )
    )


class Services(containers.DeclarativeContainer):
    config = providers.Configuration()
    httpx = providers.DependenciesContainer()

    rule_explorer: providers.Provider[RuleExplorer] = providers.Singleton(
        RuleExplorer,
        transport=httpx.cache_transport,
    )

    scryfall: providers.Provider[Scryfall] = providers.Singleton(
        Scryfall,
        transport=httpx.cache_transport,
    )

    edhrec_static: providers.Provider[EdhRecStatic] = providers.Singleton(
        EdhRecStatic,
        transport=httpx.cache_transport,
    )

    edhrec_api: providers.Provider[EdhRecApi] = providers.Singleton(
        EdhRecApi,
        transport=httpx.cache_transport,
    )

    card_conjurer: providers.Provider[CardConjurer] = providers.Singleton(
        CardConjurer,
        transport=httpx.cache_transport,
    )

    mtg_json: providers.Provider[MtgJson] = providers.Singleton(
        MtgJson,
        transport=httpx.cache_transport,
    )


class Application(containers.DeclarativeContainer):
    __self__ = providers.Self()  # type: ignore
    config = providers.Configuration()
    appdirs: providers.Singleton[AppDirs] = providers.Singleton(
        AppDirs, config.appname.required()
    )

    storage = providers.Container(Storage, config=config.storage, appdirs=appdirs)

    httpx: providers.Provider[Httpx] = providers.Container(
        Httpx, config=config.http, appdirs=appdirs
    )

    beanie: providers.Provider[Beanie] = providers.Container(Beanie, storage=storage)

    services: providers.Provider[Services] = providers.Container(
        Services,
        config=config.storage,
        httpx=httpx,
    )

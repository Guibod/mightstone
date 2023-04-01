import logging
import os
import pathlib
from typing import Callable, Union

import beanie as beanie
import beanita.db
import httpx_cache
import motor.motor_asyncio
from appdirs import AppDirs
from dependency_injector import containers, providers

from .ass import synchronize
from .config import DbImplem
from .core import get_documents
from .services.cardconjurer import CardConjurer
from .services.edhrec import EdhRecApi, EdhRecStatic
from .services.mtgjson import MtgJson
from .services.scryfall import Scryfall
from .services.wotc import RuleExplorer

logger = logging.getLogger("mightstone")


def build_directories(container=containers.DeclarativeContainer):
    logger.debug("building directory configurator")
    app_name_accessor = container.config.appname.required()

    return AppDirs(app_name_accessor())


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
) -> Union[beanita.Client, motor.motor_asyncio.AsyncIOMotorClient]:
    implem_accessor = container.config.implementation.required()

    if implem_accessor() == DbImplem.MOTOR:
        uri_accessor = container.config.uri.required()
        return motor.motor_asyncio.AsyncIOMotorClient(uri_accessor())

    directory = container.config.directory()
    if not directory:
        logger.debug(
            "http cache directory is not defined, using mightstone data directory"
        )
        directory = pathlib.Path(container.appdirs().user_data_dir).joinpath("mongita")

        container.config.directory.from_value(directory)
        # Also update the global config
        container.parent.parent.config.storage.directory.from_value(directory)

    if not directory.exists():
        logger.warning(
            "http data directory %s does not exist yet, attempting to create it",
            directory,
        )
        os.makedirs(directory)

    return beanita.Client(directory)


def build_storage_database(container=containers.DeclarativeContainer):
    client = container.client()
    dbname = container.config.database.required()()
    return client[dbname]


@synchronize
async def init_beanie(container: "Beanie"):
    await beanie.init_beanie(
        database=container.storage.database(), document_models=get_documents()
    )


class Storage(containers.DeclarativeContainer):
    __self__ = providers.Self()  # type: ignore
    config = providers.Configuration()
    appdirs = providers.Dependency(instance_of=AppDirs)

    client: providers.Callable[
        Union[beanita.Client, motor.motor_asyncio.AsyncIOMotorClient]
    ] = providers.Callable(build_storage_client_provider, __self__)

    database: providers.Callable[
        Union[beanita.db.Database, motor.motor_asyncio.AsyncIOMotorDatabase]
    ] = providers.Callable(build_storage_database, __self__)


class Beanie(containers.DeclarativeContainer):
    __self__ = providers.Self()  # type: ignore
    storage = providers.DependenciesContainer()

    init_beanie = providers.Resource(init_beanie, __self__)


class Httpx(containers.DeclarativeContainer):
    __self__ = providers.Self()  # type: ignore
    appdirs = providers.Dependency(instance_of=AppDirs)
    config = providers.Configuration()

    cache_backend: providers.Provider[
        Union[httpx_cache.FileCache, httpx_cache.DictCache]
    ] = providers.Callable(
        build_http_cache_backend,
        __self__,
    )

    cache_transport: providers.Provider[
        httpx_cache.AsyncCacheControlTransport
    ] = providers.Singleton(
        httpx_cache.AsyncCacheControlTransport,
        cache=cache_backend,
        cacheable_methods=config.cache.methods.required(),
        cacheable_status_codes=config.cache.status.required(),
    )


class Services(containers.DeclarativeContainer):
    config = providers.Configuration()
    httpx = providers.DependenciesContainer()

    rule_explorer: providers.Provider[RuleExplorer] = providers.Factory(
        RuleExplorer,
        transport=httpx.cache_transport,
    )

    scryfall: providers.Provider[Scryfall] = providers.Factory(
        Scryfall,
        transport=httpx.cache_transport,
    )

    edhrec_static: providers.Provider[EdhRecStatic] = providers.Factory(
        EdhRecStatic,
        transport=httpx.cache_transport,
    )

    edhrec_api: providers.Provider[EdhRecApi] = providers.Factory(
        EdhRecApi,
        transport=httpx.cache_transport,
    )

    card_conjurer: providers.Provider[CardConjurer] = providers.Factory(
        CardConjurer,
        transport=httpx.cache_transport,
    )

    mtg_json: providers.Provider[MtgJson] = providers.Factory(
        MtgJson,
        transport=httpx.cache_transport,
    )


class Application(containers.DeclarativeContainer):
    __self__ = providers.Self()  # type: ignore
    config = providers.Configuration()
    appdirs: providers.Callable[AppDirs] = providers.Callable(
        build_directories, __self__
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

import logging
import os
import pathlib

import ijson as ijson_module
import mongomock_motor
import motor.motor_asyncio
from appdirs import AppDirs
from httpx_cache import AsyncCacheControlTransport, BaseCache, DictCache, FileCache
from injector import Binder, Module, SingletonScope, provider, singleton

from .config import DbImplem, InMemorySettings, MainSettings
from .injector import cleaned
from .services.cardconjurer import CardConjurer
from .services.edhrec import EdhRecApi, EdhRecStatic
from .services.mtgjson import MtgJson
from .services.scryfall import Scryfall
from .services.wotc import RuleExplorer
from .storage import MightstoneInMemoryContext, Mongod
from .types import MightstoneIjsonBackend

logger = logging.getLogger("mightstone")


class JSON(Module):
    @provider
    @singleton
    def ijson(self, config: MainSettings) -> MightstoneIjsonBackend:
        try:
            out = ijson_module.get_backend(config.ijson)
            return out
        except ImportError:
            return ijson_module.get_backend("python")


class Storage(Module):
    def configure(self, binder: Binder):
        binder.bind(Mongod, scope=cleaned, to=self.mongod)
        binder.bind(motor.motor_asyncio.AsyncIOMotorClient, to=self.client)
        binder.bind(motor.motor_asyncio.AsyncIOMotorDatabase, to=self.database)
        binder.bind(mongomock_motor.AsyncMongoMockClient, to=self.mock_client)
        binder.bind(mongomock_motor.AsyncMongoMockDatabase, to=self.mock_database)

    @provider
    @singleton
    def client(
        self, config: MainSettings, mongod: Mongod
    ) -> motor.motor_asyncio.AsyncIOMotorClient:
        if config.storage.implementation == DbImplem.FAKE:
            raise NotImplementedError("No real client available in fake mode")
        if config.storage.implementation == DbImplem.MOTOR:
            return motor.motor_asyncio.AsyncIOMotorClient(str(config.storage.uri))
        return motor.motor_asyncio.AsyncIOMotorClient(mongod.connection_string)

    @provider
    @singleton
    def mock_client(self, config: MainSettings) -> mongomock_motor.AsyncMongoMockClient:
        if config.storage.implementation == DbImplem.FAKE:
            return mongomock_motor.AsyncMongoMockClient(
                "mongodb://example.com:27677/tutu"
            )
        raise NotImplementedError("No fake client available in real mode")

    @provider
    def database(
        self,
        config: MainSettings,
        client: motor.motor_asyncio.AsyncIOMotorClient,
        mongod: Mongod,
    ) -> motor.motor_asyncio.AsyncIOMotorDatabase:
        if config.storage.implementation == DbImplem.FAKE:
            raise NotImplementedError("No fake database available in real mode")

        # Ensure that the DB is started in case of local db
        if mongod:
            mongod.start()

        return client.get_database(config.storage.database)

    @provider
    def mock_database(
        self,
        config: MainSettings,
        client: mongomock_motor.AsyncMongoMockClient,
    ) -> mongomock_motor.AsyncMongoMockClient:
        if config.storage.implementation == DbImplem.FAKE:
            return client.get_database(config.storage.database)
        raise NotImplementedError("No real database available in fake mode")

    @provider
    @singleton
    def mongod(self, appdirs: AppDirs, config: MainSettings) -> Mongod:
        if not isinstance(config.storage, InMemorySettings):
            return None  # type: ignore

        context = MightstoneInMemoryContext(
            appdirs.user_data_dir, appdirs.user_cache_dir, str(config.storage.directory)
        )
        return Mongod(context)


class Httpx(Module):
    @provider
    @singleton
    def cache_backend(self, config: MainSettings, appdirs: AppDirs) -> BaseCache:
        if not config.http.cache.persist:
            return DictCache()

        if not config.http.cache.directory:
            logger.debug(
                "http cache directory is not defined, using mightstone cache directory"
            )
            config.http.cache.directory = pathlib.Path(appdirs.user_cache_dir).joinpath(
                "http"
            )

        if not config.http.cache.directory.exists():
            logger.warning(
                "http cache directory %s does not exist yet, attempting to create it",
                config.http.cache.directory,
            )
            os.makedirs(config.http.cache.directory)

        return FileCache(cache_dir=config.http.cache.directory)

    @provider
    @singleton
    def cache_transport(
        self, config: MainSettings, cache_backend: BaseCache
    ) -> AsyncCacheControlTransport:
        return AsyncCacheControlTransport(
            cache=cache_backend,
            cacheable_methods=tuple(config.http.cache.methods),
            cacheable_status_codes=tuple(config.http.cache.status),
        )


class Services(Module):
    @singleton
    @provider
    def rule_explorer(
        self,
        cache: AsyncCacheControlTransport,
        ijson: MightstoneIjsonBackend,
    ) -> RuleExplorer:
        return RuleExplorer(transport=cache, ijson=ijson)  # type: ignore

    @singleton
    @provider
    def scryfall(
        self,
        cache: AsyncCacheControlTransport,
        ijson: MightstoneIjsonBackend,
    ) -> Scryfall:
        return Scryfall(transport=cache, ijson=ijson)  # type: ignore

    @singleton
    @provider
    def edhrec_static(
        self,
        cache: AsyncCacheControlTransport,
        ijson: MightstoneIjsonBackend,
    ) -> EdhRecStatic:
        return EdhRecStatic(transport=cache, ijson=ijson)  # type: ignore

    @singleton
    @provider
    def edhrec_api(
        self,
        cache: AsyncCacheControlTransport,
        ijson: MightstoneIjsonBackend,
    ) -> EdhRecApi:
        return EdhRecApi(transport=cache, ijson=ijson)  # type: ignore

    @singleton
    @provider
    def card_conjurer(
        self,
        cache: AsyncCacheControlTransport,
        ijson: MightstoneIjsonBackend,
    ) -> CardConjurer:
        return CardConjurer(transport=cache, ijson=ijson)

    @singleton
    @provider
    def mtg_json(
        self,
        cache: AsyncCacheControlTransport,
        ijson: MightstoneIjsonBackend,
    ) -> MtgJson:
        return MtgJson(transport=cache, ijson=ijson)


class Configuration(Module):
    def configure(self, binder: Binder):
        binder.bind(MainSettings, scope=SingletonScope, to=lambda: MainSettings())


class Directories(Module):
    @provider
    @singleton
    def app_dirs(self, config: MainSettings) -> AppDirs:
        return AppDirs(config.appname)


modules = [JSON, Configuration, Directories, Storage, Httpx]

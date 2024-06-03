import logging
from typing import Optional, Union

import beanie
import httpx_cache
import mongomock_motor
import motor.motor_asyncio
from appdirs import AppDirs
from asgiref.sync import async_to_sync

from mightstone.config import DbImplem, MainSettings
from mightstone.core import get_documents
from mightstone.injector import CleanupInjector
from mightstone.services.cardconjurer import CardConjurer
from mightstone.services.edhrec import EdhRecApi, EdhRecStatic
from mightstone.services.mtgjson import MtgJson
from mightstone.services.scryfall import Scryfall
from mightstone.services.wotc import RuleExplorer
from mightstone.storage import Mongod

logger = logging.getLogger("mightstone")


class Mightstone:
    """
    A Mighstone instance

    Using python dependency injector, this class provides the services in an
    orderly fashion after setting up dependencies such as Beanie.
    """

    def __init__(self, config: Optional[Union[MainSettings, dict]] = None):
        from .container import modules

        self.container = CleanupInjector(modules)
        if config:
            if isinstance(config, dict):
                config = MainSettings.model_validate(config)
            self.container.binder.bind(MainSettings, config)
        self.beanie_init()

    @async_to_sync
    async def beanie_init(self) -> None:
        await beanie.init_beanie(
            database=self.mongo_database,
            document_models=get_documents(),
        )

    def __del__(self):
        self.container.cleanup()

    @property
    def config(self) -> MainSettings:
        return self.container.get(MainSettings)

    @property
    def app_dirs(self) -> AppDirs:
        return self.container.get(AppDirs)

    @property
    def mongo_client(
        self,
    ) -> Union[
        motor.motor_asyncio.AsyncIOMotorClient, mongomock_motor.AsyncMongoMockClient
    ]:
        if self.container.get(MainSettings).storage.implementation == DbImplem.FAKE:
            return self.container.get(mongomock_motor.AsyncMongoMockClient)
        return self.container.get(motor.motor_asyncio.AsyncIOMotorClient)

    @property
    def mongo_database(
        self,
    ) -> Union[
        motor.motor_asyncio.AsyncIOMotorDatabase, mongomock_motor.AsyncMongoMockDatabase
    ]:
        if self.container.get(MainSettings).storage.implementation == DbImplem.FAKE:
            return self.container.get(mongomock_motor.AsyncMongoMockDatabase)
        return self.container.get(motor.motor_asyncio.AsyncIOMotorDatabase)

    @property
    def mongo_server(self) -> Optional[Mongod]:
        return self.container.get(Mongod)

    @property
    def cache_transport(self) -> httpx_cache.AsyncCacheControlTransport:
        return self.container.get(httpx_cache.AsyncCacheControlTransport)

    @property
    def scryfall(self) -> Scryfall:
        return self.container.get(Scryfall)

    @property
    def mtg_json(self) -> MtgJson:
        return self.container.get(MtgJson)

    @property
    def card_conjurer(self) -> CardConjurer:
        return self.container.get(CardConjurer)

    @property
    def edhrec_api(self) -> EdhRecApi:
        return self.container.get(EdhRecApi)

    @property
    def edhrec_static(self) -> EdhRecStatic:
        return self.container.get(EdhRecStatic)

    @property
    def rule_explorer(self) -> RuleExplorer:
        return self.container.get(RuleExplorer)

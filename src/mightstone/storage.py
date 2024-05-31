import os
import tempfile
from typing import Optional

import pymongo_inmemory
from dependency_injector import containers
from pymongo_inmemory.context import Context


class MightstoneInMemoryContext(Context):
    def __init__(
        self,
        data_dir: Optional[str] = None,
        cache_dir: Optional[str] = None,
        database: Optional[str] = None,
    ) -> None:
        super().__init__()

        if not data_dir:
            data_dir = tempfile.TemporaryDirectory().name
        else:
            os.makedirs(os.path.join(data_dir, "mongo", "data"), exist_ok=True)

        if database:
            self.dbname = database

        self.mongo_version = "7.0"
        self.mongod_data_folder = os.path.join(data_dir, "mongo", "data")
        self.mongo_client_host = None
        self.storage_engine = "wiredTiger"

        if cache_dir:
            os.makedirs(os.path.join(cache_dir, "mongo", "download"), exist_ok=True)
            os.makedirs(os.path.join(cache_dir, "mongo", "extract"), exist_ok=True)
            os.makedirs(
                os.path.join(cache_dir, "mongo", "extract", self.url_hash),
                exist_ok=True,
            )
            os.makedirs(
                os.path.join(cache_dir, "mongo", "download", self.url_hash),
                exist_ok=True,
            )

            self.download_folder = os.path.join(cache_dir, "mongo", "extract")
            self.extract_folder = os.path.join(cache_dir, "mongo", "download")
            self.archive_folder = os.path.join(
                cache_dir, "mongo", "download", self.url_hash
            )
            self.extracted_folder = os.path.join(
                cache_dir, "mongo", "extract", self.url_hash
            )


class DatabaseDispatcher:
    def __init__(self, container: containers.Container):
        self.container = container

    def get_database(self):
        # Ensure that the DB is started in case of local db
        self.container.up.provided.call()

        client = self.container.client()
        dbname = self.container.config.database.required()()
        return client[dbname]


class Mongod(pymongo_inmemory.Mongod):
    def start(self):
        if self.is_locked:
            raise RuntimeError(
                "Mongo seems to be already running under another Mightstone instance. "
                "If you plan to use the storage concurrently, you should consider "
                "using a dedicated mongodb instance."
            )
        super().start()

    @staticmethod
    def generator(
        data_dir: str, cache_dir: Optional[str] = None, database: Optional[str] = None
    ):
        context = MightstoneInMemoryContext(data_dir, cache_dir, database)
        mongod = Mongod(context)
        yield mongod
        if mongod._proc:
            mongod.stop()

    @property
    def is_locked(self):
        lock_file = os.path.join(self.data_folder, "mongod.lock")
        if not os.path.exists(lock_file):
            return False

        return os.path.getsize(lock_file) != 0

import unittest
from tempfile import TemporaryDirectory

from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient

from mightstone.core import get_documents
from mightstone.storage import MightstoneInMemoryContext, Mongod


class TestBeanie(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self) -> None:
        self.tmpdir = TemporaryDirectory()
        context = MightstoneInMemoryContext(self.tmpdir.name)
        self.mongo = Mongod(context)
        self.mongo.start()
        self.client = AsyncIOMotorClient(self.mongo.connection_string)
        await init_beanie(database=self.client["foo"], document_models=get_documents())

    async def asyncTearDown(self) -> None:
        self.client.close()
        self.mongo.stop()
        self.tmpdir.cleanup()

import tempfile
import unittest

from beanie import init_beanie
from beanita import Client

from mightstone.core import get_documents


class TestBeanie(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.client = Client(self.temp_dir.name)
        await init_beanie(database=self.client["foo"], document_models=get_documents())

    async def asyncTearDown(self) -> None:
        self.client.close()
        self.temp_dir.cleanup()

import asyncio

import pytest
import pytest_asyncio
from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo_inmemory import Mongod
from pytest_asyncio import is_async_test

from mightstone.core import get_documents
from mightstone.storage import MightstoneInMemoryContext


def pytest_collection_modifyitems(items):
    pytest_asyncio_tests = (item for item in items if is_async_test(item))
    session_scope_marker = pytest.mark.asyncio(scope="session")
    for async_test in pytest_asyncio_tests:
        async_test.add_marker(session_scope_marker, append=False)


@pytest.fixture(scope="session")
def mongodb_in_memory():
    context = MightstoneInMemoryContext()
    with Mongod(context) as mongod:
        yield mongod


@pytest.fixture(scope="session")
def mongodb_test_connection_string(mongodb_in_memory):
    return mongodb_in_memory.connection_string


@pytest.fixture(scope="session")
def get_document_fixture():
    return get_documents()


@pytest_asyncio.fixture(scope="session")
async def init_beanie_fixture(mongodb_test_connection_string, get_document_fixture):
    client = AsyncIOMotorClient(mongodb_test_connection_string)
    await init_beanie(database=client["foo"], document_models=get_document_fixture)
    yield client
    client.close()

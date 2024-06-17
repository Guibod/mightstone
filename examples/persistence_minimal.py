import asyncio

from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo_inmemory import Mongod
from pymongo_inmemory.context import Context

from mightstone.services.scryfall import Scryfall, SerializableCard


async def run():
    # client = AsyncIOMotorClient("mongodb://user:pass@host:27017")
    with Mongod(Context()) as mongo_server:
        client = AsyncIOMotorClient(mongo_server.connection_string)

        models = [SerializableCard]  # or mightstone.core.get_documents()
        # Initialize beanie with the Product document class and a database
        await init_beanie(database=client.my_database, document_models=models)

        scryfall = Scryfall()
        random = await scryfall.random()

        await random.to_serializable().save()

        count = await SerializableCard.find().count()
        print(f"I now have {count} card in my database")


asyncio.run(run())

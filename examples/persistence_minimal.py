import asyncio

from beanie import init_beanie

# from motor.motor_asyncio import AsyncIOMotorClient
from beanita import Client

from mightstone.core import get_documents
from mightstone.services.scryfall import Card, Scryfall


async def run():
    # client = AsyncIOMotorClient("mongodb://user:pass@host:27017")
    client = Client()

    models = [Card]  # or mightstone.core.get_documents()
    # Initialize beanie with the Product document class and a database
    await init_beanie(database=client.my_database, document_models=models)

    scryfall = Scryfall()
    random = await scryfall.random_async()

    await random.save()

    count = await Card.find().count()
    print(f"I now have {count} card in my database")


asyncio.run(run())

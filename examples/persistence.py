import asyncio
import os
import tempfile

from mightstone.app import Mightstone
from mightstone.services.scryfall import Card


async def run(app: Mightstone):
    total = await Card.count()
    print(f"There are currently {total} cards in the database")
    async for res in app.scryfall.search_async("c:b cmc=2 o:destroy"):
        await res.save()

    total = await Card.count()
    print(f"We saved {total} cards in the database after our research")

    card = await Card.find_one()
    print(f"For instance, {card.name} with uuid {card.id} is in the database")

    queried = await app.scryfall.named_async(card.name)
    print(f"I can query it directly and find it again through the named endpoint")
    await queried.save()
    print(
        "As I save it, the unique key prevent it from being inserted again it will be "
        "updated "
    )

    after_total = await Card.count()
    print(f"There are still {after_total} in the database.")


with tempfile.TemporaryDirectory() as directory:
    os.environ["mightstone_db_uri"] = directory

    mightstone = Mightstone()
    asyncio.run(run(mightstone))

import asyncio

from mightstone.app import Mightstone

mightstone = Mightstone()


async def async_sample():
    items = []
    async for companion in mightstone.edhrec_static.companions_async():
        items.append(companion)
    return items


companions = asyncio.run(async_sample())
print(companions[0].name)

import asyncio

from mightstone.services.edhrec import EdhRecStatic

edhrec = EdhRecStatic()


async def async_sample():
    items = []
    async for companion in edhrec.companions_async():
        items.append(companion)
    return items


companions = asyncio.run(async_sample())
print(companions[0].name)

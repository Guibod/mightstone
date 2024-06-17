import asyncio

from mightstone.app import Mightstone


async def run(m: Mightstone):
    print("boseiju matches:")
    found = 0
    async for card in m.scryfall.search_async("boseiju"):
        found += 1
        print(f" - {card}")

    print(f"Found {found} instances of Boseiju")

    print("Thalia matches, without universalasync wrapper")
    print(list([x.name async for x in m.scryfall.search_async("thalia")]))


m = Mightstone()
asyncio.run(run(m))

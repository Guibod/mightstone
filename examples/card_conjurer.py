import asyncio

from mightstone.app import Mightstone


async def run(mightstone: Mightstone):
    cc = mightstone.card_conjurer
    card = await cc.card("../tests/services/cardconjurer/samples/Dimirova Smiley.json")  # type: ignore
    # You might need to define the remote server if the card was
    # remotely built and no asset are present locally
    card.asset_root_url = "https://card-conjurer-assets.s3.us-east-1.amazonaws.com"
    await cc.render(card, "my_card.png")  # type: ignore


mightstone = Mightstone()
asyncio.run(run(mightstone))

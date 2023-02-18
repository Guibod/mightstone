import asyncio

from mightstone.services.cardconjurer import CardConjurer

cc = CardConjurer()


async def run():
    card = await cc.card("my_card.json")
    # You might need to define the remote server if the card was
    # remotely built and no asset are present locally
    card.asset_root_url = "https://card-conjurer-assets.s3.us-east-1.amazonaws.com"
    await cc.render(card, "my_card.png")


asyncio.run(run())

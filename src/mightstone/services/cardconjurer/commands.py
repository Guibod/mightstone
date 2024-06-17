import asyncclick as click

from mightstone.cli.models import MightstoneCli, pass_mightstone
from mightstone.cli.utils import pretty_print

from .models import Card


@click.group()
@click.option("--cache", type=int, default=0)
def cardconjurer():
    pass


@cardconjurer.command()
@pass_mightstone
@click.argument("url_or_path")
async def card(cli: MightstoneCli, **kwargs):
    await pretty_print(await cli.app.card_conjurer.card_async(**kwargs), cli.format)


@cardconjurer.command()
@pass_mightstone
@click.argument("url_or_path")
async def template(cli: MightstoneCli, **kwargs):
    await pretty_print(await cli.app.card_conjurer.template_async(**kwargs), cli.format)


@cardconjurer.command()
@pass_mightstone
@click.argument("url_or_path")
@click.argument("output", type=click.File("wb"))
@click.option("--asset-root-url", type=str)
async def render(cli: MightstoneCli, url_or_path, output, asset_root_url):
    card_: Card = await cli.app.card_conjurer.card_async(url_or_path)  # type: ignore
    if asset_root_url:
        card_.asset_root_url = asset_root_url
    await cli.app.card_conjurer.render_async(card_, output)

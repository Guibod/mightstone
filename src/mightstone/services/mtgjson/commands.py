import asyncio

import asyncclick as click

from mightstone.cli.models import MightstoneCli, pass_mightstone
from mightstone.cli.utils import pretty_print
from mightstone.services.mtgjson import MtgJsonCompression


@click.group()
@pass_mightstone
@click.option(
    "--compression",
    type=click.Choice([t for t in MtgJsonCompression]),
    default=MtgJsonCompression.GZIP,
)
def mtgjson(cli: MightstoneCli, compression):
    cli.app.mtg_json.set_compression(compression)


@mtgjson.command()
@pass_mightstone
async def meta(cli: MightstoneCli):
    """Display the current version."""
    await pretty_print(await cli.app.mtg_json.meta_async(), cli.format)


@mtgjson.command()
@pass_mightstone
async def card_types(cli: MightstoneCli):
    """Display every card type of any type of card."""
    await pretty_print(await cli.app.mtg_json.card_types_async(), cli.format)


@mtgjson.command()
@pass_mightstone
@click.argument("code", type=str)
async def set(cli: MightstoneCli, **kwargs):
    """Display every card type of any type of card."""
    await pretty_print(await cli.app.mtg_json.set_async(**kwargs), cli.format)


@mtgjson.command()
@pass_mightstone
async def compiled_list(cli: MightstoneCli):
    """Display every card type of any type of card."""
    await pretty_print(await cli.app.mtg_json.compiled_list_async(), cli.format)


@mtgjson.command()
@pass_mightstone
async def keywords(cli: MightstoneCli):
    """Display every card type of any type of card."""
    await pretty_print(await cli.app.mtg_json.keywords_async(), cli.format)


@mtgjson.command()
@pass_mightstone
async def enum_values(cli: MightstoneCli):
    """Display every card type of any type of card."""
    await pretty_print(await cli.app.mtg_json.enum_values_async(), cli.format)

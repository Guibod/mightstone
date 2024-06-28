from typing import Union

import asyncclick as click

from mightstone.cli.models import MightstoneCli, pass_mightstone
from mightstone.cli.utils import pretty_print
from mightstone.services.edhrec.api import EnumIdentity, EnumPeriod
from mightstone.services.edhrec.models import EnumType, Page


def common_stream_options(function):
    function = click.option("--start", type=int)(function)
    function = click.option("--stop", type=int)(function)
    function = click.option("--step", type=int)(function)
    function = click.option("--parallel", type=int)(function)

    return function


async def show_simplified_page(page: Page, format):
    await pretty_print(
        {
            "title": page.container.title,
            "breadcrumb": page.container.breadcrumb,
            "collections": page.get_collection_names(),
            "card": page.card,
            "count": len(page.items) if page.items else 0,
            "mightstone_id": str(page.id),
        },
        format,
    )
    print("\n")


@click.group()
def edhrec():
    pass


@edhrec.command()
@pass_mightstone
@click.argument("name", nargs=1)
@click.argument("subtype", required=False)
async def commander(cli: MightstoneCli, **kwargs):
    await pretty_print(
        await cli.app.edhrec_static.commander_async(**kwargs), cli.format
    )


@edhrec.command()
@pass_mightstone
@common_stream_options
async def typals(cli: MightstoneCli, **kwargs):
    async for item in cli.app.edhrec_static.typals_stream_async(**kwargs):
        await show_simplified_page(item, cli.format)


@edhrec.command()
@pass_mightstone
@common_stream_options
async def themes(cli: MightstoneCli, **kwargs):
    async for item in cli.app.edhrec_static.themes_stream_async(**kwargs):
        await show_simplified_page(item, cli.format)


@edhrec.command()
@pass_mightstone
@click.argument("name", required=True)
async def set(cli: MightstoneCli, **kwargs):
    await pretty_print(await cli.app.edhrec_static.set_async(**kwargs), cli.format)


@edhrec.command()
@pass_mightstone
@common_stream_options
async def companions(cli: MightstoneCli, **kwargs):
    async for item in cli.app.edhrec_static.companions_stream_async(**kwargs):
        await show_simplified_page(item, cli.format)


@edhrec.command()
@pass_mightstone
@common_stream_options
async def partners(cli: MightstoneCli, **kwargs):
    async for item in cli.app.edhrec_static.companions_stream_async(**kwargs):
        await show_simplified_page(item, cli.format)


@edhrec.command()
@pass_mightstone
@common_stream_options
@click.option("-p", "--period", type=EnumPeriod)
@click.option("-i", "--identity", type=EnumIdentity)
async def commanders(cli: MightstoneCli, **kwargs):
    async for item in cli.app.edhrec_static.commanders_stream_async(**kwargs):
        await show_simplified_page(item, cli.format)


@edhrec.command()
@pass_mightstone
@common_stream_options
@click.argument("identity", type=click.Choice(EnumIdentity))  # type: ignore # click 2210
async def combos(cli: MightstoneCli, **kwargs):
    async for item in cli.app.edhrec_static.combos_stream_async(**kwargs):
        await show_simplified_page(item, cli.format)


@edhrec.command()
@pass_mightstone
@click.argument("identity", type=click.Choice(EnumIdentity))  # type: ignore # click 2210
@click.argument("combo_id", type=str)
async def combo(cli: MightstoneCli, **kwargs):
    await pretty_print(
        await cli.app.edhrec_static.combo_async(**kwargs),
        cli.format,
    )


@edhrec.command()
@pass_mightstone
@click.argument("year", required=False, type=int)
@common_stream_options
async def salt(cli: MightstoneCli, **kwargs):
    async for item in cli.app.edhrec_static.salt_stream_async(**kwargs):
        await show_simplified_page(item, cli.format)


@edhrec.command()
@pass_mightstone
@common_stream_options
@click.option("-t", "--type", type=click.Choice(EnumType))  # type: ignore # click 2210
@click.option("-p", "--period", type=click.Choice(EnumPeriod))  # type: ignore # click 2210
async def top_cards(cli: MightstoneCli, **kwargs):
    async for item in cli.app.edhrec_static.top_cards_stream_async(**kwargs):
        await show_simplified_page(item, cli.format)

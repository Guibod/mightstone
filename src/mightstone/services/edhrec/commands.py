import asyncclick as click

from mightstone.cli.models import MightstoneCli, pass_mightstone
from mightstone.cli.utils import pretty_print
from mightstone.services.edhrec.api import (
    EdhRecCategory,
    EdhRecIdentity,
    EdhRecPeriod,
    EdhRecType,
)


@click.group()
def edhrec():
    pass


@edhrec.command()
@pass_mightstone
@click.argument("name", nargs=1)
@click.argument("sub", required=False)
async def commander(cli: MightstoneCli, **kwargs):
    await pretty_print(
        await cli.app.edhrec_static.commander_async(**kwargs), cli.format
    )


@edhrec.command()
@pass_mightstone
@click.argument("identity", required=False)
@click.option("-l", "--limit", type=int)
async def typals(cli: MightstoneCli, **kwargs):
    await pretty_print(
        [typal async for typal in cli.app.edhrec_static.typals_async(**kwargs)],
        cli.format,
    )


@edhrec.command()
@pass_mightstone
@click.argument("identity", required=False)
@click.option("-l", "--limit", type=int)
async def themes(cli: MightstoneCli, **kwargs):
    await pretty_print(
        [theme async for theme in cli.app.edhrec_static.themes_async(**kwargs)],
        cli.format,
    )


@edhrec.command()
@pass_mightstone
@click.option("-l", "--limit", type=int)
async def sets(cli: MightstoneCli, **kwargs):
    await pretty_print(
        [s async for s in cli.app.edhrec_static.sets_async(**kwargs)], cli.format
    )


@edhrec.command()
@pass_mightstone
@click.option("-l", "--limit", type=int)
async def companions(cli: MightstoneCli, **kwargs):
    await pretty_print(
        [
            companion
            async for companion in cli.app.edhrec_static.companions_async(**kwargs)
        ],
        cli.format,
    )


@edhrec.command()
@pass_mightstone
@click.option("-i", "--identity", type=str)
@click.option("-l", "--limit", type=int)
async def partners(cli: MightstoneCli, **kwargs):
    await pretty_print(
        [partner async for partner in cli.app.edhrec_static.partners_async(**kwargs)],
        cli.format,
    )


@edhrec.command()
@pass_mightstone
@click.option("-i", "--identity", type=str)
@click.option("-l", "--limit", type=int, default=100)
async def commanders(cli: MightstoneCli, **kwargs):
    await pretty_print(
        [
            commander
            async for commander in cli.app.edhrec_static.commanders_async(**kwargs)
        ],
        cli.format,
    )


@edhrec.command()
@pass_mightstone
@click.argument("identity", type=click.Choice([t.value for t in EdhRecIdentity]))
@click.option("-l", "--limit", type=int, default=100)
async def combos(cli: MightstoneCli, **kwargs):
    await pretty_print(
        [combo async for combo in cli.app.edhrec_static.combos_async(**kwargs)],
        cli.format,
    )


@edhrec.command()
@pass_mightstone
@click.argument("identity", type=click.Choice([t.value for t in EdhRecIdentity]))
@click.argument("identifier", type=str)
@click.option("-l", "--limit", type=int, default=100)
async def combo(cli: MightstoneCli, **kwargs):
    await pretty_print(
        [combo async for combo in cli.app.edhrec_static.combo_async(**kwargs)],
        cli.format,
    )


@edhrec.command()
@pass_mightstone
@click.argument("year", required=False, type=int)
@click.option("-l", "--limit", type=int)
async def salt(cli: MightstoneCli, **kwargs):
    await pretty_print(
        [salt async for salt in cli.app.edhrec_static.salt_async(**kwargs)], cli.format
    )


@edhrec.command()
@pass_mightstone
@click.option("-t", "--type", type=click.Choice([t.value for t in EdhRecType]))
@click.option("-p", "--period", type=click.Choice([t.value for t in EdhRecPeriod]))
@click.option("-l", "--limit", type=int)
async def top_cards(cli: MightstoneCli, **kwargs):
    await pretty_print(
        [card async for card in cli.app.edhrec_static.top_cards_async(**kwargs)],
        cli.format,
    )


@edhrec.command()
@pass_mightstone
@click.option("-c", "--category", type=click.Choice([t.value for t in EdhRecCategory]))
@click.option("-t", "--theme", type=str)
@click.option("--commander", type=str)
@click.option("-i", "--identity", type=str)
@click.option("-s", "--set", type=str)
@click.option("-l", "--limit", type=int)
async def cards(cli: MightstoneCli, **kwargs):
    await pretty_print(
        [card async for card in cli.app.edhrec_static.cards_async(**kwargs)], cli.format
    )

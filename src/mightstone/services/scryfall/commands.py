from typing import Optional

import asyncclick as click

from mightstone.cli.models import MightstoneCli, pass_mightstone
from mightstone.cli.utils import catch_service_error, pretty_print
from mightstone.services.scryfall.models import (
    CardIdentifierPath,
    CatalogType,
    RulingIdentifierPath,
)


@click.group()
def scryfall():
    pass


@scryfall.command(name="sets")
@click.option("--limit", type=int)
@catch_service_error
@pass_mightstone
async def scryfall_sets(cli: MightstoneCli, **kwargs):
    await pretty_print(
        [s async for s in cli.app.scryfall.sets_async(**kwargs)],
        cli.format,
    )


@scryfall.command(name="set")
@click.argument("id_or_code", type=str)
@pass_mightstone
async def scryfall_set(cli: MightstoneCli, **kwargs):
    await pretty_print(await cli.app.scryfall.set_async(**kwargs), cli.format)


@scryfall.command()
@click.argument("id", type=str)
@click.argument(
    "type",
    type=click.Choice([i.value for i in CardIdentifierPath.__members__.values()]),
    default=CardIdentifierPath.SCRYFALL,
)
@catch_service_error
@pass_mightstone
async def card(cli: MightstoneCli, **kwargs):
    await pretty_print(await cli.app.scryfall.card_async(**kwargs), cli.format)


@scryfall.command()
@click.argument("q", type=str)
@click.option("--limit", type=int, default=100)
@catch_service_error
@pass_mightstone
async def search(cli: MightstoneCli, **kwargs):
    await pretty_print(
        [s async for s in cli.app.scryfall.search_async(**kwargs)],
        cli.format,
    )


@scryfall.command()
@click.argument("q", type=str, default="")
@catch_service_error
@pass_mightstone
async def random(cli: MightstoneCli, **kwargs):
    await pretty_print(await cli.app.scryfall.random_async(**kwargs), cli.format)


@scryfall.command()
@click.argument("q", type=str)
@click.option("--exact", type=bool, is_flag=True)
@click.option("--set", type=str)
@catch_service_error
@pass_mightstone
async def named(cli: MightstoneCli, **kwargs):
    await pretty_print(await cli.app.scryfall.named_async(**kwargs), cli.format)


@scryfall.command()
@click.argument("q", type=str)
@click.option("--include_extras", type=bool, is_flag=True)
@catch_service_error
@pass_mightstone
async def autocomplete(cli: MightstoneCli, **kwargs):
    await pretty_print(await cli.app.scryfall.autocomplete_async(**kwargs)), cli.format


class ScryfallIdentifier(click.ParamType):
    name = "identifier"

    def convert(self, value, param, ctx):
        item = {}
        for constraint in value.split(","):
            (key, value) = constraint.split(":", 1)
            item[key] = value
        return item


@scryfall.command()
@click.argument("identifiers", nargs=-1, type=ScryfallIdentifier())
@catch_service_error
@pass_mightstone
async def collection(cli: MightstoneCli, **kwargs):
    """
    scryfall collection id:683a5707-cddb-494d-9b41-51b4584ded69 "name:Ancient tomb"
    "set:dmu,collector_number:150"

    :param obj:
    :param kwargs:
    :return:
    """
    await pretty_print(
        [s async for s in cli.app.scryfall.collection_async(**kwargs)],
        cli.format,
    )


@scryfall.command()
@click.argument("id", type=str)
@click.argument("type", type=click.Choice([t.value for t in RulingIdentifierPath]))
@click.option("-l", "--limit", type=int)
@catch_service_error
@pass_mightstone
async def rulings(cli: MightstoneCli, **kwargs):
    await pretty_print(
        [s async for s in cli.app.scryfall.rulings_async(**kwargs)],
        cli.format,
    )


@scryfall.command()
@click.option("-l", "--limit", type=int, required=False)
@catch_service_error
@pass_mightstone
async def symbols(cli: MightstoneCli, **kwargs):
    await pretty_print(
        [s async for s in cli.app.scryfall.symbols_async(**kwargs)],
        cli.format,
    )


@scryfall.command()
@click.argument("cost", type=str)
@catch_service_error
@pass_mightstone
async def parse_mana(cli: MightstoneCli, **kwargs):
    await pretty_print(await cli.app.scryfall.parse_mana_async(**kwargs), cli.format)


@scryfall.command()
@click.argument("type", type=click.Choice([t.value for t in CatalogType]))
@catch_service_error
@pass_mightstone
async def catalog(cli: MightstoneCli, **kwargs):
    await pretty_print(await cli.app.scryfall.catalog_async(**kwargs), cli.format)


@scryfall.command()
@click.option("-l", "--limit", type=int, default=100)
@catch_service_error
@pass_mightstone
async def migrations(cli: MightstoneCli, **kwargs):
    await pretty_print(
        [s async for s in cli.app.scryfall.migrations_async(**kwargs)],
        cli.format,
    )


@scryfall.command()
@click.argument("id", type=str)
@catch_service_error
@pass_mightstone
async def migration(cli: MightstoneCli, **kwargs):
    await pretty_print(await cli.app.scryfall.migration_async(**kwargs), cli.format)

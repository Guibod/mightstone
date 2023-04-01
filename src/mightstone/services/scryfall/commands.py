import click

from mightstone.ass import aiterator_to_list
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
def scryfall_sets(cli: MightstoneCli, **kwargs):
    pretty_print(
        aiterator_to_list(cli.app.scryfall.sets_async(**kwargs)),
        cli.format,
    )


@scryfall.command(name="set")
@click.argument("id_or_code", type=str)
@pass_mightstone
def scryfall_set(cli: MightstoneCli, **kwargs):
    pretty_print(cli.app.scryfall.set(**kwargs), cli.format)


@scryfall.command()
@click.argument("id", type=str)
@click.argument("type", type=click.Choice([t.value for t in CardIdentifierPath]))
@catch_service_error
@pass_mightstone
def card(cli: MightstoneCli, **kwargs):
    pretty_print(cli.app.scryfall.card(**kwargs), cli.format)


@scryfall.command()
@click.argument("q", type=str)
@click.option("--limit", type=int, default=100)
@catch_service_error
@pass_mightstone
def search(cli: MightstoneCli, **kwargs):
    pretty_print(
        aiterator_to_list(cli.app.scryfall.search_async(**kwargs)),
        cli.format,
    )


@scryfall.command()
@click.argument("q", type=str)
@catch_service_error
@pass_mightstone
def random(cli: MightstoneCli, **kwargs):
    pretty_print(cli.app.scryfall.random(**kwargs), cli.format)


@scryfall.command()
@click.argument("q", type=str)
@click.option("--exact", type=bool, is_flag=True)
@click.option("--set", type=str)
@catch_service_error
@pass_mightstone
def named(cli: MightstoneCli, **kwargs):
    pretty_print(cli.app.scryfall.named(**kwargs), cli.format)


@scryfall.command()
@click.argument("q", type=str)
@click.option("--include_extras", type=bool, is_flag=True)
@catch_service_error
@pass_mightstone
def autocomplete(cli: MightstoneCli, **kwargs):
    pretty_print(cli.app.scryfall.autocomplete(**kwargs)), cli.format


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
def collection(cli: MightstoneCli, **kwargs):
    """
    scryfall collection id:683a5707-cddb-494d-9b41-51b4584ded69 "name:Ancient tomb"
    "set:dmu,collector_number:150"

    :param obj:
    :param kwargs:
    :return:
    """
    pretty_print(
        aiterator_to_list(cli.app.scryfall.collection_async(**kwargs)),
        cli.format,
    )


@scryfall.command()
@click.argument("id", type=str)
@click.argument("type", type=click.Choice([t.value for t in RulingIdentifierPath]))
@click.option("-l", "--limit", type=int)
@catch_service_error
@pass_mightstone
def rulings(cli: MightstoneCli, **kwargs):
    pretty_print(
        aiterator_to_list(cli.app.scryfall.rulings_async(**kwargs)),
        cli.format,
    )


@scryfall.command()
@click.option("-l", "--limit", type=int, required=False)
@catch_service_error
@pass_mightstone
def symbols(cli: MightstoneCli, **kwargs):
    pretty_print(
        aiterator_to_list(cli.app.scryfall.symbols_async(**kwargs)),
        cli.format,
    )


@scryfall.command()
@click.argument("cost", type=str)
@catch_service_error
@pass_mightstone
def parse_mana(cli: MightstoneCli, **kwargs):
    pretty_print(cli.app.scryfall.parse_mana(**kwargs), cli.format)


@scryfall.command()
@click.argument("type", type=click.Choice([t.value for t in CatalogType]))
@catch_service_error
@pass_mightstone
def catalog(cli: MightstoneCli, **kwargs):
    pretty_print(cli.app.scryfall.catalog(**kwargs), cli.format)


@scryfall.command()
@click.option("-l", "--limit", type=int, default=100)
@catch_service_error
@pass_mightstone
def migrations(cli: MightstoneCli, **kwargs):
    pretty_print(
        aiterator_to_list(cli.app.scryfall.migrations_async(**kwargs)),
        cli.format,
    )


@scryfall.command()
@click.argument("id", type=str)
@catch_service_error
@pass_mightstone
def migration(cli: MightstoneCli, **kwargs):
    pretty_print(cli.app.scryfall.migration(**kwargs), cli.format)

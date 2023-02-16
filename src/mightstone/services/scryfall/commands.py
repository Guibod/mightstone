from typing import TypedDict

import click

from mightstone.ass import asyncio_run, stream_as_list
from mightstone.cli.utils import catch_service_error, pretty_print
from mightstone.services.scryfall import (
    CardIdentifierPath,
    CatalogType,
    RulingIdentifierPath,
    Scryfall,
)


class ScryfallObj(TypedDict):
    client: Scryfall
    format: str


@click.group()
@click.pass_obj
@click.option("--cache", type=int, default=0)
def scryfall(obj: ScryfallObj, **kwargs):
    obj["client"] = Scryfall(**kwargs)


@scryfall.command(name="sets")
@click.pass_obj
@click.option("--limit", type=int)
@catch_service_error
def scryfall_sets(obj: ScryfallObj, **kwargs):
    pretty_print(stream_as_list(obj["client"].sets(**kwargs)), obj.get("format"))


@scryfall.command(name="set")
@click.pass_obj
@click.argument("id_or_code", type=str)
def scryfall_set(obj: ScryfallObj, **kwargs):
    pretty_print(asyncio_run(obj["client"].set(**kwargs)), obj.get("format"))


@scryfall.command()
@click.pass_obj
@click.argument("id", type=str)
@click.argument("type", type=click.Choice([t.value for t in CardIdentifierPath]))
@catch_service_error
def card(obj: ScryfallObj, **kwargs):
    pretty_print(asyncio_run(obj["client"].card(**kwargs)), obj.get("format"))


@scryfall.command()
@click.pass_obj
@click.argument("q", type=str)
@click.option("--limit", type=int, default=100)
@catch_service_error
def search(obj: ScryfallObj, **kwargs):
    pretty_print(stream_as_list(obj["client"].search(**kwargs)), obj.get("format"))


@scryfall.command()
@click.pass_obj
@click.argument("q", type=str)
@catch_service_error
def random(obj: ScryfallObj, **kwargs):
    pretty_print(asyncio_run(obj["client"].random(**kwargs)), obj.get("format"))


@scryfall.command()
@click.pass_obj
@click.argument("q", type=str)
@click.option("--exact", type=bool, is_flag=True)
@click.option("--set", type=str)
@catch_service_error
def named(obj: ScryfallObj, **kwargs):
    pretty_print(asyncio_run(obj["client"].named(**kwargs)), obj.get("format"))


@scryfall.command()
@click.pass_obj
@click.argument("q", type=str)
@click.option("--include_extras", type=bool, is_flag=True)
@catch_service_error
def autocomplete(obj: ScryfallObj, **kwargs):
    pretty_print(asyncio_run(obj["client"].autocomplete(**kwargs)), obj.get("format"))


class ScryfallIdentifier(click.ParamType):
    name = "identifier"

    def convert(self, value, param, ctx):
        item = {}
        for constraint in value.split(","):
            (key, value) = constraint.split(":", 1)
            item[key] = value
        return item


@scryfall.command()
@click.pass_obj
@click.argument("identifiers", nargs=-1, type=ScryfallIdentifier())
@catch_service_error
def collection(obj: ScryfallObj, **kwargs):
    """
    scryfall collection id:683a5707-cddb-494d-9b41-51b4584ded69 "name:Ancient tomb"
    "set:dmu,collector_number:150"

    :param obj:
    :param kwargs:
    :return:
    """
    pretty_print(stream_as_list(obj["client"].collection(**kwargs)), obj.get("format"))


@scryfall.command()
@click.pass_obj
@click.argument("id", type=str)
@click.argument("type", type=click.Choice([t.value for t in RulingIdentifierPath]))
@click.option("-l", "--limit", type=int)
@catch_service_error
def rulings(obj: ScryfallObj, **kwargs):
    pretty_print(stream_as_list(obj["client"].rulings(**kwargs)), obj.get("format"))


@scryfall.command()
@click.pass_obj
@click.option("-l", "--limit", type=int, required=False)
@catch_service_error
def symbols(obj: ScryfallObj, **kwargs):
    pretty_print(stream_as_list(obj["client"].symbols(**kwargs)), obj.get("format"))


@scryfall.command()
@click.pass_obj
@click.argument("cost", type=str)
@catch_service_error
def parse_mana(obj: ScryfallObj, **kwargs):
    pretty_print(asyncio_run(obj["client"].parse_mana(**kwargs)), obj.get("format"))


@scryfall.command()
@click.pass_obj
@click.argument("type", type=click.Choice([t.value for t in CatalogType]))
@catch_service_error
def catalog(obj: ScryfallObj, **kwargs):
    pretty_print(asyncio_run(obj["client"].catalog(**kwargs)), obj.get("format"))


@scryfall.command()
@click.pass_obj
@click.option("-l", "--limit", type=int, default=100)
@catch_service_error
def migrations(obj: ScryfallObj, **kwargs):
    pretty_print(stream_as_list(obj["client"].migrations(**kwargs)), obj.get("format"))


@scryfall.command()
@click.pass_obj
@click.argument("id", type=str)
@catch_service_error
def migration(obj: ScryfallObj, **kwargs):
    pretty_print(asyncio_run(obj["client"].migration(**kwargs)), obj.get("format"))

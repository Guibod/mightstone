import json
import logging
import sys
from functools import partial, wraps

import click
import yaml
from pydantic.json import pydantic_encoder

import mightstone
from mightstone.ass import asyncio_run, stream_as_list
from mightstone.services import ServiceError
from mightstone.services.edhrec import (
    EdhRecCategory,
    EdhRecIdentity,
    EdhRecPeriod,
    EdhRecStatic,
    EdhRecType,
)
from mightstone.services.scryfall import (
    CardIdentifierPath,
    CatalogType,
    RulingIdentifierPath,
    Scryfall,
)

logger = logging.getLogger("mightstone")


def pretty_print(data, format="yaml"):
    from pygments import highlight
    from pygments.formatters import TerminalFormatter
    from pygments.lexers import JsonLexer, YamlLexer

    datastr = json.dumps(data, indent=2, sort_keys=True, default=pydantic_encoder)
    formatter = TerminalFormatter()
    if format == "json":
        lexer = JsonLexer()
    else:
        lexer = YamlLexer()
        datastr = yaml.dump(json.loads(datastr), indent=2)  # Yes, that’s that bad

    if sys.stdout.isatty():
        highlight(datastr, lexer, formatter, outfile=sys.stdout)
    else:
        sys.stdout.write(datastr)


def catch_service_error(func=None):
    if not func:
        return partial(catch_service_error)

    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ServiceError as e:
            raise click.ClickException(f"{e.message}, at {e.method} {e.url}")

    return wrapper


@click.group()
@click.pass_context
@click.option("-f", "--format", type=click.Choice(["json", "yaml"]), default="json")
@click.option("-v", "--verbose", count=True)
@click.option("-l", "--log-level", default="ERROR", envvar="LOG_LEVEL")
def cli(ctx, format, verbose, log_level):
    if verbose:
        log_level = logging.WARNING
    if verbose > 1:
        log_level = logging.INFO
    if verbose > 2:
        log_level = logging.DEBUG

    ctx.ensure_object(dict)
    ctx.obj["format"] = format

    logging.basicConfig(
        level=log_level,
        format="[%(name)s] %(levelname)s - %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%S",
    )
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("asyncio").setLevel(logging.WARNING)


@cli.command()
@click.option("-v", "--verbose", count=True)
def version(verbose):
    """Displays the version"""
    click.echo("Version: %s" % mightstone.__version__)
    if verbose > 0:
        click.echo("Author: %s" % mightstone.__author__)


@cli.group()
def scryfall():
    ...


@scryfall.command(name="sets")
@click.pass_obj
@click.option("--limit", type=int)
@catch_service_error
def scryfall_sets(obj, **kwargs):
    with Scryfall() as client:
        pretty_print(stream_as_list(client.sets(**kwargs)), obj.get("format"))


@scryfall.command(name="set")
@click.pass_obj
@click.argument("id_or_code", type=str)
def scryfall_set(obj, **kwargs):
    with Scryfall() as client:
        pretty_print(asyncio_run(client.set(**kwargs)), obj.get("format"))


@scryfall.command()
@click.pass_obj
@click.argument("id", type=str)
@click.argument("type", type=click.Choice([t.value for t in CardIdentifierPath]))
@catch_service_error
def card(obj, **kwargs):
    with Scryfall() as client:
        pretty_print(asyncio_run(client.card(**kwargs)), obj.get("format"))


@scryfall.command()
@click.pass_obj
@click.argument("q", type=str)
@click.option("--limit", type=int, default=100)
@catch_service_error
def search(obj, **kwargs):
    with Scryfall() as client:
        pretty_print(stream_as_list(client.search(**kwargs)), obj.get("format"))


@scryfall.command()
@click.pass_obj
@click.argument("q", type=str)
@catch_service_error
def random(obj, **kwargs):
    with Scryfall() as client:
        pretty_print(asyncio_run(client.random(**kwargs)), obj.get("format"))


@scryfall.command()
@click.pass_obj
@click.argument("q", type=str)
@click.option("--exact", type=bool, is_flag=True)
@click.option("--set", type=str)
@catch_service_error
def named(obj, **kwargs):
    with Scryfall() as client:
        pretty_print(asyncio_run(client.named(**kwargs)), obj.get("format"))


@scryfall.command()
@click.pass_obj
@click.argument("q", type=str)
@click.option("--include_extras", type=bool, is_flag=True)
@catch_service_error
def autocomplete(obj, **kwargs):
    with Scryfall() as client:
        pretty_print(asyncio_run(client.autocomplete(**kwargs)), obj.get("format"))


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
def collection(obj, **kwargs):
    """
    scryfall collection id:683a5707-cddb-494d-9b41-51b4584ded69 "name:Ancient tomb"
    "set:dmu,collector_number:150"

    :param obj:
    :param kwargs:
    :return:
    """
    with Scryfall() as client:
        pretty_print(stream_as_list(client.collection(**kwargs)), obj.get("format"))


@scryfall.command()
@click.pass_obj
@click.argument("id", type=str)
@click.argument("type", type=click.Choice([t.value for t in RulingIdentifierPath]))
@click.option("-l", "--limit", type=int)
@catch_service_error
def rulings(obj, **kwargs):
    with Scryfall() as client:
        pretty_print(stream_as_list(client.rulings(**kwargs)), obj.get("format"))


@scryfall.command()
@click.pass_obj
@click.option("-l", "--limit", type=int, required=False)
@catch_service_error
def symbols(obj, **kwargs):
    with Scryfall() as client:
        pretty_print(stream_as_list(client.symbols(**kwargs)), obj.get("format"))


@scryfall.command()
@click.pass_obj
@click.argument("cost", type=str)
@catch_service_error
def parse_mana(obj, **kwargs):
    with Scryfall() as client:
        pretty_print(asyncio_run(client.parse_mana(**kwargs)), obj.get("format"))


@scryfall.command()
@click.pass_obj
@click.argument("type", type=click.Choice([t.value for t in CatalogType]))
@catch_service_error
def catalog(obj, **kwargs):
    with Scryfall() as client:
        pretty_print(asyncio_run(client.catalog(**kwargs)), obj.get("format"))


@scryfall.command()
@click.pass_obj
@click.option("-l", "--limit", type=int, default=100)
@catch_service_error
def migrations(obj, **kwargs):
    with Scryfall() as client:
        pretty_print(stream_as_list(client.migrations(**kwargs)), obj.get("format"))


@scryfall.command()
@click.pass_obj
@click.argument("id", type=str)
@catch_service_error
def migration(obj, **kwargs):
    with Scryfall() as client:
        pretty_print(asyncio_run(client.migration(**kwargs)), obj.get("format"))


@cli.group()
def edhrec():
    ...


@edhrec.command()
@click.pass_obj
@click.argument("name", nargs=1)
@click.argument("sub", required=False)
def commander(obj, **kwargs):
    with EdhRecStatic() as client:
        pretty_print(asyncio_run(client.commander(**kwargs)), obj.get("format"))


@edhrec.command()
@click.pass_obj
@click.argument("identity", required=False)
@click.option("-l", "--limit", type=int)
def tribes(obj, **kwargs):
    with EdhRecStatic() as client:
        pretty_print(stream_as_list(client.tribes(**kwargs)), obj.get("format"))


@edhrec.command()
@click.pass_obj
@click.argument("identity", required=False)
@click.option("-l", "--limit", type=int)
def themes(obj, **kwargs):
    with EdhRecStatic() as client:
        pretty_print(stream_as_list(client.themes(**kwargs)), obj.get("format"))


@edhrec.command()
@click.pass_obj
@click.option("-l", "--limit", type=int)
def sets(obj, **kwargs):
    with EdhRecStatic() as client:
        pretty_print(stream_as_list(client.sets(**kwargs)), obj.get("format"))


@edhrec.command()
@click.pass_obj
@click.option("-l", "--limit", type=int)
def companions(obj, **kwargs):
    with EdhRecStatic() as client:
        pretty_print(stream_as_list(client.companions(**kwargs)), obj.get("format"))


@edhrec.command()
@click.pass_obj
@click.option("-i", "--identity", type=str)
@click.option("-l", "--limit", type=int)
def partners(obj, **kwargs):
    with EdhRecStatic() as client:
        pretty_print(stream_as_list(client.partners(**kwargs)), obj.get("format"))


@edhrec.command()
@click.pass_obj
@click.option("-i", "--identity", type=str)
@click.option("-l", "--limit", type=int, default=100)
def commanders(obj, **kwargs):
    with EdhRecStatic() as client:
        pretty_print(stream_as_list(client.commanders(**kwargs)), obj.get("format"))


@edhrec.command()
@click.pass_obj
@click.argument("identity", type=click.Choice([t.value for t in EdhRecIdentity]))
@click.option("-l", "--limit", type=int, default=100)
def combos(obj, **kwargs):
    with EdhRecStatic() as client:
        pretty_print(stream_as_list(client.combos(**kwargs)), obj.get("format"))


@edhrec.command()
@click.pass_obj
@click.argument("identity", type=click.Choice([t.value for t in EdhRecIdentity]))
@click.argument("identifier", type=str)
@click.option("-l", "--limit", type=int, default=100)
def combo(obj, **kwargs):
    with EdhRecStatic() as client:
        pretty_print(stream_as_list(client.combo(**kwargs)), obj.get("format"))


@edhrec.command()
@click.pass_obj
@click.argument("year", required=False, type=int)
@click.option("-l", "--limit", type=int)
def salt(obj, **kwargs):
    with EdhRecStatic() as client:
        pretty_print(stream_as_list(client.salt(**kwargs)), obj.get("format"))


@edhrec.command()
@click.pass_obj
@click.option("-t", "--type", type=click.Choice([t.value for t in EdhRecType]))
@click.option("-p", "--period", type=click.Choice([t.value for t in EdhRecPeriod]))
@click.option("-l", "--limit", type=int)
def top_cards(obj, **kwargs):
    with EdhRecStatic() as client:
        pretty_print(stream_as_list(client.top_cards(**kwargs)), obj.get("format"))


@edhrec.command()
@click.pass_obj
@click.option("-c", "--category", type=click.Choice([t.value for t in EdhRecCategory]))
@click.option("-t", "--theme", type=str)
@click.option("--commander", type=str)
@click.option("-i", "--identity", type=str)
@click.option("-s", "--set", type=str)
@click.option("-l", "--limit", type=int)
def cards(obj, **kwargs):
    logger.info(f"Searching top cards using for type {kwargs}")
    with EdhRecStatic() as client:
        pretty_print(stream_as_list(client.cards(**kwargs)), obj.get("format"))


if __name__ == "__main__":
    cli()

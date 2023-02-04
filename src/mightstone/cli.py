import json
import logging
import sys

import click
import yaml
from pydantic.json import pydantic_encoder

import mightstone
from mightstone.ass import asyncio_run, stream_as_list
from mightstone.services.edhrec import (
    EdhRecCategory,
    EdhRecIdentity,
    EdhRecPeriod,
    EdhRecStatic,
    EdhRecType,
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
    logging.debug("debug")
    logging.error("error")
    logging.fatal("fatal")


@cli.command()
@click.option("-v", "--verbose", count=True)
def version(verbose):
    """Displays the version"""
    click.echo("Version: %s" % mightstone.__version__)
    if verbose > 0:
        click.echo("Author: %s" % mightstone.__author__)


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

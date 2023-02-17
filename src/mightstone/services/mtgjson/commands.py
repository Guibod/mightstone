import asyncio
from typing import TypedDict

import click

from mightstone.cli.utils import pretty_print
from mightstone.services.mtgjson import MtgJson, MtgJsonCompression


class MtgJsonObj(TypedDict):
    client: MtgJson


@click.group()
@click.pass_obj
@click.option("--cache", type=int, default=0)
@click.option(
    "--compression",
    type=click.Choice([t.value for t in MtgJsonCompression]),
    default=MtgJsonCompression.GZIP,
)
def mtgjson(obj, **kwargs):
    obj["client"] = MtgJson(**kwargs)


@mtgjson.command()
@click.pass_obj
def meta(obj: MtgJsonObj):
    """Display the current version."""
    pretty_print(asyncio.run(obj["client"].meta()))


@mtgjson.command()
@click.pass_obj
def card_types(obj: MtgJsonObj):
    """Display every card type of any type of card."""
    pretty_print(asyncio.run(obj["client"].card_types()))


@mtgjson.command()
@click.pass_obj
@click.argument("code", type=str)
def set(obj: MtgJsonObj, **kwargs):
    """Display every card type of any type of card."""
    pretty_print(asyncio.run(obj["client"].set(**kwargs)))


@mtgjson.command()
@click.pass_obj
def compiled_list(obj: MtgJsonObj):
    """Display every card type of any type of card."""
    pretty_print(asyncio.run(obj["client"].compiled_list()))


@mtgjson.command()
@click.pass_obj
def keywords(obj: MtgJsonObj):
    """Display every card type of any type of card."""
    pretty_print(asyncio.run(obj["client"].keywords()))


@mtgjson.command()
@click.pass_obj
def enum_values(obj: MtgJsonObj):
    """Display every card type of any type of card."""
    pretty_print(asyncio.run(obj["client"].enum_values()))

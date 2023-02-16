from typing import TypedDict

import click

import mightstone
from mightstone.ass import asyncio_run, stream_as_list
from mightstone.cli.utils import pretty_print
from mightstone.services.edhrec import (
    EdhRecCategory,
    EdhRecIdentity,
    EdhRecPeriod,
    EdhRecStatic,
    EdhRecType,
)


class EdhRecObj(TypedDict):
    static: EdhRecStatic
    client: EdhRecStatic
    format: str


@click.group()
@click.pass_obj
@click.option("--cache", type=int, default=0)
def edhrec(obj, **kwargs):
    obj["static"] = EdhRecStatic(**kwargs)


@edhrec.command()
@click.pass_obj
@click.argument("name", nargs=1)
@click.argument("sub", required=False)
def commander(obj: EdhRecObj, **kwargs):
    pretty_print(asyncio_run(obj["static"].commander(**kwargs)), obj.get("format"))


@edhrec.command()
@click.pass_obj
@click.argument("identity", required=False)
@click.option("-l", "--limit", type=int)
def tribes(obj: EdhRecObj, **kwargs):
    pretty_print(stream_as_list(obj["static"].tribes(**kwargs)), obj.get("format"))


@edhrec.command()
@click.pass_obj
@click.argument("identity", required=False)
@click.option("-l", "--limit", type=int)
def themes(obj: EdhRecObj, **kwargs):
    pretty_print(stream_as_list(obj["static"].themes(**kwargs)), obj.get("format"))


@edhrec.command()
@click.pass_obj
@click.option("-l", "--limit", type=int)
def sets(obj: EdhRecObj, **kwargs):
    pretty_print(stream_as_list(obj["static"].sets(**kwargs)), obj.get("format"))


@edhrec.command()
@click.pass_obj
@click.option("-l", "--limit", type=int)
def companions(obj: EdhRecObj, **kwargs):
    pretty_print(stream_as_list(obj["static"].companions(**kwargs)), obj.get("format"))


@edhrec.command()
@click.pass_obj
@click.option("-i", "--identity", type=str)
@click.option("-l", "--limit", type=int)
def partners(obj: EdhRecObj, **kwargs):
    pretty_print(stream_as_list(obj["static"].partners(**kwargs)), obj.get("format"))


@edhrec.command()
@click.pass_obj
@click.option("-i", "--identity", type=str)
@click.option("-l", "--limit", type=int, default=100)
def commanders(obj: EdhRecObj, **kwargs):
    pretty_print(stream_as_list(obj["static"].commanders(**kwargs)), obj.get("format"))


@edhrec.command()
@click.pass_obj
@click.argument("identity", type=click.Choice([t.value for t in EdhRecIdentity]))
@click.option("-l", "--limit", type=int, default=100)
def combos(obj: EdhRecObj, **kwargs):
    pretty_print(stream_as_list(obj["static"].combos(**kwargs)), obj.get("format"))


@edhrec.command()
@click.pass_obj
@click.argument("identity", type=click.Choice([t.value for t in EdhRecIdentity]))
@click.argument("identifier", type=str)
@click.option("-l", "--limit", type=int, default=100)
def combo(obj: EdhRecObj, **kwargs):
    pretty_print(stream_as_list(obj["static"].combo(**kwargs)), obj.get("format"))


@edhrec.command()
@click.pass_obj
@click.argument("year", required=False, type=int)
@click.option("-l", "--limit", type=int)
def salt(obj: EdhRecObj, **kwargs):
    pretty_print(stream_as_list(obj["static"].salt(**kwargs)), obj.get("format"))


@edhrec.command()
@click.pass_obj
@click.option("-t", "--type", type=click.Choice([t.value for t in EdhRecType]))
@click.option("-p", "--period", type=click.Choice([t.value for t in EdhRecPeriod]))
@click.option("-l", "--limit", type=int)
def top_cards(obj: EdhRecObj, **kwargs):
    pretty_print(stream_as_list(obj["static"].top_cards(**kwargs)), obj.get("format"))


@edhrec.command()
@click.pass_obj
@click.option("-c", "--category", type=click.Choice([t.value for t in EdhRecCategory]))
@click.option("-t", "--theme", type=str)
@click.option("--commander", type=str)
@click.option("-i", "--identity", type=str)
@click.option("-s", "--set", type=str)
@click.option("-l", "--limit", type=int)
def cards(obj, **kwargs):
    mightstone.logger.info(f"Searching top cards using for type {kwargs}")
    pretty_print(stream_as_list(obj["static"].cards(**kwargs)), obj.get("format"))

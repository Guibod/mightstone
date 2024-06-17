import importlib
from pathlib import Path

import asyncclick as click
from pydantic_core._pydantic_core import Url

from mightstone.cli.models import MightstoneCli, pass_mightstone


@click.group()
def wiki():
    pass


@wiki.group()
def scrape(): ...


module = importlib.import_module("mightstone.rule.data")
default_output = Path(module.__path__[0]).joinpath("abilities.json")


@scrape.command()
@click.argument("output", type=click.File("w"), default=default_output)
@pass_mightstone
async def abilities(mightstone: MightstoneCli, output: click.utils.LazyFile):
    print("Building abilities from mtg wiki...")
    abilities = await mightstone.app.wiki.scrape_abilities_async()

    print("Saving informations...")
    output.write(abilities.model_dump_json(indent=2))
    print(f"{len(abilities.abilities)} abilities saved into {output.name}")

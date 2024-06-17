import importlib
from pathlib import Path
from typing import Optional

import asyncclick as click

from mightstone.cli.models import MightstoneCli, pass_mightstone
from mightstone.services.wotc import ComprehensiveRules


@click.group()
def wotc():
    pass


@wotc.group()
def scrape(): ...


module = importlib.import_module("mightstone.rule.data")
default_output = Path(module.__path__[0]).joinpath("rules.json")


@scrape.command()
@click.option("--url", "-U", type=str, default=None)
@click.argument("output", type=click.File("w"), default=default_output)
@pass_mightstone
async def rules(
    mightstone: MightstoneCli, url: Optional[str], output: click.utils.LazyFile
):
    print("Building rules from mtg website...")
    rules: ComprehensiveRules = await mightstone.app.rule_explorer.open_async(url)  # type: ignore

    print("Saving informations...")
    output.write(rules.model_dump_json(indent=2))
    print(f"Rules saved into {output.name}")

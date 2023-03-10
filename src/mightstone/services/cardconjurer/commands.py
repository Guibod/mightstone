from typing import TypedDict

import click

from mightstone.cli.utils import pretty_print
from mightstone.containers import Container
from mightstone.services.cardconjurer import CardConjurer


class CardConjurerObj(TypedDict):
    container: Container
    client: CardConjurer
    format: str


@click.group()
@click.pass_obj
@click.option("--cache", type=int, default=0)
def cardconjurer(obj: CardConjurerObj, **kwargs):
    obj["client"] = obj["container"].card_conjurer(**kwargs)


@cardconjurer.command()
@click.pass_obj
@click.argument("url_or_path")
def card(obj: CardConjurerObj, **kwargs):
    pretty_print(obj["client"].card(**kwargs), obj.get("format"))


@cardconjurer.command()
@click.pass_obj
@click.argument("url_or_path")
def template(obj: CardConjurerObj, **kwargs):
    pretty_print(obj["client"].template(**kwargs), obj.get("format"))


@cardconjurer.command()
@click.pass_obj
@click.argument("url_or_path")
@click.argument("output", type=click.File("wb"))
@click.option("--asset-root-url", type=str)
def render(obj: CardConjurerObj, url_or_path, output, asset_root_url):
    card = obj["client"].card(url_or_path)
    if asset_root_url:
        card.asset_root_url = asset_root_url
    obj["client"].render(card, output)

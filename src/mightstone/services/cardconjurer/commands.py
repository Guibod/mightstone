import click

from mightstone.cli.models import MightstoneCli, pass_mightstone
from mightstone.cli.utils import pretty_print


@click.group()
@click.option("--cache", type=int, default=0)
def cardconjurer():
    pass


@cardconjurer.command()
@pass_mightstone
@click.argument("url_or_path")
def card(cli: MightstoneCli, **kwargs):
    pretty_print(cli.app.card_conjurer.card(**kwargs), cli.format)


@cardconjurer.command()
@pass_mightstone
@click.argument("url_or_path")
def template(cli: MightstoneCli, **kwargs):
    pretty_print(cli.app.card_conjurer.template(**kwargs), cli.format)


@cardconjurer.command()
@pass_mightstone
@click.argument("url_or_path")
@click.argument("output", type=click.File("wb"))
@click.option("--asset-root-url", type=str)
def render(cli: MightstoneCli, url_or_path, output, asset_root_url):
    card = cli.app.card_conjurer.card(url_or_path)
    if asset_root_url:
        card.asset_root_url = asset_root_url
    cli.app.card_conjurer.render(card, output)

import click

from mightstone.ass import aiterator_to_list
from mightstone.cli.models import MightstoneCli, pass_mightstone
from mightstone.cli.utils import pretty_print
from mightstone.services.edhrec.api import (
    EdhRecCategory,
    EdhRecIdentity,
    EdhRecPeriod,
    EdhRecType,
)


@click.group()
def edhrec():
    pass


@edhrec.command()
@pass_mightstone
@click.argument("name", nargs=1)
@click.argument("sub", required=False)
def commander(cli: MightstoneCli, **kwargs):
    pretty_print(cli.app.edhrec_static.commander(**kwargs), cli.format)


@edhrec.command()
@pass_mightstone
@click.argument("identity", required=False)
@click.option("-l", "--limit", type=int)
def tribes(cli: MightstoneCli, **kwargs):
    pretty_print(
        aiterator_to_list(cli.app.edhrec_static.tribes_async(**kwargs)), cli.format
    )


@edhrec.command()
@pass_mightstone
@click.argument("identity", required=False)
@click.option("-l", "--limit", type=int)
def themes(cli: MightstoneCli, **kwargs):
    pretty_print(
        aiterator_to_list(cli.app.edhrec_static.themes_async(**kwargs)), cli.format
    )


@edhrec.command()
@pass_mightstone
@click.option("-l", "--limit", type=int)
def sets(cli: MightstoneCli, **kwargs):
    pretty_print(
        aiterator_to_list(cli.app.edhrec_static.sets_async(**kwargs)), cli.format
    )


@edhrec.command()
@pass_mightstone
@click.option("-l", "--limit", type=int)
def companions(cli: MightstoneCli, **kwargs):
    pretty_print(
        aiterator_to_list(cli.app.edhrec_static.companions_async(**kwargs)), cli.format
    )


@edhrec.command()
@pass_mightstone
@click.option("-i", "--identity", type=str)
@click.option("-l", "--limit", type=int)
def partners(cli: MightstoneCli, **kwargs):
    pretty_print(
        aiterator_to_list(cli.app.edhrec_static.partners_async(**kwargs)), cli.format
    )


@edhrec.command()
@pass_mightstone
@click.option("-i", "--identity", type=str)
@click.option("-l", "--limit", type=int, default=100)
def commanders(cli: MightstoneCli, **kwargs):
    pretty_print(
        aiterator_to_list(cli.app.edhrec_static.commanders_async(**kwargs)), cli.format
    )


@edhrec.command()
@pass_mightstone
@click.argument("identity", type=click.Choice([t.value for t in EdhRecIdentity]))
@click.option("-l", "--limit", type=int, default=100)
def combos(cli: MightstoneCli, **kwargs):
    pretty_print(
        aiterator_to_list(cli.app.edhrec_static.combos_async(**kwargs)), cli.format
    )


@edhrec.command()
@pass_mightstone
@click.argument("identity", type=click.Choice([t.value for t in EdhRecIdentity]))
@click.argument("identifier", type=str)
@click.option("-l", "--limit", type=int, default=100)
def combo(cli: MightstoneCli, **kwargs):
    pretty_print(
        aiterator_to_list(cli.app.edhrec_static.combo_async(**kwargs)), cli.format
    )


@edhrec.command()
@pass_mightstone
@click.argument("year", required=False, type=int)
@click.option("-l", "--limit", type=int)
def salt(cli: MightstoneCli, **kwargs):
    pretty_print(
        aiterator_to_list(cli.app.edhrec_static.salt_async(**kwargs)), cli.format
    )


@edhrec.command()
@pass_mightstone
@click.option("-t", "--type", type=click.Choice([t.value for t in EdhRecType]))
@click.option("-p", "--period", type=click.Choice([t.value for t in EdhRecPeriod]))
@click.option("-l", "--limit", type=int)
def top_cards(cli: MightstoneCli, **kwargs):
    pretty_print(
        aiterator_to_list(cli.app.edhrec_static.top_cards_async(**kwargs)), cli.format
    )


@edhrec.command()
@pass_mightstone
@click.option("-c", "--category", type=click.Choice([t.value for t in EdhRecCategory]))
@click.option("-t", "--theme", type=str)
@click.option("--commander", type=str)
@click.option("-i", "--identity", type=str)
@click.option("-s", "--set", type=str)
@click.option("-l", "--limit", type=int)
def cards(cli: MightstoneCli, **kwargs):
    pretty_print(
        aiterator_to_list(cli.app.edhrec_static.cards_async(**kwargs)), cli.format
    )

import logging

import click

import mightstone

from ..services.edhrec.commands import edhrec
from ..services.mtgjson.commands import mtgjson
from ..services.scryfall.commands import scryfall


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


cli.add_command(mtgjson)
cli.add_command(scryfall)
cli.add_command(edhrec)

import logging
import os
import pathlib
from logging.handlers import RotatingFileHandler

import click

from .. import Mightstone, __author__, __version__
from ..config import MainSettings
from ..core import MightstoneError
from ..services.cardconjurer.commands import cardconjurer
from ..services.edhrec.commands import edhrec
from ..services.mtgjson.commands import mtgjson
from ..services.scryfall.commands import scryfall
from .models import CliFormat, MightstoneCli, pass_mightstone
from .utils import pretty_print


@click.group()
@click.option(
    "-f",
    "--format",
    type=click.Choice([t.value for t in CliFormat]),
    default=CliFormat.JSON,
)
@click.option("-v", "--verbose", count=True)
@click.option("-l", "--log-level", default="ERROR")
@click.option(
    "-c", "--config", type=click.Path(readable=True, exists=True), default=None
)
@pass_mightstone
def cli(mightstone: MightstoneCli, format, verbose, log_level, config):
    mightstone.format = format

    if config:
        try:
            settings = MainSettings.model_validate(config)
            mightstone.app = Mightstone(config=settings)
        except MightstoneError as e:
            raise click.ClickException(str(e) + "\n" + str(e.__context__))

    if verbose:
        log_level = logging.WARNING
    if verbose > 1:
        log_level = logging.INFO
    if verbose > 2:
        log_level = logging.DEBUG

    log_directory = pathlib.Path(mightstone.app.app_dirs.user_log_dir)
    if not log_directory.exists():
        os.makedirs(log_directory)
    logging.basicConfig(
        handlers=[
            logging.StreamHandler(),
            RotatingFileHandler(
                log_directory.joinpath("mightstone.log"),
                maxBytes=100000,
                backupCount=10,
            ),
        ],
        level=log_level,
        format=(
            "[%(asctime)s] %(levelname)s [%(name)s.%(funcName)s:%(lineno)d] %(message)s"
        ),
        datefmt="%Y-%m-%dT%H:%M:%S",
    )


@cli.command()
@pass_mightstone
def config(mightstone: MightstoneCli):
    """Dumps configuration"""

    pretty_print(mightstone.app.config)


@cli.command()
@click.option("-v", "--verbose", count=True)
def version(verbose):
    """Displays the version"""

    click.echo("Version: %s" % __version__)
    if verbose > 0:
        click.echo("Author: %s" % __author__)


cli.add_command(mtgjson)
cli.add_command(scryfall)
cli.add_command(edhrec)
cli.add_command(cardconjurer)

import logging
import os
import pathlib
from logging.handlers import RotatingFileHandler
from typing import Union

import asyncclick as click

from .. import Mightstone, __author__, __version__
from ..config import MightstoneSettings
from ..core import MightstoneError
from ..services.cardconjurer.commands import cardconjurer
from ..services.edhrec.commands import edhrec
from ..services.mtgjson.commands import mtgjson
from ..services.scryfall.commands import scryfall
from ..services.wiki.commands import wiki
from ..services.wotc.commands import wotc
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
    "config_file",
    "-c",
    "--config",
    type=click.Path(readable=True, exists=True),
    default=None,
)
@pass_mightstone
async def cli(
    mightstone: MightstoneCli,
    format,
    verbose,
    log_level,
    config_file: Union[str, bytes, os.PathLike[str]],
):
    mightstone.format = format

    if config_file:
        with open(config_file, encoding="utf-8") as fp:
            try:
                settings = MightstoneSettings.model_validate_json(fp.read())
                mightstone.app = Mightstone(config=settings)
            except MightstoneError as e:
                raise click.ClickException(str(e) + "\n" + str(e.__context__))

    await mightstone.app.enable_persistence()

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
async def config(mightstone: MightstoneCli):
    """Dumps configuration"""

    await pretty_print(mightstone.app.config)


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
cli.add_command(wiki)
cli.add_command(wotc)

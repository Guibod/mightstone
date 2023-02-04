import json
import logging
import sys

import click
import yaml
from pydantic.json import pydantic_encoder

import mightstone
from mightstone.app import App
from mightstone.ass import asyncio_run, stream_as_list
from mightstone.services.edhrec import EdhRecStatic

logger = logging.getLogger("mightstone")


def pretty_print(data, format="yaml"):
    from pygments import highlight
    from pygments.formatters import TerminalFormatter
    from pygments.lexers import JsonLexer, YamlLexer

    datastr = json.dumps(data, indent=2, sort_keys=True, default=pydantic_encoder)
    formatter = TerminalFormatter()
    if format == "json":
        lexer = JsonLexer()
    else:
        lexer = YamlLexer()
        datastr = yaml.dump(json.loads(datastr), indent=2)  # Yes, that’s that bad

    if sys.stdout.isatty():
        highlight(datastr, lexer, formatter, outfile=sys.stdout)
    else:
        sys.stdout.write(datastr)


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
    logging.debug("debug")
    logging.error("error")
    logging.fatal("fatal")


@cli.command()
@click.option("-v", "--verbose", count=True)
def version(verbose):
    """Displays the version"""
    click.echo("Version: %s" % mightstone.__version__)
    if verbose > 0:
        click.echo("Author: %s" % mightstone.__author__)


@cli.group()
def edhrec():
    ...


@edhrec.command()
@click.pass_obj
@click.argument("name", nargs=1)
@click.argument("sub", required=False)
def commander(obj, name, sub):
    logger.info(f"Searching commander {name} at edhrec")
    with EdhRecStatic() as edhrec:
        pretty_print(asyncio_run(edhrec.commander(name, sub)), obj.get("format"))


@edhrec.command()
@click.pass_obj
@click.argument("identity", required=False)
@click.option("-l", "--limit", type=int)
def tribes(obj, identity, limit):
    logger.info(f"Searching tribes using color identity {identity} at edhrec")
    with EdhRecStatic() as edhrec:
        pretty_print(
            stream_as_list(edhrec.tribes(identity, limit=limit)), obj.get("format")
        )


@cli.command()
@click.option(
    "-c",
    "--conf",
    "--config",
    "config_file",
    type=click.Path(exists=True),
)
def serve(config_file):
    """Start mightstone in server mode"""

    settings = {}
    if config_file:
        try:
            with open(config_file, "r") as stream:
                try:
                    settings = yaml.safe_load(stream)
                except yaml.YAMLError as exc:
                    click.echo(exc)
                    sys.exit(1)
        except IOError as exc:
            logger.fatal("%s: %s", exc.strerror, exc.filename)
            sys.exit(1)
        except Exception as exc:
            logger.fatal(
                "Cannot load conf file '%s'. Error message is: %s", config_file, exc
            )
            sys.exit(1)

    # TODO: Create your application object
    app = App(settings)
    try:
        logger.info("Starting")
        # TODO: Start your application
        app.start()
    except KeyboardInterrupt:
        pass
    except Exception as exc:
        logger.exception("Unexpected exception: %s", exc)
    finally:
        logger.info("Shutting down")
        # TODO: Cleanup code
        app.stop()

    logger.info("All done")


if __name__ == "__main__":
    cli()

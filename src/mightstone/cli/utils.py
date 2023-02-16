import json
import sys
from functools import partial, wraps

import click
import yaml
from pydantic.json import pydantic_encoder

from mightstone.services import ServiceError


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


def catch_service_error(func=None):
    if not func:
        return partial(catch_service_error)

    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ServiceError as e:
            raise click.ClickException(f"{e.message}, at {e.method} {e.url}")

    return wrapper

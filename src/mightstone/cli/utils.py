import inspect
import json
import sys
from functools import partial, wraps
from typing import Any, AsyncGenerator, Coroutine, Union

import asyncclick as click
import yaml
from pydantic import BaseModel

from mightstone.services import ServiceError


async def pretty_print(
    data: Union[list[BaseModel], BaseModel, Any],
    format="yaml",
):
    from pygments import highlight
    from pygments.formatters import TerminalFormatter
    from pygments.lexers import JsonLexer, YamlLexer

    if isinstance(data, BaseModel):
        data = data.model_dump(mode="json")
    else:
        try:
            data = [d.model_dump(mode="json") for d in data]
        except AttributeError:
            ...

    formatter = TerminalFormatter()
    if format == "json":
        lexer = JsonLexer()
        datastr = json.dumps(data, indent=2)
    else:
        lexer = YamlLexer()
        datastr = yaml.dump(data, indent=2)

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

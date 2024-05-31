from enum import Enum

import click
from pydantic import BaseModel, ConfigDict, Field

from mightstone.app import Mightstone


class CliFormat(str, Enum):
    JSON = "json"
    YAML = "yaml"


class MightstoneCli(BaseModel):
    """
    Command line CLI context
    """

    format: CliFormat = CliFormat.JSON
    app: Mightstone = Field(default_factory=Mightstone)
    model_config = ConfigDict(arbitrary_types_allowed=True)


pass_mightstone = click.make_pass_decorator(MightstoneCli, ensure=True)

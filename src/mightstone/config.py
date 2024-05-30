import json
import logging
import os
import pathlib
from enum import Enum
from typing import Any, Literal, Optional, Type, TypeVar, Union

import toml
import yaml
from pydantic.env_settings import BaseSettings
from pydantic.networks import MongoDsn
from pydantic.parse import Protocol

from mightstone.core import MightstoneError

logger = logging.getLogger("mightstone")


def load_file(filepath, encoding):
    try:
        with open(filepath, "r", encoding=encoding) as f:
            _, extension = os.path.splitext(filepath)
            if extension.lower() in [".yml", ".yaml"]:
                return yaml.safe_load(f)

            if extension.lower() == ".toml":
                return toml.load(f)

            return json.load(f)
    except Exception as e:
        raise MightstoneError("Unable to parse %s" % filepath) from e


class DbImplem(str, Enum):
    LOCAL = "local"
    MOTOR = "motor"


T = TypeVar("T", bound="MightstoneSettings")


class MightstoneSettings(BaseSettings):
    @classmethod
    def parse_file(
        cls: Type[T],
        path: Union[str, pathlib.Path],
        *,
        content_type: str = None,
        encoding: str = "utf8",
        proto: Protocol = None,
        allow_pickle: bool = False,
    ) -> T:
        obj = load_file(
            path,
            encoding=encoding,
        )
        return cls.parse_obj(obj)


class HttpCacheSettings(MightstoneSettings):
    persist: bool = True
    directory: Optional[pathlib.Path]
    methods: list[str] = ["GET"]
    status: list[int] = [200, 203, 300, 301, 308]


class HttpSettings(MightstoneSettings):
    cache: HttpCacheSettings = HttpCacheSettings()


class InMemorySettings(MightstoneSettings):
    implementation: Literal[DbImplem.LOCAL] = DbImplem.LOCAL
    directory: Optional[pathlib.Path]
    database: str = "mightstone"


class MotorSettings(MightstoneSettings):
    implementation: Literal[DbImplem.MOTOR] = DbImplem.MOTOR
    uri: MongoDsn
    database: str = "mightstone"


class MainSettings(MightstoneSettings):
    appname: str = "Mightstone"
    storage: Union[InMemorySettings, MotorSettings] = InMemorySettings()
    http: HttpSettings = HttpSettings()

    class Config:
        env_prefix = "mightstone_"
        env_nested_delimiter = "__"
        env_file_encoding = "utf-8"

        @classmethod
        def customise_sources(
            cls,
            init_settings,
            env_settings,
            file_secret_settings,
        ):
            return (
                init_settings,
                cls.json_config_settings_source,
                env_settings,
                file_secret_settings,
            )

        @classmethod
        def candidate_paths(cls) -> list[pathlib.Path]:
            candidate = os.getenv("MIGHTSTONE_CONFIG_FILE")
            if candidate:
                return [pathlib.Path(candidate)]

            return [
                pathlib.Path(path).joinpath(f"mightstone.{extension}")
                for path in [os.getcwd(), os.path.expanduser("~")]
                for extension in ["yaml", "yml", "json", "toml"]
            ]

        @classmethod
        def json_config_settings_source(cls, settings: BaseSettings) -> dict[str, Any]:
            """
            A simple settings source that loads variables from a JSON file
            at the project's root.

            Here we happen to choose to use the `env_file_encoding` from Config
            when reading `config.json`
            """

            for candidate in cls.candidate_paths():
                if not candidate.exists():
                    continue

                try:
                    return load_file(
                        candidate, encoding=settings.__config__.env_file_encoding
                    )
                except MightstoneError as e:
                    logger.fatal(
                        "Unable to parse configuration from %s, %s", candidate, e
                    )

            return {}

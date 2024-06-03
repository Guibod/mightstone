import datetime
import importlib
import inspect
import os
from typing import Type

import setuptools
from beanie import Document
from pydantic import BaseModel
from pydantic_extra_types.color import Color


class MightstoneModel(BaseModel):
    def __hash__(self):
        return hash((type(self),) + tuple(self.__dict__.values()))


class MightstoneDocument(MightstoneModel, Document):
    pass


def get_documents():
    """
    Explore mightstone to find any file that extends MightstoneDocument

    This is useful to initialize beanie database.

    :return: A list of class expanding MightstoneDocument type
    """
    models = []

    for package in setuptools.find_packages(os.path.dirname(__file__)):
        module_spec = importlib.util.find_spec(f"mightstone.{package}.models")
        if module_spec:
            module = importlib.import_module(module_spec.name)

            for name, cls in inspect.getmembers(module):
                if not inspect.isclass(cls):
                    continue
                if not issubclass(cls, MightstoneDocument):
                    continue
                if MightstoneDocument == cls:
                    continue
                if bool(getattr(cls, "__abstractmethods__", False)):
                    continue

                patch_model(cls)
                models.append(cls)

    return models


def patch_model(model: Type[MightstoneDocument]):
    """
    Beanie documents require a Settings inner class that defines its configuration.
    We forcefully patch the models globally to add:

    * bson_encoders support for datetime.date
    * name the model from the module

    :param model:
    :return:
    """

    notable_parent_package = [
        pkg for pkg in model.__module__.split(".") if pkg != "models"
    ][-1]
    collection_name = "_".join([notable_parent_package, model.__name__.lower()])
    if collection_name[-1] != "s":
        collection_name += "s"

    model.Settings = type(  # type: ignore
        "Settings",
        (object,),
        {
            "bson_encoders": {
                datetime.date: lambda dt: datetime.datetime(
                    year=dt.year,
                    month=dt.month,
                    day=dt.day,
                    hour=0,
                    minute=0,
                    second=0,
                ),
                Color: lambda c: c.as_hex(),
            },
            "name": collection_name,
        },
    )


class MightstoneError(Exception):
    pass

import datetime
import importlib
import inspect
import pkgutil
import sys
from abc import ABC
from types import ModuleType
from typing import Any, Optional, Type, Union
from uuid import UUID

from beanie import Document, PydanticObjectId
from beanie.exceptions import CollectionWasNotInitialized
from beanie.odm.settings.document import DocumentSettings
from pydantic import (
    BaseModel,
    ValidationInfo,
    ValidatorFunctionWrapHandler,
    WrapValidator,
)
from pydantic_extra_types.color import Color


def Fallback(fallback_value: Any):
    def use_fallback(
        v: Any,
        handler: ValidatorFunctionWrapHandler,
        info: ValidationInfo,
    ) -> Any:
        try:
            return handler(v)
        except ValueError:
            return fallback_value

    return WrapValidator(use_fallback)


class MightstoneModel(ABC, BaseModel):
    def __hash__(self):
        return hash((type(self),) + tuple(self.__dict__.values()))


class MightstoneDocument(MightstoneModel):
    def to_serializable(
        self,
    ):
        target_class = get_serializable_class(self.__class__)
        if not target_class:
            raise Exception(
                "There is no available serializable variant of %s"
                % self.__class__.__name__
            )

        return target_class.model_validate(self.model_dump())


class MightstoneSerializableDocument(MightstoneModel, Document):
    id: Optional[Union[UUID, PydanticObjectId]] = None  # type: ignore

    @classmethod
    def get_settings(cls) -> DocumentSettings:
        try:
            return super().get_settings()
        except CollectionWasNotInitialized as e:
            raise MightstoneError(
                "In order to benefit from database serialization you need to "
                "initialize Mightstone through Mighstone.with_beanie() factory"
                "or use Mighstone.beanie_init()."
            ) from e


def get_serializable_class(
    cls: type[MightstoneDocument],
) -> Union[MightstoneSerializableDocument, None]:
    for name, candidate in inspect.getmembers(
        sys.modules[cls.__module__], inspect.isclass
    ):
        if candidate in [
            Document,
            MightstoneDocument,
            MightstoneSerializableDocument,
            cls,
        ]:
            continue
        if issubclass(candidate, (cls, Document)):
            return candidate  # type: ignore
    return None


def get_documents(root_module: Union[ModuleType, str] = "mightstone"):
    """
    Explore a package (mightstone by default) to find any file that extends Document

    This is useful to initialize beanie database.

    :return: A list of class expanding Document type
    """
    models = set()

    if isinstance(root_module, str):
        root_module = sys.modules[root_module]

    for package in pkgutil.walk_packages(
        root_module.__path__, root_module.__name__ + "."
    ):
        module = importlib.import_module(package.name)

        for name, cls in inspect.getmembers(module, inspect.isclass):
            if inspect.isabstract(cls):
                continue
            if not issubclass(cls, Document):
                continue
            if cls in [Document, MightstoneDocument, MightstoneSerializableDocument]:
                continue

            patch_beanie_document(cls)
            models.add(cls)

    return list(models)


def patch_beanie_document(model: Type[Document]):
    """
    Beanie documents require a Settings inner class that defines its configuration.
    We forcefully patch the models globally to add:

    * bson_encoders support for:
        - datetime.date
        - pydantic Color
    * name the model collection from the module if not already defined

    :param model:
    :return:
    """

    if hasattr(model, "Settings") and hasattr(model.Settings, "name"):
        collection_name = model.Settings.name
    else:
        notable_parent_package = [
            pkg
            for pkg in model.__module__.split(".")
            if pkg not in ["models", "services"]
        ]
        collection_name = "_".join(
            notable_parent_package
            + [model.__name__.lower().replace("serializable", "")]
        )
        if collection_name[-1] != "s":
            collection_name += "s"

    model.Settings = type(
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
    )  # type: ignore


class MightstoneError(Exception):
    pass

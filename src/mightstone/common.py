import uuid
from typing import Any, Callable, Generator, get_args, get_origin

from pydantic import BaseModel


def generate_uuid_from_string(string: str) -> uuid.UUID:
    return uuid.uuid5(uuid.NAMESPACE_OID, str(string).strip().lower())


def pydantic_model_recurse(
    obj: BaseModel, matcher: Callable = lambda: True
) -> Generator[Any, None, None]:
    """
    Recursively match any BaseModel property of current object if the matcher expression is positive
    :param obj:
    :param matcher:
    :return:
    """
    if matcher(obj):
        yield obj

    for field_name, definition in obj.__fields__.items():
        value = getattr(obj, field_name)
        origin = get_origin(definition.annotation)
        if isinstance(value, BaseModel):
            yield from pydantic_model_recurse(value, matcher)
        elif origin == list and issubclass(
            get_args(definition.annotation)[0], BaseModel
        ):
            for i in value:
                yield from pydantic_model_recurse(i, matcher)
        elif origin == dict and issubclass(
            get_args(definition.annotation)[1], BaseModel
        ):
            for i in value.values():
                yield from pydantic_model_recurse(i, matcher)

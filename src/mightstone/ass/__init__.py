import logging
from functools import wraps
from typing import Any, AsyncGenerator, Callable, List, TypeVar

import asyncstdlib
from asgiref.sync import async_to_sync

logger = logging.getLogger(__name__)

T = TypeVar("T")


@async_to_sync
async def aiterator_to_list(ait: AsyncGenerator[T, Any], limit=100) -> List[T]:
    """
    Transforms an async iterator into a sync list

    :param ait: Asynchronous iterator
    :param limit: Max item to return
    :return: The list of items
    """
    return [item async for item in asyncstdlib.islice(ait, limit)]


R = TypeVar("R")


def synchronize(f: Callable[..., R], docstring: str = None) -> Callable[..., R]:
    qname = f"{f.__module__}.{f.__qualname__}"

    @wraps(f)
    def inner(*args, **kwargs) -> R:
        executor = async_to_sync(f)
        return executor(*args, **kwargs)

    if docstring:
        inner.__doc__ = docstring
    else:
        inner.__doc__ = (
            f"Sync version of :func:`~{qname}`, same behavior but "
            "wrapped by :func:`~asgiref.sync.async_to_sync`."
        )

    return inner

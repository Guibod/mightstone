import asyncio
import logging
from functools import wraps
from typing import (
    Any,
    AsyncGenerator,
    Callable,
    Coroutine,
    Generator,
    List,
    Optional,
    TypeVar,
)

import asyncstdlib
from asgiref.sync import async_to_sync

logger = logging.getLogger(__name__)

T = TypeVar("T")


@async_to_sync
async def aiterator_to_list(agen: AsyncGenerator[T, Any], limit=100) -> List[T]:
    """
    Transforms an async iterator into a sync list

    :param agen: Asynchronous iterator
    :param limit: Max item to return
    :return: The list of items
    """

    if limit:
        ait = asyncstdlib.islice(agen.__aiter__(), limit)
    else:
        ait = agen.__aiter__()
    return [item async for item in ait]


R = TypeVar("R")


def synchronize(
    f: Callable[..., Coroutine[Any, Any, R]],
    docstring: Optional[str] = None,
) -> Callable[..., R]:
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


def sync_generator(
    f: Callable[..., AsyncGenerator[R, None]],
    docstring: Optional[str] = None,
) -> Callable[..., Generator[R, None, None]]:
    qname = f"{f.__module__}.{f.__qualname__}"
    loop = asyncio.get_event_loop()

    @wraps(f)
    def inner(*args, **kwargs) -> Generator[R, None, None]:
        async_generator = f(*args, **kwargs)
        try:
            while True:
                yield loop.run_until_complete(async_generator.__anext__())
        except StopAsyncIteration:
            return

    if docstring:
        inner.__doc__ = docstring
    else:
        inner.__doc__ = (
            f"Sync version of :func:`~{qname}`, same behavior but "
            "wrapped by :func:`~asgiref.sync.async_to_sync`."
        )

    return inner

import asyncio
from functools import wraps

import logging

from typing import Any, AsyncGenerator, List, TypeVar, Callable
from asgiref.sync import async_to_sync
import nest_asyncio
from aiostream import pipe, stream

logger = logging.getLogger(__name__)

T = TypeVar("T")


def asyncio_run(future, as_task=True):
    """
    A better implementation of `asyncio.run`.

    :param future: A future or task or call of an async method.
    :param as_task: Forces the future to be scheduled as task (needed for e.g. aiohttp).
    """

    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:  # no event loop running:
        loop = asyncio.new_event_loop()
        return loop.run_until_complete(_to_task(future, as_task, loop))
    else:
        nest_asyncio.apply(loop)
        return asyncio.run(_to_task(future, as_task, loop))


def _to_task(future, as_task, loop):
    if not as_task or isinstance(future, asyncio.Task):
        return future
    return loop.create_task(future)


def stream_as_list(ait: AsyncGenerator[T, Any], limit=100) -> List[T]:
    async def run(my_it):
        return await (stream.iterate(my_it) | pipe.take(limit) | pipe.list())

    return asyncio_run(run(ait))


def stream_print(ait: AsyncGenerator[T, Any], limit=100):
    async def run(my_it):
        await (stream.iterate(my_it) | pipe.take(limit) | pipe.print())

    return asyncio_run(run(ait))


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
        inner.__doc__ = f"Sync version of :func:`~{qname}`, same behavior but " \
                        f"wrapped by :func:`~asgiref.sync.async_to_sync`."

    return inner

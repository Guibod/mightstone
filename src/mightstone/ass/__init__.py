import logging
from functools import wraps
from typing import (
    Any,
    AsyncGenerator,
    Callable,
    Coroutine,
    Generator,
    Optional,
    TypeVar,
    Union,
    overload,
)

import universalasync

logger = logging.getLogger(__name__)

T = TypeVar("T")


@overload
def synchronize(
    f: Callable[..., Coroutine[Any, Any, T]],
    docstring: Optional[str] = None,
) -> Callable[..., Union[Coroutine[Any, Any, T], T]]: ...
@overload
def synchronize(
    f: Callable[..., AsyncGenerator[T, None]],
    docstring: Optional[str] = None,
) -> Callable[..., Union[AsyncGenerator[T, None], Generator[T, None, None]]]: ...


def synchronize(
    f: Callable,
    docstring: Optional[str] = None,
) -> Callable:
    qname = f"{f.__module__}.{f.__qualname__}"

    @wraps(f)
    def inner(*args, **kwargs):
        return universalasync.async_to_sync_wraps(f)(*args, **kwargs)

    if docstring:
        inner.__doc__ = docstring
    else:
        inner.__doc__ = (
            f"Universal (async or sync) version of :func:`~{qname}`, same behavior but "
            "wrapped by :func:`~universalasync`."
        )

    return inner

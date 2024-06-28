import asyncio
from typing import Optional

import ijson as ijson_module
from hishel import AsyncCacheClient, AsyncCacheTransport
from httpx import Timeout
from injector import inject

from .. import __version__
from ..types import MightstoneIjsonBackend


class ServiceError(Exception):
    def __init__(self, message, url=None, status=None, data=None, method=None):
        self.message = message
        self.url = url
        self.status = status
        self.data = data
        self.method = method

    def __str__(self):
        return "{message} (HTTP:{status} {method} {url})".format(**self.__dict__)


class MightstoneHttpClient:
    base_url: str
    """
    Base url of the service (must be a root path such as https://example.com)
    """
    delay = 0
    """
    Induced delay in second between each API call
    """
    timeout: Optional[Timeout] = None

    @inject
    def __init__(
        self,
        transport: Optional[AsyncCacheTransport] = None,
        ijson: Optional[MightstoneIjsonBackend] = None,
    ):
        self.transport = transport
        self.ijson = ijson or ijson_module.get_backend(ijson_module.backend)

    @property
    def client(self):
        # See: https://github.com/encode/httpx/issues/2473
        options = {
            "transport": self.transport,
            "headers": {
                "cache-control": f"max-age={60 * 60 * 24}",
                "user-agent": f"mightstone/{__version__}",
            },
        }
        if self.timeout:
            options["timeout"] = self.timeout
        if hasattr(self, "base_url"):
            options["base_url"] = self.base_url
        if self.transport:
            options["storage"] = self.transport._storage
            options["controller"] = self.transport._controller
        return AsyncCacheClient(**options)

    async def close(self):
        await self.client.aclose()

    async def _sleep(self):
        await asyncio.sleep(self.delay)

import asyncio

import ijson as ijson_module
from httpx import AsyncClient, BaseTransport

# try:
#     ijson = ijson_module.get_backend("yajl2")
# except ImportError:
ijson = ijson_module.get_backend("python")


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

    def __init__(self, transport: BaseTransport = None):
        self.transport = transport
        self.ijson = ijson

    @property
    def client(self):
        # See: https://github.com/encode/httpx/issues/2473
        options = {
            "transport": self.transport,
            "headers": {"cache-control": f"max-age={60 * 60 * 24}"},
        }
        if hasattr(self, "base_url"):
            options["base_url"] = self.base_url

        return AsyncClient(**options)

    async def close(self):
        await self.client.aclose()

    async def _sleep(self):
        await asyncio.sleep(self.delay)

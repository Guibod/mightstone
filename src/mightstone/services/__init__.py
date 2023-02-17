import asyncio

import ijson as ijson_module
from aiohttp_client_cache import CacheBackend, CachedSession, SQLiteBackend
from appdirs import user_cache_dir

from mightstone.ass import asyncio_run

try:
    ijson = ijson_module.get_backend("yajl2")
except ImportError:
    ijson = ijson_module.get_backend("python")

cache_dir = user_cache_dir("mightstone")


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
    base_url = None
    """
    Base url of the service (must be a root path such as https://example.com)
    """
    delay = 0
    """
    Induced delay in second between each API call
    """

    def __init__(self, cache: int = 60 * 60):
        self._session = None
        self.ijson = ijson
        self.cache = cache

    @property
    def session(self):
        if not self._session:
            self._session = self._build_session()
        return self._session

    def _build_session(self, *args, **kwargs) -> CachedSession:
        if self.cache and self.cache > 0:
            cache = SQLiteBackend(
                cache_name=f"{cache_dir}/http-cache.sqlite", expire_after=self.cache
            )
        else:
            cache = CacheBackend(expire_after=0, allowed_codes=())

        return CachedSession(base_url=self.base_url, cache=cache, *args, **kwargs)

    async def __aenter__(self):
        return self

    def __enter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self._session:
            await self._session.close()

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._session:
            asyncio_run(self.session.close())

    def __del__(self):
        if self._session:
            asyncio_run(self.session.close())

    async def _sleep(self):
        await asyncio.sleep(self.delay)

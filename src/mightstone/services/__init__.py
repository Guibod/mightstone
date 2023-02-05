import asyncio

from aiohttp import ClientSession

from mightstone.ass import asyncio_run


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
    delay = 0

    def __init__(self):
        self._session = None

    @property
    def session(self):
        if not self._session:
            self._session = self.build_session()
        return self._session

    @classmethod
    def build_session(cls, *args, **kwargs):
        return ClientSession(base_url=cls.base_url, *args, **kwargs)

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

    async def sleep(self):
        await asyncio.sleep(self.delay)

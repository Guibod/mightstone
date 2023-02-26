import unittest
import pytest

from mightstone.ass import stream_as_list
from mightstone.services.scryfall import Scryfall, SortStrategy


@pytest.mark.asyncio
@pytest.mark.skip_remote_api
class TestScryfall(unittest.IsolatedAsyncioTestCase):
    def setUp(self) -> None:
        self.client = Scryfall()

    async def test_search(self):
        found = stream_as_list(self.client.search("boseiju", order=SortStrategy.EUR))

        self.assertEqual(found[0].name, )
        print(found)

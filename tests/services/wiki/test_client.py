from typing import AsyncGenerator

import pytest
from assertpy import assert_that

from mightstone.services.wiki import Wiki


@pytest.mark.asyncio
@pytest.mark.skip_remote_api
class TestClient:
    async def test_export_pages_unknown_pages(self):
        client = Wiki()
        response = await client.export_pages_async(["zorblug", "non-existing"])

        assert_that(response.count(b"<page>")).is_equal_to(0)
        assert_that(response).is_instance_of(bytes)
        assert_that(response).does_not_contain(b"<page>")

    async def test_export_pages_existing_pages(self):
        client = Wiki()
        response = await client.export_pages_async(["Ability", "Action"])

        assert_that(response).is_instance_of(bytes)
        assert_that(response).contains(b"<page>")

        assert_that(response.count(b"<page>")).is_equal_to(2)
        assert_that(response).contains(b"<title>Ability</title>")
        assert_that(response).contains(b"<title>Action</title>")

    async def test_export_pages_mixed_pages(self):
        client = Wiki()
        response = await client.export_pages_async(["Ability", "non-existing"])
        assert_that(response).is_instance_of(bytes)

        assert_that(response.count(b"<page>")).is_equal_to(1)
        assert_that(response).contains(b"<title>Ability</title>")

    async def test_export_category_missing(self):
        client = Wiki()
        response = await client.export_category_async("does not exist")
        assert_that(response).is_instance_of(bytes)

        assert_that(response.count(b"<page>")).is_equal_to(0)

    async def test_export_category_exist(self):
        client = Wiki()
        response = await client.export_category_async("Keywords")
        assert_that(response).is_instance_of(bytes)

        assert_that(response.count(b"<page>")).is_greater_than(10)

    async def test_export_all_pages_no_redirect(self):
        client = Wiki()
        async_generator = client.explore_pages(False)
        assert_that(async_generator).is_instance_of(AsyncGenerator)

        all_pages = [page async for page in client.explore_pages(False)]
        count_pages = len(all_pages)

        assert_that(count_pages).is_greater_than(400)

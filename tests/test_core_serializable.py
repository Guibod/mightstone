import unittest

import pytest
from assertpy import assert_that
from beanie import Document

from mightstone.core import MightstoneDocument, MightstoneModel, patch_beanie_document


class SampleSubClass(MightstoneModel):
    string: str
    integer: int


class SampleDocument(MightstoneDocument):
    name: str
    sub: SampleSubClass


class SerializableSampleDocument(SampleDocument, Document): ...


@pytest.fixture(scope="session")
def get_document_fixture():
    patch_beanie_document(SerializableSampleDocument)
    return [SerializableSampleDocument]


@pytest.mark.usefixtures("get_document_fixture")
@pytest.mark.asyncio(scope="session")
class MixinCoreTest:
    async def test_serializable_at_runtime(self):
        doc = SampleDocument.model_validate(
            {"name": "foo", "sub": {"string": "bar", "integer": 12}}
        )

        assert_that(hasattr(doc, "save")).is_fals()

        serializable = doc.to_serializable()

        assert_that(hasattr(serializable, "save")).is_true()
        assert_that(hasattr(serializable, "save")).is_instance_of(
            SerializableSampleDocument
        )

    async def test_serialize_at_runtime(self):
        doc = SampleDocument.model_validate(
            {"name": "foo", "sub": {"string": "bar", "integer": 12}}
        )

        serializable = doc.to_serializable()
        await serializable.save()

        found = await SerializableSampleDocument.find_one({"name": "foo"})

        assert_that(found).is_not_none()
        assert_that(found.sub.string).is_equal_to("bar")
        assert_that(found.sub.integer).is_equal_to(12)

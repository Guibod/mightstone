from beanie import Document

from mightstone.core import MightstoneDocument, MightstoneModel, patch_beanie_document

from .testcase import TestBeanie


class SampleSubClass(MightstoneModel):
    string: str
    integer: int


class SampleDocument(MightstoneDocument):
    name: str
    sub: SampleSubClass


class SerializableSampleDocument(SampleDocument, Document): ...


class MixinCoreTest(TestBeanie):
    def get_documents(self):
        patch_beanie_document(SerializableSampleDocument)
        return [SerializableSampleDocument]

    def test_serializable_at_runtime(self):
        doc = SampleDocument.model_validate(
            {"name": "foo", "sub": {"string": "bar", "integer": 12}}
        )

        self.assertFalse(hasattr(doc, "save"))

        serializable = doc.to_serializable()

        self.assertTrue(hasattr(serializable, "save"))
        self.assertIsInstance(serializable, SerializableSampleDocument)

    async def test_serialize_at_runtime(self):
        doc = SampleDocument.model_validate(
            {"name": "foo", "sub": {"string": "bar", "integer": 12}}
        )

        serializable = doc.to_serializable()
        await serializable.save()

        found = await SerializableSampleDocument.find_one({"name": "foo"})

        self.assertIsNotNone(found)
        self.assertEqual(found.sub.string, "bar")
        self.assertEqual(found.sub.integer, 12)

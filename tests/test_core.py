from unittest import TestCase

from mightstone.core import (
    MightstoneDocument,
    MightstoneSerializableDocument,
    get_documents,
)


class TestDocumentClassFinder(TestCase):
    def test_find(self):
        self.assertIsInstance(get_documents(), list)

    def test_document_instance(self):
        self.assertTrue(
            all(
                [
                    issubclass(doc, MightstoneSerializableDocument)
                    for doc in get_documents()
                ]
            )
        )

    def test_document_has_not_the_root_class(self):
        self.assertNotIn(MightstoneDocument, get_documents())

    def test_document_has_not_the_root_serializable_class(self):
        self.assertNotIn(MightstoneSerializableDocument, get_documents())

    def test_count(self):
        self.assertGreater(len(get_documents()), 10)

import unittest
from unittest.mock import patch

from mongomock_motor import AsyncMongoMockClient

from mightstone import Mightstone
from mightstone.config import MightstoneSettings
from mightstone.storage import Mongod


class DependencyInjectionTests(unittest.IsolatedAsyncioTestCase):
    def test_defaults_config(self):
        instance = Mightstone()

        self.assertIsInstance(instance.config, MightstoneSettings)
        self.assertEqual(instance.config.appname, "Mightstone")

    def test_default_config_from_settings(self):
        instance = Mightstone()

        self.assertEqual(instance.config.storage.implementation, "local")
        self.assertEqual(instance.config.storage.database, "mightstone")
        self.assertEqual(instance.config.storage.directory, None)

    @patch("motor.motor_asyncio.AsyncIOMotorClient", side_effect=AsyncMongoMockClient)
    def test_defaults_to_in_memory(self, mock):
        instance = Mightstone()

        self.assertIsInstance(instance.mongo_client, AsyncMongoMockClient)
        self.assertIsInstance(instance.mongo_server, Mongod)
        self.assertIn(instance.mongo_client.address[0], ["localhost", "127.0.0.1"])

    def test_fake_implementation(self):
        instance = Mightstone({"storage": {"implementation": "fake"}})

        self.assertIsInstance(instance.mongo_client, AsyncMongoMockClient)
        self.assertIsNone(instance.mongo_server)
        self.assertEqual(instance.mongo_client.address, ("example.com", 27677))

    @patch("motor.motor_asyncio.AsyncIOMotorClient", side_effect=AsyncMongoMockClient)
    def test_can_switch_to_motor(self, mock):
        instance = Mightstone(
            {
                "storage": {
                    "implementation": "motor",
                    "uri": "mongodb://sysop:moon@example.com",
                }
            }
        )

        self.assertEqual(instance.config.storage.implementation, "motor")
        self.assertIsInstance(instance.mongo_client, AsyncMongoMockClient)
        self.assertEqual(instance.mongo_client.address, ("example.com", 27017))
        self.assertIsNone(instance.mongo_server)

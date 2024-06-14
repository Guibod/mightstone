from unittest.mock import patch

import pytest
from assertpy import assert_that
from mongomock_motor import AsyncMongoMockClient

from mightstone import Mightstone
from mightstone.config import MightstoneSettings
from mightstone.storage import Mongod


class TestDependencyInjectionTests:
    def test_defaults_config(self):
        instance = Mightstone()

        assert_that(instance.config).is_instance_of(MightstoneSettings)
        assert_that(instance.config.appname).is_equal_to("Mightstone")

    def test_default_config_from_settings(self):
        instance = Mightstone()

        assert_that(instance.config.storage.implementation).is_equal_to("local")
        assert_that(instance.config.storage.database).is_equal_to("mightstone")
        assert_that(instance.config.storage.directory).is_equal_to(None)

    @patch("motor.motor_asyncio.AsyncIOMotorClient", side_effect=AsyncMongoMockClient)
    def test_defaults_to_in_memory(self, mock):
        instance = Mightstone()

        assert_that(instance.mongo_client).is_instance_of(AsyncMongoMockClient)
        assert_that(instance.mongo_server).is_instance_of(Mongod)
        assert_that(["localhost", "127.0.0.1"]).contains(
            instance.mongo_client.address[0]
        )

    def test_fake_implementation(self):
        instance = Mightstone({"storage": {"implementation": "fake"}})

        assert_that(instance.mongo_client).is_instance_of(AsyncMongoMockClient)
        assert_that(instance.mongo_server).is_none()
        assert_that(instance.mongo_client.address).is_equal_to(("example.com", 27677))

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

        assert_that(instance.config.storage.implementation).is_equal_to("motor")
        assert_that(instance.mongo_client).is_instance_of(AsyncMongoMockClient)
        assert_that(instance.mongo_client.address).is_equal_to(("example.com", 27017))
        assert_that(instance.mongo_server).is_none()

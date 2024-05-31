import unittest

import motor.motor_asyncio

from mightstone.config import MainSettings
from mightstone.containers import Application


class DependencyInjectionTests(unittest.IsolatedAsyncioTestCase):
    async def test_defaults_config(self):
        container = Application()
        config = container.config()

        self.assertIsInstance(config, dict)
        self.assertEqual(config, {})

    async def test_default_config_from_settings(self):
        container = Application()
        json_config = MainSettings().model_dump(mode="json")
        container.config.from_dict(json_config)

        config = container.config()

        self.assertEqual(config["storage"]["implementation"], "local")
        self.assertEqual(config["storage"]["database"], "mightstone")
        self.assertEqual(config["storage"]["directory"], None)

    async def test_defaults_to_in_memory(self):
        container = Application()
        json_config = MainSettings().model_dump(mode="json")
        container.config.from_dict(json_config)

        client = container.storage().client()

        self.assertIsInstance(client, motor.motor_asyncio.AsyncIOMotorClient)

    async def test_can_switch_to_motor(self):
        container = Application(
            config={
                "storage": {
                    "implementation": "motor",
                    "uri": "fu",
                }
            }
        )

        client = container.storage().client()
        self.assertIsInstance(client, motor.motor_asyncio.AsyncIOMotorClient)

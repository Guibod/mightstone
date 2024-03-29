import unittest

import beanita
import beanita.db
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
        container.config.from_pydantic(MainSettings())

        config = container.config()

        self.assertEqual(config["storage"]["implementation"], "beanita")
        self.assertEqual(config["storage"]["database"], "mightstone")
        self.assertEqual(config["storage"]["directory"], None)

    async def test_defaults_to_beanita(self):
        container = Application()
        container.config.from_pydantic(MainSettings())

        client = container.storage().client()

        self.assertIsInstance(client, beanita.Client)

    async def test_defaults_to_beanie_database(self):
        container = Application()
        container.config.from_pydantic(MainSettings())

        database = container.storage().database()

        self.assertIsInstance(database, beanita.db.Database)

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

import datetime
import os

from beanie.odm.fields import PydanticObjectId

from mightstone.services.wotc import ComprehensiveRules
from mightstone.services.wotc.api import RuleExplorer
from mightstone.services.wotc.models import Effectiveness, Rule

from ...testcase import TestBeanie


class TestSerialization(TestBeanie):
    async def test_explorer(self):
        explorer = RuleExplorer()
        cr = await explorer.open_async(
            os.path.dirname(__file__) + "/samples/20230203.txt"
        )
        await cr.save()

        crs = await ComprehensiveRules.find_many().to_list()
        self.assertEqual(len(crs), 1)

        cr2 = await ComprehensiveRules.find_one({"_id": cr.id})
        self.assertEqual(cr2.effective.date, datetime.date(2023, 2, 3))

        self.assertEqual(cr2.ruleset["100.1"].ref, "100.1")
        self.assertIn(
            "These Magic rules apply to any Magic game with two or more players",
            cr2.ruleset["100.1"].text,
        )

    async def test_card(self):
        self.assertEqual(ComprehensiveRules.Settings.name, "wotc_comprehensiverules")
        cr = ComprehensiveRules()
        cr.effective = Effectiveness(
            "These rules are effective as of February 3, 2023."
        )
        self.assertEqual(cr.effective.date, datetime.date(2023, 2, 3))
        cr.ruleset.rules["100.1"] = Rule(ref="100.1", text="Lorem ipsum sin dolore")
        cr.id = PydanticObjectId("64177f98b22f2bd2c96f4cc5")

        await cr.save()

        crs = await ComprehensiveRules.find_many().to_list()
        self.assertEqual(len(crs), 1)
        self.assertEqual(crs[0].id, PydanticObjectId("64177f98b22f2bd2c96f4cc5"))
        self.assertEqual(crs[0].effective.date, datetime.date(2023, 2, 3))
        self.assertEqual(crs[0].ruleset["100.1"].ref, "100.1")

        cr2 = ComprehensiveRules()
        cr2.effective = Effectiveness(
            "These rules are effective as of February 3, 2023."
        )
        cr2.ruleset.rules["100.2"] = Rule(ref="100.2", text="Lorem ipsum sin dolore")
        cr2.id = PydanticObjectId("64177f98b22f2bd2c96f4cc5")
        await cr2.save()

        crs = await ComprehensiveRules.find_many().to_list()
        self.assertEqual(len(crs), 1)
        self.assertEqual(crs[0].id, PydanticObjectId("64177f98b22f2bd2c96f4cc5"))
        self.assertEqual(crs[0].effective.date, datetime.date(2023, 2, 3))
        self.assertEqual(crs[0].ruleset["100.2"].ref, "100.2")

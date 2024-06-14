import datetime
import os
from uuid import UUID

import pytest
from assertpy import assert_that

from mightstone.common import generate_uuid_from_string
from mightstone.services.wotc import SerializableComprehensiveRules
from mightstone.services.wotc.api import RuleExplorer
from mightstone.services.wotc.models import Effectiveness, Rule


@pytest.mark.asyncio
async def test_explorer(init_beanie_fixture):
    explorer = RuleExplorer()
    cr = await explorer.open_async(os.path.dirname(__file__) + "/samples/20230203.txt")
    await cr.to_serializable().save()

    crs = await SerializableComprehensiveRules.find_many().to_list()
    assert_that(crs).is_length(1)

    cr2 = await SerializableComprehensiveRules.find_one({"_id": cr.id})
    assert_that(cr2.effective.date).is_equal_to(datetime.date(2023, 2, 3))
    assert_that(cr2.ruleset["100.1"].ref).is_equal_to("100.1.")
    assert_that(cr2.ruleset["100.1"].text).contains(
        "These Magic rules apply to any Magic game with two or more players"
    )


@pytest.mark.asyncio
async def test_directly(init_beanie_fixture):
    assert_that(SerializableComprehensiveRules.Settings.name).is_equal_to(
        "mightstone_wotc_comprehensiverules",
    )
    cr = SerializableComprehensiveRules()
    cr.effective = Effectiveness("These rules are effective as of February 3, 2023.")
    assert_that(cr.effective.date).is_equal_to(datetime.date(2023, 2, 3))
    cr.ruleset.rules["100.1"] = Rule(ref="100.1", text="Lorem ipsum sin dolore")
    cr.id = generate_uuid_from_string(cr.effective)

    await cr.save()

    crs = await SerializableComprehensiveRules.find_many().to_list()
    assert_that(crs).is_length(1)
    assert_that(crs[0].id).is_equal_to(UUID("7b3b7d69-4894-551d-8602-d443370a07ff"))
    assert_that(crs[0].effective.date).is_equal_to(datetime.date(2023, 2, 3))
    assert_that(crs[0].ruleset["100.1"].ref).is_equal_to("100.1")

    cr2 = SerializableComprehensiveRules()
    cr2.effective = Effectiveness("These rules are effective as of February 3, 2023.")
    cr2.ruleset.rules["100.2"] = Rule(ref="100.2", text="Lorem ipsum sin dolore")
    cr2.id = generate_uuid_from_string(cr2.effective)
    await cr2.save()

    crs = await SerializableComprehensiveRules.find_many().to_list()
    assert_that(crs).is_length(1)
    assert_that(crs[0].id).is_equal_to(UUID("7b3b7d69-4894-551d-8602-d443370a07ff"))
    assert_that(crs[0].effective.date).is_equal_to(datetime.date(2023, 2, 3))
    assert_that(crs[0].ruleset["100.2"].ref).is_equal_to("100.2")

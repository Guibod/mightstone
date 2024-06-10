import datetime
from unittest import TestCase

from mightstone.rule.models.ability import AbilityList
from mightstone.services.wotc import ComprehensiveRules


class RulesDataTest(TestCase):
    def test_is_defined(self):
        from mightstone.rule.data.rules import rules

        assert isinstance(rules, ComprehensiveRules)

    def test_has_effective_date_not_too_old(self):
        from mightstone.rule.data.rules import rules

        assert rules.effective is not None

        assert rules.effective.date > (
            datetime.date.today() - datetime.timedelta(days=90)
        )

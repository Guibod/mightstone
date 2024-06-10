from unittest import TestCase

from mightstone.rule.models.ability import AbilityList


class AbilitityDataTest(TestCase):
    def test_is_defined(self):
        from mightstone.rule.data.ability import abilities

        assert isinstance(abilities, AbilityList)

    def test_is_expected_size(self):
        from mightstone.rule.data.ability import abilities

        assert len(abilities.abilities) > 250

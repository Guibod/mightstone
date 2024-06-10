from unittest import TestCase

from mightstone.rule.models.color import ColorPie, IdentityMap


class ColorsDataTest(TestCase):
    def test_pie_is_defined(self):
        from mightstone.rule.data.color import color_pie

        assert isinstance(color_pie, ColorPie)

    def test_pie_is_expected_size(self):
        from mightstone.rule.data.color import color_pie

        assert len(color_pie) == 5

    def test_identities_is_defined(self):
        from mightstone.rule.data.color import identities

        assert isinstance(identities, IdentityMap)

    def test_identities_is_expected_size(self):
        from mightstone.rule.data.color import identities

        assert len(identities) == 32

    def test_identities_naya_canonical(self):
        from mightstone.rule.data.color import identities

        assert identities["grw"].canonical == "rgw"
        assert identities["naya"].canonical == "rgw"
        assert identities["NAYA"].canonical == "rgw"
        assert identities["cabaretti"].canonical == "rgw"
        assert identities["CaBareTti"].canonical == "rgw"

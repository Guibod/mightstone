import unittest

from mightstone.services.edhrec import EdhRecFilterQuery, slugify
from mightstone.services.edhrec.models import EdhRecFilterOperator, EdhRecFilterType


class EdhRecSlugify(unittest.TestCase):
    def test_slug_simple(self):
        self.assertEqual("reflecting-pool", slugify("Reflecting Pool"))
        self.assertEqual("talisman-of-dominance", slugify("Talisman of Dominance"))
        self.assertEqual("geier-reach-sanitarium", slugify("Geier Reach Sanitarium"))

    def test_slug_apos(self):
        self.assertEqual("witchs-cottage", slugify("Witch's Cottage"))
        self.assertEqual("kayas-ghostform", slugify("Kaya's Ghostform"))

    def test_slug_diacritic(self):
        self.assertEqual("lim-duls-vault", slugify("Lim-Dûl's Vault"))
        self.assertEqual("deja-vu", slugify("déjà-vu"))

    def test_slug_plus_two_mace(self):
        self.assertEqual("plus-2-mace", slugify("+2 Mace"))


class EdhRecQueryTest(unittest.TestCase):
    def test_empty_to_str(self):
        query = EdhRecFilterQuery()
        self.assertEqual("", str(query))

    def test_in_str(self):
        query = EdhRecFilterQuery(card_in=["Sol Ring", "Rampant Growth"])
        self.assertEqual("In=Sol Ring;In=Rampant Growth", str(query))

    def test_out_str(self):
        query = EdhRecFilterQuery(card_out=["One With Nothing", "Savannah Lions"])
        self.assertEqual("Out=One With Nothing;Out=Savannah Lions", str(query))

    def test_out_in_str(self):
        query = EdhRecFilterQuery(
            card_out=["One With Nothing"],
            card_in=["Sol Ring"],
        )
        self.assertEqual("Out=One With Nothing;In=Sol Ring", str(query))

    def test_at_least_10_creatures_enum(self):
        query = EdhRecFilterQuery(
            count={
                EdhRecFilterType.CREATURE: {
                    "value": 10,
                    "operator": EdhRecFilterOperator.LESS_THAN,
                }
            }
        )

        self.assertEqual("c:lt=10", str(query))

    def test_at_least_10_creatures_const(self):
        query = EdhRecFilterQuery(count={"c": {"value": 10, "operator": "lt"}})

        self.assertEqual("c:lt=10", str(query))

    def test_equal_30_instant_const(self):
        query = EdhRecFilterQuery(count={"i": {"value": 30, "operator": "eq"}})

        self.assertEqual("i:eq=30", str(query))

    def test_two_operators(self):
        query = EdhRecFilterQuery(
            count={
                "i": {"value": 30, "operator": "eq"},
                "p": {"value": 1, "operator": "lt"},
            }
        )

        self.assertEqual("i:eq=30;p:lt=1", str(query))

    def test_all(self):
        query = EdhRecFilterQuery(
            card_out=["One With Nothing"],
            card_in=["Sol Ring"],
            count={"d": {"value": 300, "operator": "gt"}},
        )

        self.assertEqual("Out=One With Nothing;In=Sol Ring;d:gt=300", str(query))

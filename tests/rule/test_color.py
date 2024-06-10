import unittest

from mightstone.rule.models.color import Color, ColorPie, Identity, IdentityMap

White = Color(symbol="w", index=0)
Blue = Color(symbol="u", index=1)
Black = Color(symbol="b", index=2)
Red = Color(symbol="r", index=3)
Green = Color(symbol="g", index=4)
Purple = Color(symbol="p", index=5)


class TestIdentityMap(unittest.TestCase):
    def setUp(self) -> None:
        self.pie = ColorPie(colors=(Blue, Red))
        self.idmap = IdentityMap(self.pie)
        self.idmap.add([Blue])

    def test_key_access_as_identity_object(self):
        self.assertIn(Identity([Blue]), self.idmap)

    def test_key_access_as_string(self):
        self.assertIn("u", self.idmap)

    def test_key_access_bad_identity_object(self):
        self.assertNotIn(Identity([Red]), self.idmap)

    def test_key_access_bad_checksum(self):
        self.assertNotIn(100, self.idmap)

    def test_key_access_bad_string(self):
        self.assertNotIn("r", self.idmap)


class TestColorPie(unittest.TestCase):
    def test_length(self):
        pie = ColorPie(colors=(Red, Blue, Purple))
        self.assertEqual(3, len(pie))

    def test_length_with_duplicates(self):
        with self.assertRaises(ValueError):
            ColorPie(colors=(Red, Blue, Purple, Blue))

    def test_parse_identity(self):
        pie = ColorPie(colors=(Red, Blue, Purple))

        self.assertEqual(pie.parse("rp"), Identity([Red, Purple]))

    def test_access(self):
        pie = ColorPie(colors=(Red, Blue, Purple))

        self.assertEqual(pie[0], Red)
        self.assertEqual(pie[1], Blue)
        self.assertEqual(pie[2], Purple)

    def test_next_NONE(self):
        pie = ColorPie(colors=(Blue, Red, Green, Purple))

        self.assertEqual(pie.shift(Blue), Red)
        self.assertEqual(pie.shift(Red), Green)
        self.assertEqual(pie.shift(Green), Purple)
        self.assertEqual(pie.shift(Purple), Blue)

    def test_next_1(self):
        pie = ColorPie(colors=(Blue, Red, Green, Purple))

        self.assertEqual(pie.shift(Blue, 1), Red)
        self.assertEqual(pie.shift(Red, 1), Green)
        self.assertEqual(pie.shift(Green, 1), Purple)
        self.assertEqual(pie.shift(Purple, 1), Blue)

    def test_next_2(self):
        pie = ColorPie(colors=(Blue, Red, Green, Purple))

        self.assertEqual(pie.shift(Blue, 2), Green)
        self.assertEqual(pie.shift(Red, 2), Purple)
        self.assertEqual(pie.shift(Green, 2), Blue)
        self.assertEqual(pie.shift(Purple, 2), Red)

    def test_prev_1(self):
        pie = ColorPie(colors=(Blue, Red, Green, Purple))

        self.assertEqual(pie.shift(Blue, -1), Purple)
        self.assertEqual(pie.shift(Red, -1), Blue)
        self.assertEqual(pie.shift(Green, -1), Red)
        self.assertEqual(pie.shift(Purple, -1), Green)

    def test_combinations_with_one_color_pie(self):
        pie = ColorPie(colors=(Blue,))
        combi = pie.combinations()
        self.assertEqual(len(combi), 2)

        idmap = pie.build_identity_map()
        self.assertEqual(len(idmap), 2)
        self.assertIn(Identity([]), idmap)
        self.assertIn("", idmap)
        self.assertIn(Identity([Blue]), idmap)
        self.assertIn("u", idmap)

    def test_combinations_with_two_color_pie(self):
        pie = ColorPie(colors=(Blue, Red))
        combi = pie.combinations()
        self.assertEqual(len(combi), 4)

        idmap = pie.build_identity_map()

        self.assertEqual(len(idmap), 4)
        self.assertIn("", idmap)
        self.assertIn(Identity([Blue]), idmap)
        self.assertIn(Identity([Red]), idmap)
        self.assertIn(Identity([Blue, Red]), idmap)

    def test_combinations_with_three_color_pie(self):
        pie = ColorPie(colors=(Blue, Red, Green))

        combi = pie.combinations()
        self.assertEqual(len(combi), 8)

        idmap = pie.build_identity_map()
        self.assertEqual(len(idmap), 8)
        self.assertIn(Identity([]), idmap)
        self.assertIn(Identity([Blue]), idmap)
        self.assertIn(Identity([Red]), idmap)
        self.assertIn(Identity([Green]), idmap)
        self.assertIn(Identity([Blue, Red]), idmap)
        self.assertIn(Identity([Red, Green]), idmap)
        self.assertIn(Identity([Green, Red]), idmap)
        self.assertIn(Identity([Blue, Red, Green]), idmap)

    def test_combinations_with_four_color_pie(self):
        pie = ColorPie(colors=(Blue, Black, Red, Green))

        combi = pie.combinations()
        self.assertEqual(len(combi), 16)

        idmap = pie.build_identity_map()
        self.assertEqual(len(idmap), 16)
        self.assertIn("", idmap)
        self.assertIn("u", idmap)
        self.assertIn("b", idmap)
        self.assertIn("r", idmap)
        self.assertIn("g", idmap)
        self.assertIn("ub", idmap)
        self.assertIn("br", idmap)
        self.assertIn("rg", idmap)
        self.assertIn("gu", idmap)
        self.assertIn("ur", idmap)
        self.assertIn("bg", idmap)
        self.assertIn("ubr", idmap)
        self.assertIn("brg", idmap)
        self.assertIn("rgu", idmap)
        self.assertIn("urbg", idmap)

    def test_combinations_with_five_color_pie(self):
        pie = ColorPie(
            colors=(
                White,
                Blue,
                Black,
                Red,
                Green,
            )
        )

        combi = pie.combinations()
        self.assertEqual(len(combi), 32)

        idmap = pie.build_identity_map()
        self.assertEqual(len(idmap), 32)

    def test_combinations_with_six_color_pie(self):
        pie = ColorPie(colors=(White, Blue, Black, Red, Green, Purple))

        combi = pie.combinations()
        self.assertEqual(len(combi), 64)

        idmap = pie.build_identity_map()
        self.assertEqual(len(idmap), 64)


class TestIdentity(unittest.TestCase):
    def setUp(self) -> None:
        self.pie = ColorPie(colors=(Blue, Red, Purple, White))

    def test_empty(self):
        id1 = Identity([])
        self.assertEqual(id1.checksum(), 0b00)
        cl2 = Identity([])
        self.assertEqual(id1.checksum(), 0b00)

        self.assertEqual(id1, cl2)

    def test_size_1(self):
        id1 = Identity([Blue])
        self.assertEqual(id1.checksum(), 0b10)
        cl2 = Identity([Blue])
        self.assertEqual(id1.checksum(), 0b10)

        self.assertEqual(id1, cl2)

    def test_size_2(self):
        id1 = Identity([Blue, Red])
        self.assertEqual(id1.checksum(), 0b1010)
        id2 = Identity([Blue, Red])
        self.assertEqual(id1.checksum(), 0b1010)
        id3 = Identity([Red, Blue])
        self.assertEqual(id3.checksum(), 0b1010)

        self.assertEqual(id1, id2)
        self.assertEqual(id2, id3)
        self.assertEqual(id1, id3)

    def test_canonical(self):
        id1 = Identity([Blue, Red])
        self.assertEqual(id1.canonical, "ur")
        id2 = Identity([Red, Blue])
        self.assertEqual(id2.canonical, "ur")
        id3 = Identity([Red, Blue, Purple])
        self.assertEqual(id3.canonical, "urp")

    def test_name(self):
        id1 = Identity([Blue, Red])
        self.assertEqual(id1.name, "ur")

        id1.describe(name="Izzet League")
        self.assertEqual(id1.name, "Izzet League")

        id1.describe("Izzet")
        self.assertEqual(id1.name, "Izzet")
        self.assertEqual(id1.aliases, [])

    def test_aliases(self):
        id1 = Identity([Blue, Red])
        self.assertEqual(id1.aliases, [])

        id1.describe("fu", ["Izzet League"])
        self.assertEqual(id1.aliases, ["Izzet League"])

        id1.describe(aliases=["Prismari"])
        self.assertEqual(id1.aliases, ["Izzet League", "Prismari"])


class TestColor(unittest.TestCase):
    def test_white(self):
        self.assertEqual(str(White), "{W}")

    def test_blue(self):
        self.assertEqual(str(Blue), "{U}")

    def test_black(self):
        self.assertEqual(str(Black), "{B}")

    def test_red(self):
        self.assertEqual(str(Red), "{R}")

    def test_green(self):
        self.assertEqual(str(Green), "{G}")

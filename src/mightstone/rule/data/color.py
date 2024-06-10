from mightstone.rule.models.color import Color, ColorPie

White = Color(symbol="w", index=0)
Blue = Color(symbol="u", index=1)
Black = Color(symbol="b", index=2)
Red = Color(symbol="r", index=3)
Green = Color(symbol="g", index=4)

all_colors = [White, Blue, Black, Red, Green]

color_pie = ColorPie([White, Blue, Black, Red, Green])

identities = color_pie.build_identity_map()
identities.refine("", "Colorless")
identities.refine("w", "Mono-White", ["White"])
identities.refine("u", "Mono-Blue", ["Blue"])
identities.refine("b", "Mono-Black", ["Black"])
identities.refine("r", "Mono-Red", ["Red"])
identities.refine("g", "Mono-Green", ["Green"])
identities.refine("wu", "Azorius", ["Azorius Senate"])
identities.refine("ub", "Dimir", ["House Dimir"])
identities.refine("br", "Rakdos", ["Cult of Rakdos"])
identities.refine("rg", "Gruul", ["Gruul Clans"])
identities.refine("gu", "Simic", ["Simic Combine", "Quandrix"])
identities.refine(
    "gw",
    "Selesnya",
    ["Selesnya Conclave"],
)
identities.refine("wb", "Orzhov", ["Orzhov Syndicate", "Silverquill"])
identities.refine("ur", "Izzet", ["Izzet League", "Prismari"])
identities.refine("rw", "Boros", ["Boros Legion", "Lorehold"])
identities.refine("gb", "Golgari", ["Golgari Swarm", "Witherbloom"])
identities.refine("wub", "Esper", ["Obscura"])
identities.refine("ubr", "Grixis", ["Maestros"])
identities.refine("brg", "Jund", ["Riveteers"])
identities.refine("rgw", "Naya", ["Cabaretti"])
identities.refine("guw", "Bant", ["Brokers"])
identities.refine("wbg", "Abzan", ["Abzan Houses", "Indatha"])
identities.refine("urw", "Jeskai", ["Jeskai Way", "Raugrin"])
identities.refine("bgu", "Sultai", ["Sultai Brood", "Zagoth"])
identities.refine("rwb", "Mardu", ["Mardu Horde", "Savai"])
identities.refine("gur", "Temur", ["Temur Frontier", "Ketria"])
identities.refine("wubr", "Artifice", ["Yore-Tiller", "Green-less", "Yore"])
identities.refine("ubrg", "Chaos", ["Glint-Eye", "White-less", "Glint"])
identities.refine("brgw", "Aggression", ["Dune-Brood", "Blue-less", "Dune"])
identities.refine("rgwu", "Altruism", ["Ink-Treader", "Black-less", "Ink"])
identities.refine("gwub", "Growth", ["Witch-Maw", "Red-less", "Witch"])
identities.refine("wubrg", "Five-Color", ["5c", "Rainbow"])

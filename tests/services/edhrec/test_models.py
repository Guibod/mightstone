import pathlib
from uuid import UUID

from assertpy import assert_that

from mightstone.services.edhrec.models import (
    CollectionItem,
    CollectionItemCard,
    CollectionItemCardIncluded,
    CollectionItemCompleteCard,
    PageAverageDeck,
    PageBackground,
    PageBackgrounds,
    PageCard,
    PageCombo,
    PageCombos,
    PageCommander,
    PageCommanders,
    PageCompanions,
    PageDeck,
    PageDecks,
    PageManaStaples,
    PagePartner,
    PagePartners,
    PageSalts,
    PageSet,
    PageSets,
    PageStaples,
    PageTheme,
    PageThemes,
    PageTopCards,
    PageTypal,
    PageTypals,
    slugify,
)


class TestEdhRecItemCardIncluded:
    def test_salt_not_salt(self):
        item = CollectionItemCardIncluded(
            label="Lorem ipsum",
            inclusion=100,
            num_decks=200,
            name="Foo bar",
            sanitized="foo-bar",
            sanitized_wo="foo-bar",
        )

        assert_that(item.salt).is_none()

    def test_salt_for_salt(self):
        item = CollectionItemCardIncluded(
            label="Salt Score: 0.82\nfoo fu",
            inclusion=100,
            num_decks=200,
            name="Foo bar",
            sanitized="foo-bar",
            sanitized_wo="foo-bar",
        )

        assert_that(item.salt).is_equal_to(0.82)


class TestSlugify:
    def test_none(self):
        assert_that(slugify(None)).is_none()

    def test_empty(self):
        assert_that(slugify("")).is_equal_to("")

    def test_cased(self):
        assert_that(slugify("Lorem Ipsum")).is_equal_to("lorem-ipsum")

    def test_commander_name(self):
        assert_that(slugify("Punctuation, like a commander")).is_equal_to(
            "punctuation-like-a-commander"
        )

    def test_special_case_for_plus(self):
        assert_that(slugify("+1/+1 assault rifle")).is_equal_to(
            "plus-1-plus-1-assault-rifle"
        )


class TestModels:
    def test_page_average_deck(self):
        f = pathlib.Path(__file__).parent.joinpath("samples/average-deck.adamaro.json")
        model = PageAverageDeck.model_validate_json(f.read_bytes())

        assert_that(model).is_instance_of(PageAverageDeck)
        assert_that(model.id).is_equal_to(UUID("e569df23-4e49-5017-8959-b26b9ca2164f"))

        assert_that(model.header).is_equal_to(
            "Average Deck for Adamaro, First to Desire"
        )
        assert_that(model.description).is_equal_to("")
        assert_that(model.container.breadcrumb).is_length(2)
        assert_that(model.container.breadcrumb[0]["#"]).is_equal_to("Decks")
        assert_that(model.container.description).is_equal_to(
            "Average deck for Adamaro, First to Desire"
        )
        assert_that(model.container.keywords).contains("Adamaro")
        assert_that(model.container.title).is_equal_to(
            "Average Deck for Adamaro, First to Desire"
        )
        assert_that(model.container.data.collections).is_length(9)
        assert_that(model.get_collection("creatures").tag).is_equal_to("creatures")
        assert_that(model.get_collection("creatures").items).is_length(19)
        assert_that(model.get_collection("creatures").items[0].name).is_equal_to(
            "Balor"
        )
        assert_that(model.get_collection("creatures").items[0].sanitized).is_equal_to(
            "balor"
        )
        assert_that(model.get_collection("creatures").items[0].url).is_none()
        assert_that(model.container.data.card.cmc).is_equal_to(3)
        assert_that(model.container.data.card.prices["cardhoarder"].price).is_equal_to(
            0.02
        )
        assert_that(model.container.data.card.aetherhub_uri).is_equal_to(
            "https://aetherhub.com/Meta/Format/Commander/?com=Adamaro%2C%20First%20to%20Desire&updated=all-time"
        )
        assert_that(model.items[0].name).is_equal_to("Balor")
        assert_that(model.panels.links[0].items[0].value).is_equal_to("As commander")
        assert_that(model.panels.links[0].items[0].href).is_equal_to(
            pathlib.Path("/commanders/adamaro-first-to-desire")
        )
        assert_that(model.panels.tags).is_none()
        assert_that(model.panels.mana_curve[0]).is_equal_to(1)
        assert_that(model.panels.mana_curve[2]).is_equal_to(17)
        assert_that(model.panels.combos).is_none()
        assert_that(model.panels.articles).is_none()

    def test_page_backgrounds(self):
        f = pathlib.Path(__file__).parent.joinpath("samples/backgrounds.json")
        model = PageBackgrounds.model_validate_json(f.read_bytes())

        assert_that(model).is_instance_of(PageBackgrounds)
        assert_that(model.id).is_equal_to(UUID("cefddf50-81ef-5b98-ac45-c3582d2fe3a5"))

        assert_that(model.header).is_equal_to("Backgrounds")
        assert_that(model.description).starts_with(
            "Backgrounds is a mechanic unique to Baldur's Gate."
        )
        assert_that(model.container.breadcrumb).is_length(1)
        assert_that(model.container.breadcrumb[0]["/backgrounds"]).is_equal_to(
            "Backgrounds"
        )
        assert_that(model.container.description).is_none()
        assert_that(model.container.keywords).contains("Backgrounds")
        assert_that(model.container.title).is_equal_to("Backgrounds")
        assert_that(model.container.data.collections).is_length(2)
        assert_that(model.get_collection("commanders").tag).is_equal_to("commanders")
        assert_that(model.get_collection("commanders").items).is_length(32)
        assert_that(model.get_collection("commanders").items[0].name).is_equal_to(
            "Wilson, Refined Grizzly"
        )
        assert_that(model.get_collection("commanders").items[0].sanitized).is_equal_to(
            "wilson-refined-grizzly"
        )
        assert_that(model.get_collection("commanders").items[0].url).is_equal_to(
            pathlib.Path("/backgrounds/wilson-refined-grizzly")
        )
        assert_that(model.container.data.card).is_none()
        assert_that(model.items[0].name).is_equal_to("Raised by Giants")

    def test_page_background_raised_by_giants(self):
        f = pathlib.Path(__file__).parent.joinpath(
            "samples/background.raised-by-giants.json"
        )
        model = PageBackground.model_validate_json(f.read_bytes())
        assert_that(model.id).is_equal_to(UUID("bbbf35c7-c0cc-5462-8485-8a5d9d921cce"))

        assert_that(model).is_instance_of(PageBackground)
        assert_that(model.header).is_equal_to("Raised by Giants (Pairings)")
        assert_that(model.description).is_equal_to("")
        assert_that(model.partners).is_length(32)
        assert_that(model.partners[0].href).is_equal_to(
            pathlib.Path("/commanders/baeloth-barrityl-entertainer-raised-by-giants")
        )
        assert_that(model.container.breadcrumb).is_length(2)
        assert_that(model.container.breadcrumb[0]["/backgrounds"]).is_equal_to(
            "Backgrounds"
        )
        assert_that(model.container.description).is_none()
        assert_that(model.container.keywords).contains("Pairings")
        assert_that(model.container.title).is_equal_to("Raised by Giants (Pairings)")
        assert_that(model.container.data.collections).is_length(1)
        assert_that(model.get_collection("").tag).is_equal_to("")
        assert_that(model.get_collection("").items).is_length(32)
        assert_that(model.get_collection("").items[0].name).is_equal_to(
            "Baeloth Barrityl, Entertainer"
        )
        assert_that(model.get_collection("").items[0].sanitized).is_equal_to(
            "baeloth-barrityl-entertainer"
        )
        assert_that(model.get_collection("").items[0].url).is_equal_to(
            pathlib.Path("/commanders/baeloth-barrityl-entertainer-raised-by-giants")
        )
        assert_that(model.container.data.card).is_instance_of(
            CollectionItemCompleteCard
        )
        assert_that(model.items[0].name).is_equal_to("Baeloth Barrityl, Entertainer")

    def test_page_combo(self):
        f = pathlib.Path(__file__).parent.joinpath("samples/combo.1478-3293.json")
        model = PageCombo.model_validate_json(f.read_bytes())

        assert_that(model).is_instance_of(PageCombo)
        assert_that(model.id).is_equal_to(UUID("6a7704b6-73ec-5c43-a79f-b22e55ddec5b"))

        assert_that(model.header).is_equal_to("Emeria Shepherd + Sakura-Tribe Elder")
        assert_that(model.description).starts_with("Result: Put all basic Plains")
        assert_that(model.combo.combo_id).is_equal_to("1478-3293")
        assert_that(model.combo.require_txt).starts_with(
            "Emeria Shepherd must be on the battlefield."
        )
        assert_that(model.combo.results_txt).starts_with(
            "Put all basic Plains from your librar"
        )
        assert_that(model.combo.process_txt[0]).starts_with(
            "Activate Sakura-Tribe Elder by sacrificing it,"
        )
        assert_that(model.items).is_length(333)
        assert_that(model.items[0]).is_instance_of(CollectionItem)
        assert_that(model.items[0].name).is_equal_to("Emeria Shepherd")
        assert_that(model.items[0].sanitized).is_equal_to("emeria-shepherd")
        assert_that(model.items[0].url).is_equal_to(
            pathlib.Path("/combos/emeria-shepherd")
        )
        assert_that(model.items[1]).is_instance_of(CollectionItem)
        assert_that(model.items[2]).is_instance_of(CollectionItemCard)
        assert_that(model.items[2].name).is_equal_to("Karametra, God of Harvests")
        assert_that(model.items[2].num_decks).is_equal_to(1591)
        assert_that(model.items[3].name).is_equal_to("Obuun, Mul Daya Ancestor")
        assert_that(model.items[3].num_decks).is_equal_to(629)
        assert_that(model.items[4].name).is_equal_to("Maja, Bretagard Protector")
        assert_that(model.items[4].num_decks).is_equal_to(135)

    def test_page_combos_selesnya(self):
        f = pathlib.Path(__file__).parent.joinpath("samples/combos.gw.json")
        model = PageCombos.model_validate_json(f.read_bytes())

        assert_that(model).is_instance_of(PageCombos)
        assert_that(model.id).is_equal_to(UUID("15ca6f16-8a1a-59ef-a1e9-afdf0cc1370b"))
        assert_that(model.header).is_equal_to("Selesnya Combos")
        assert_that(model.description).starts_with(
            "Submit your own combos and corrections to"
        )
        assert_that(model.items).is_length(288)
        assert_that(model.items[0]).is_instance_of(CollectionItem)
        assert_that(model.items[0].name).is_equal_to("Devoted Druid")
        assert_that(model.items[0].sanitized).is_equal_to("devoted-druid")
        assert_that(model.items[0].url).is_equal_to(
            pathlib.Path("/combos/gw/3807-4762")
        )

    def test_page_combos(self):
        f = pathlib.Path(__file__).parent.joinpath("samples/combos.json")
        model = PageCombos.model_validate_json(f.read_bytes())

        assert_that(model).is_instance_of(PageCombos)
        assert_that(model.id).is_equal_to(UUID("ca256011-e60b-5e8a-b14e-344d44d04ce4"))
        assert_that(model.header).is_equal_to("Combos")
        assert_that(model.description).is_equal_to("")
        assert_that(model.items).is_length(0)

    def test_page_card_charging_badger(self):
        f = pathlib.Path(__file__).parent.joinpath("samples/card.charging-badger.json")
        model = PageCard.model_validate_json(f.read_bytes())

        assert_that(model).is_instance_of(PageCard)
        assert_that(model.id).is_equal_to(UUID("89cd19a9-ce9f-5a4c-9ee4-9eb567134043"))
        assert_that(model.header).is_equal_to("Charging Badger (Card)")
        assert_that(model.description).is_equal_to("")
        assert_that(model.similar).is_length(6)
        assert_that(model.items).is_length(344)
        assert_that(model.get_collection("topcommanders").items).is_length(5)

    def test_page_commander_angus(self):
        f = pathlib.Path(__file__).parent.joinpath("samples/commander.angus.json")
        model = PageCommander.model_validate_json(f.read_bytes())

        assert_that(model).is_instance_of(PageCommander)
        assert_that(model.id).is_equal_to(UUID("d490ea21-4411-5b10-81f9-a860bad2ba8b"))
        assert_that(model.header).is_equal_to("Angus Mackenzie (Commander)")
        assert_that(model.description).is_equal_to("")
        assert_that(model.items).is_length(342)
        assert_that(model.similar).is_length(6)

    def test_page_commanders_black(self):
        f = pathlib.Path(__file__).parent.joinpath("samples/commanders.b.json")
        model = PageCommanders.model_validate_json(f.read_bytes())

        assert_that(model).is_instance_of(PageCommanders)
        assert_that(model.id).is_equal_to(UUID("3733cb91-528a-58fa-a791-967f3a47de9b"))
        assert_that(model.header).is_equal_to("Top Mono-Black Commanders")
        assert_that(model.description).is_equal_to("")
        assert_that(model.items).is_length(291)
        assert_that(model.get_collection("mono-blackcommanders").items).is_length(100)
        assert_that(model.get_collection("mono-blackcommanders").more).is_equal_to(
            pathlib.Path("commanders/b-mono-blackcommanders-1.json")
        )
        assert_that(model.related_info.tribes[0].name).is_equal_to("Rats")
        assert_that(model.related_info.tribes[0].url).is_equal_to(
            pathlib.Path("/typal/rats/b")
        )

    def test_page_commanders_year(self):
        f = pathlib.Path(__file__).parent.joinpath("samples/commanders.year.json")
        model = PageCommanders.model_validate_json(f.read_bytes())

        assert_that(model).is_instance_of(PageCommanders)
        assert_that(model.id).is_equal_to(UUID("535f5454-01a0-5beb-bfa9-26c20a2300f7"))
        assert_that(model.header).is_equal_to("Top Commanders (Past 2 Years)")
        assert_that(model.description).is_equal_to("")
        assert_that(model.items).is_length(4975)
        assert_that(model.get_collection("past2years").items).is_length(100)
        assert_that(model.get_collection("past2years").more).is_equal_to(
            pathlib.Path("commanders/year-past2years-1.json")
        )
        assert_that(model.related_info).is_none()

    def test_page_companion_lurrus(self):
        f = pathlib.Path(__file__).parent.joinpath("samples/companion.lurrus.json")
        model = PageTheme.model_validate_json(f.read_bytes())

        assert_that(model).is_instance_of(PageTheme)
        assert_that(model.id).is_equal_to(UUID("fca3f270-9629-57da-b317-8d6714d355cf"))
        assert_that(model.header).is_equal_to("Lurrus Companion Theme")
        assert_that(model.description).starts_with("Also see related <a hre")
        assert_that(model.items).is_length(369)
        assert_that(model.get_collection("topcommanders").items).is_length(9)
        assert_that(model.get_collection("topcommanders").more).is_none()

    def test_page_companions(self):
        f = pathlib.Path(__file__).parent.joinpath("samples/companions.json")
        model = PageCompanions.model_validate_json(f.read_bytes())

        assert_that(model).is_instance_of(PageCompanions)
        assert_that(model.header).is_equal_to("All Companions")
        assert_that(model.description).is_equal_to("")
        assert_that(model.items).is_length(9)
        assert_that(model.get_collection("companions").items).is_length(9)
        assert_that(model.get_collection("companions").more).is_none()

    def test_page_deck(self):
        f = pathlib.Path(__file__).parent.joinpath(
            "samples/deck.kxd1YhFNO9SSTqGST2veBw.json"
        )
        model = PageDeck.model_validate_json(f.read_bytes())

        assert_that(model).is_instance_of(PageDeck)
        assert_that(model.id).is_equal_to(UUID("0571eb12-e652-52ec-be35-506c07ed0f14"))
        assert_that(model.header).is_equal_to("Deck with Aegar, the Freezing Flame")
        assert_that(model.description).starts_with(
            '<a href="https://www.cardkingdom.com/b'
        )
        assert_that(len(model.items)).is_greater_than(50)
        assert_that(model.items[0]).is_instance_of(str)
        assert_that(model.get_collection("creature").items).is_length(29)
        assert_that(model.get_collection("creature").more).is_none()

    def test_page_decks_aegar(self):
        f = pathlib.Path(__file__).parent.joinpath("samples/decks.aegar.json")
        model = PageDecks.model_validate_json(f.read_bytes())

        assert_that(model).is_instance_of(PageDecks)
        assert_that(model.header).is_equal_to("Decks with Aegar, the Freezing Flame")
        assert_that(model.description).is_equal_to("")
        assert_that(model.items).is_length(2563)
        assert_that(model.items[0].urlhash).is_equal_to("GZhX9YSjArNKKhK1SA0-nA")
        assert_that(model.items[0].tribe).is_equal_to("Giant")
        assert_that(model.items[0].theme).is_none()
        assert_that(model.similar).is_length(6)
        assert_that(model.similar[0].name).is_equal_to("Maelstrom Wanderer")
        assert_that(model.deck).is_length(82)
        assert_that(model.deck[0]).is_equal_to("1 Aegar, the Freezing Flame")

    def test_page_mana_staples(self):
        f = pathlib.Path(__file__).parent.joinpath("samples/manastaples.ub.json")
        model = PageManaStaples.model_validate_json(f.read_bytes())

        assert_that(model).is_instance_of(PageManaStaples)
        assert_that(model.header).is_equal_to("Top Dimir Mana Staples")
        assert_that(model.description).is_equal_to("")
        assert_that(model.items).is_length(30)
        assert_that(model.get_collection("dimirmanastaples").items).is_length(30)
        assert_that(model.get_collection("dimirmanastaples").more).is_none()

    def test_page_partner_rohgahh(self):
        f = pathlib.Path(__file__).parent.joinpath("samples/partner.rohgahh.json")
        model = PagePartner.model_validate_json(f.read_bytes())

        assert_that(model).is_instance_of(PagePartner)
        assert_that(model.header).is_equal_to("Rograkh, Son of Rohgahh (Pairings)")
        assert_that(model.description).is_equal_to("")
        assert_that(model.partners[0].value).is_equal_to(
            "Ardenn, Intrepid Archaeologist"
        )
        assert_that(model.items).is_length(57)
        assert_that(model.get_collection("partners").items).is_length(57)
        assert_that(model.get_collection("partners").more).is_none()

    def test_page_partners(self):
        f = pathlib.Path(__file__).parent.joinpath("samples/partners.json")
        model = PagePartners.model_validate_json(f.read_bytes())

        assert_that(model).is_instance_of(PagePartners)
        assert_that(model.header).is_equal_to("Partners")
        assert_that(model.description).is_equal_to("")
        assert_that(model.items).is_length(109)
        assert_that(model.get_collection("doctors").items).is_length(44)
        assert_that(model.get_collection("doctors").more).is_none()

    def test_page_set_rna(self):
        f = pathlib.Path(__file__).parent.joinpath("samples/set.rna.json")
        model = PageSet.model_validate_json(f.read_bytes())

        assert_that(model).is_instance_of(PageSet)
        assert_that(model.header).is_equal_to("Ravnica Allegiance")
        assert_that(model.description).is_equal_to("")
        assert_that(model.items).is_length(276)
        assert_that(model.get_collection("reprints").items).is_length(26)

    def test_page_sets(self):
        f = pathlib.Path(__file__).parent.joinpath("samples/sets.json")
        model = PageSets.model_validate_json(f.read_bytes())

        assert_that(model).is_instance_of(PageSets)
        assert_that(model.header).is_equal_to("All Sets")
        assert_that(model.description).starts_with(
            "These are the most popular cards from each set."
        )
        assert_that(model.items).is_length(0)

    def test_page_staples(self):
        f = pathlib.Path(__file__).parent.joinpath("samples/staples.rg.json")
        model = PageStaples.model_validate_json(f.read_bytes())

        assert_that(model).is_instance_of(PageStaples)
        assert_that(model.header).is_equal_to("Top Gruul Staples")
        assert_that(model.description).is_equal_to("")
        assert_that(model.items).is_length(72)
        assert_that(model.get_collection("gruulstaples").items).is_length(72)

    def test_page_theme_toughness(self):
        f = pathlib.Path(__file__).parent.joinpath("samples/theme.toughness.json")
        model = PageTheme.model_validate_json(f.read_bytes())

        assert_that(model).is_instance_of(PageTheme)
        assert_that(model.header).is_equal_to("Toughness Theme")
        assert_that(model.description).starts_with("This theme is based on creatures")
        assert_that(model.items).is_length(374)
        assert_that(model.get_collection("topcommanders").items).is_length(15)

    def test_page_themes(self):
        f = pathlib.Path(__file__).parent.joinpath("samples/themes.json")
        model = PageThemes.model_validate_json(f.read_bytes())

        assert_that(model).is_instance_of(PageThemes)
        assert_that(model.header).is_equal_to("All Themes")
        assert_that(model.description).is_equal_to("")
        assert_that(model.items).is_length(126)
        assert_that(model.get_collection("themesbypopularitysort").items).is_length(100)
        assert_that(model.get_collection("themesbypopularitysort").more).is_true()

    def test_page_top_salts(self):
        f = pathlib.Path(__file__).parent.joinpath("samples/top.salts.json")
        model = PageSalts.model_validate_json(f.read_bytes())

        assert_that(model).is_instance_of(PageSalts)
        assert_that(model.header).is_equal_to("Top 100 Saltiest Cards")
        assert_that(model.description).is_equal_to(
            "https://www.youtube.com/watch?v=45sBVYtMQSg"
        )
        assert_that(model.items).is_length(27504)
        assert_that(model.get_collection("").items).is_length(100)
        assert_that(model.get_collection("").more).is_true()

    def test_page_top_sorceries(self):
        f = pathlib.Path(__file__).parent.joinpath("samples/top.sorceries.json")
        model = PageTopCards.model_validate_json(f.read_bytes())

        assert_that(model).is_instance_of(PageTopCards)
        assert_that(model.header).is_equal_to("Top Sorceries (Past 2 Years)")
        assert_that(model.description).is_equal_to("")
        assert_that(model.items).is_length(2991)
        assert_that(model.get_collection("topsorceries(past2years)").items).is_length(
            100
        )
        assert_that(model.get_collection("topsorceries(past2years)").more).is_true()

    def test_page_top_years(self):
        f = pathlib.Path(__file__).parent.joinpath("samples/top.year.json")
        model = PageTopCards.model_validate_json(f.read_bytes())

        assert_that(model).is_instance_of(PageTopCards)
        assert_that(model.header).is_equal_to("Top Cards (Past 2 Years)")
        assert_that(model.description).is_equal_to("")
        assert_that(model.items).is_length(26496)
        assert_that(model.get_collection("past2years").items).is_length(100)
        assert_that(model.get_collection("past2years").more).is_true()

    def test_page_typal_zombies(self):
        f = pathlib.Path(__file__).parent.joinpath("samples/typal.zombies.json")
        model = PageTypal.model_validate_json(f.read_bytes())

        assert_that(model).is_instance_of(PageTypal)
        assert_that(model.header).is_equal_to("Zombies")
        assert_that(model.description).is_equal_to("")
        assert_that(model.items).is_length(379)
        assert_that(model.get_collection("topcommanders").items).is_length(15)
        assert_that(model.get_collection("topcommanders").more).is_none()

    def test_page_typals(self):
        f = pathlib.Path(__file__).parent.joinpath("samples/typals.json")
        model = PageTypals.model_validate_json(f.read_bytes())

        assert_that(model).is_instance_of(PageTypals)
        assert_that(model.header).is_equal_to("Typal")
        assert_that(model.description).is_equal_to("")
        assert_that(model.items).is_length(161)
        assert_that(model.get_collection("subtypes").items).is_length(100)
        assert_that(model.get_collection("subtypes").more).is_true()

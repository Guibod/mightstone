from pathlib import Path

import pytest
from assertpy import assert_that

from mightstone.services import ServiceError
from mightstone.services.edhrec.api import (
    EdhRecApi,
    EdhRecProxiedStatic,
    EnumColor,
    EnumCost,
    EnumIdentity,
)
from mightstone.services.edhrec.models import (
    CollectionItem,
    CollectionItemCard,
    CollectionItemCardIncluded,
    CollectionItemCardSynergy,
    CollectionItemCompleteCard,
    EdhRecCommanderDistribution,
    EnumPeriod,
    EnumType,
    FilterComparator,
    FilterOperator,
    FilterQuery,
    FilterType,
    Page,
    PageAverageDeck,
    PageBackground,
    PageBackgrounds,
    PageCombo,
    PageCombos,
    PageCommander,
    PageCommanders,
    PageCompanions,
    PageDeck,
    PageDecks,
    PagePartner,
    PagePartners,
    PageSalts,
    PageSet,
    PageStaples,
    PageTheme,
    PageTopCards,
    PageTypal,
    PageTypals,
    Panel,
    Recommendation,
    RelatedInfoPageTheme,
)


@pytest.fixture(scope="module")
def static_client():
    return EdhRecProxiedStatic()


@pytest.fixture(scope="module")
def api_client():
    return EdhRecApi()


@pytest.mark.skip_remote_api
@pytest.mark.asyncio
class TestEdhRecApi:
    async def test_recommendations_gyome(self, api_client: EdhRecApi):
        cards = [
            "Academy Manufactor",
            "Agent of the Iron Throne",
            "Assassin's Trophy",
            "Bake into a Pie",
            "Bala Ged Recovery / Bala Ged Sanctuary",
            "Beast Within",
            "Birds of Paradise",
            "Bojuka Bog",
            "Braids, Arisen Nightmare",
            "Bristlebud Farmer",
            "Cauldron Familiar",
            "Chatterfang, Squirrel General",
            "Command Tower",
            "Cranial Plating",
            "Culling Ritual",
            "Cultivate",
            "Darkbore Pathway / Slitherbore Pathway",
            "Deadly Dispute",
            "Deathcap Glade",
            "Dig Up",
            "Disciple of the Vault",
            "Dockside Chef",
            "Elvish Mystic",
            "Eternal Witness",
            "Exotic Orchard",
            "Fabled Passage",
            "Fangren Marauder",
        ]
        recs = await api_client.recommendations_async(["Gyome, master chef"], cards)

        assert_that(recs.deck.keys()).is_length(27)
        assert_that(recs.out_recs).is_length(27)
        assert isinstance(recs.out_recs[0], Recommendation)
        assert_that(recs.out_recs[0].score).is_greater_than(recs.out_recs[10].score)
        assert_that(recs.in_recs).is_length(100)
        assert isinstance(recs.in_recs[0], Recommendation)
        assert_that(recs.in_recs[0].score).is_greater_than(recs.in_recs[10].score)
        assert_that(recs.commanders).is_length(1)
        assert isinstance(recs.commanders[0], Recommendation)
        assert_that(recs.commanders[0].name).is_equal_to("Gyome, Master Chef")
        assert_that(recs.commanders[0].primary_type).is_equal_to("Creature")
        assert_that(recs.commanders[0].salt).is_greater_than(0)
        assert_that(recs.commanders[0].names[0]).is_equal_to("Gyome, Master Chef")
        assert_that(recs.commanders[0].score).is_none()

    async def test_recommendations_unknown_commander(self, api_client: EdhRecApi):
        with pytest.raises(ServiceError) as e:
            await api_client.recommendations_async(
                ["Fog"],
                ["Llaanouwar Elfe", "Forrrrest", "Languished Unmaking", "Ulamog"],
            )

        assert_that(e.value.message).contains(
            "Sorry, our data for this commander isn't ready yet."
        )
        assert_that(e.value.status).is_equal_to(200)
        assert_that(e.value.url).is_equal_to("https://edhrec.com/api/recs/")

    async def test_recommendations_vague_commander(self, api_client: EdhRecApi):
        with pytest.raises(ServiceError) as e:
            await api_client.recommendations_async(
                ["Ulamog"],
                ["Llaanouwar Elfe", "Forrrrest", "Languished Unmaking", "Ulamog"],
            )

        assert_that(e.value.message).contains("Unrecognized commander: Ulamog")
        assert_that(e.value.status).is_equal_to(200)
        assert_that(e.value.url).is_equal_to("https://edhrec.com/api/recs/")

    async def test_recommendations_no_correct_cards(self, api_client: EdhRecApi):
        recs = await api_client.recommendations_async(
            ["ThAlIa, HeReTic    Cathar"],
            ["Llaanouwar Elfe", "Forrrrest", "Languished Unmaking", "Ulamog"],
        )

        assert_that(recs.deck).is_length(7)
        assert_that(recs.deck.keys()).contains("Plains")
        assert_that(recs.deck.keys()).contains("Sol Ring")
        assert isinstance(recs.out_recs[0], Recommendation)
        assert_that(recs.in_recs).is_length(100)
        assert isinstance(recs.in_recs[0], Recommendation)
        assert_that(recs.commanders).is_length(1)
        assert isinstance(recs.commanders[0], Recommendation)
        assert_that(recs.commanders[0].name).is_equal_to("Thalia, Heretic Cathar")
        assert_that(recs.commanders[0].primary_type).is_equal_to("Creature")
        assert_that(recs.commanders[0].salt).is_greater_than(0)
        assert_that(recs.commanders[0].names[0]).is_equal_to("Thalia, Heretic Cathar")
        assert_that(recs.commanders[0].score).is_none()

    async def test_filter_correct(self, api_client: EdhRecApi):
        query = FilterQuery(
            card_in=["Dig up", "Assasin's trophy"],
            count={
                FilterType.ARTIFACT: FilterComparator(
                    operator=FilterOperator.GREATER_THAN, value=10
                )
            },
        )
        commander = await api_client.filter_async("Gyome, Master Chef", query)

        assert_that(commander.items).is_length(0)
        assert_that(commander.get_collection_names()).is_equal_to(
            [
                "newcards",
                "highsynergycards",
                "topcards",
                "creatures",
                "instants",
                "sorceries",
                "utilityartifacts",
                "enchantments",
                "planeswalkers",
                "utilitylands",
                "manaartifacts",
                "lands",
            ]
        )
        assert_that(commander.header).is_equal_to("Gyome, Master Chef (Commander)")
        assert isinstance(commander, PageCommander)
        assert isinstance(commander.card, CollectionItemCompleteCard)
        assert_that(commander.card.name).is_equal_to("Gyome, Master Chef")
        assert_that(commander.panels.articles).is_none()
        assert_that(commander.panels.mana_curve).contains_key(1)
        assert_that(commander.panels.mana_curve[1]).is_greater_than(0)
        assert_that(commander.panels.mana_curve).contains_key(2)
        assert_that(commander.panels.mana_curve[2]).is_greater_than(0)
        assert_that(commander.panels.mana_curve).contains_key(3)
        assert_that(commander.panels.mana_curve[3]).is_greater_than(0)
        assert_that(commander.panels.mana_curve).contains_key(4)
        assert_that(commander.panels.mana_curve[4]).is_greater_than(0)
        assert_that(commander.panels.mana_curve).contains_key(5)
        assert_that(commander.panels.mana_curve[5]).is_greater_than(0)
        assert_that(commander.panels.mana_curve).does_not_contain_key(10)
        assert_that(commander.panels.mana_curve).does_not_contain_key(20)

        assert commander.panels.themes is not None
        assert_that(len(commander.panels.themes)).is_greater_than(1)
        assert_that(commander.panels.themes[0].count).is_greater_than(1000)
        assert_that(commander.panels.tags).is_none()
        assert isinstance(commander, EdhRecCommanderDistribution)
        assert_that(commander.artifact).is_greater_than(10)
        assert_that(commander.land).is_greater_than(20)
        assert_that(len(commander.panels.links)).is_greater_than(1)
        assert_that(len(commander.panels.links[0].items)).is_greater_than(1)
        assert_that(commander.panels.links[0].items[0].href).is_not_none()

        synergy = commander.get_collection("highsynergycards")
        assert_that(synergy.items).is_length(10)
        assert isinstance(synergy.items[0], CollectionItemCompleteCard)


@pytest.mark.skip_remote_api
@pytest.mark.asyncio
class TestEdhRecStatic:
    async def test_commander_not_found(self, static_client: EdhRecProxiedStatic):
        with pytest.raises(ServiceError):
            await static_client.commander_async("This commander does not exists")

    async def test_commander_no_filter(self, static_client: EdhRecProxiedStatic):
        commander = await static_client.commander_async("Gyome, Master Chef")
        assert_that(commander.get_collection_names()).is_equal_to(
            [
                "newcards",
                "highsynergycards",
                "topcards",
                "creatures",
                "instants",
                "sorceries",
                "utilityartifacts",
                "enchantments",
                "planeswalkers",
                "utilitylands",
                "manaartifacts",
                "lands",
            ]
        )
        assert_that(commander.header).is_equal_to("Gyome, Master Chef (Commander)")
        assert isinstance(commander, PageCommander)
        assert isinstance(commander.card, CollectionItemCompleteCard)
        assert_that(commander.card.name).is_equal_to("Gyome, Master Chef")

        assert isinstance(commander.panels, Panel)
        assert_that(commander.panels.mana_curve).contains_key(1)
        assert_that(commander.panels.mana_curve[1]).is_greater_than(0)
        assert_that(commander.panels.mana_curve).contains_key(2)
        assert_that(commander.panels.mana_curve[2]).is_greater_than(0)
        assert_that(commander.panels.mana_curve).contains_key(3)
        assert_that(commander.panels.mana_curve[3]).is_greater_than(0)
        assert_that(commander.panels.mana_curve).contains_key(4)
        assert_that(commander.panels.mana_curve[4]).is_greater_than(0)
        assert_that(commander.panels.mana_curve).contains_key(5)
        assert_that(commander.panels.mana_curve[5]).is_greater_than(0)
        assert_that(commander.panels.mana_curve).does_not_contain_key(10)
        assert_that(commander.panels.mana_curve).does_not_contain_key(20)

        assert isinstance(commander.panels.articles, list)
        assert_that(len(commander.panels.articles)).is_greater_than(1)

        assert isinstance(commander.panels.themes, list)
        assert_that(len(commander.panels.themes)).is_greater_than(1)
        assert_that(commander.panels.themes[0].count).is_greater_than(1000)

        assert isinstance(commander.panels.tags, list)
        assert_that(len(commander.panels.tags)).is_greater_than(1)
        assert_that(commander.panels.tags[0].count).is_greater_than(1000)

        assert isinstance(commander, EdhRecCommanderDistribution)
        assert_that(commander.artifact).is_greater_than(1)
        assert_that(commander.land).is_greater_than(20)
        assert_that(len(commander.panels.links)).is_greater_than(1)
        assert_that(len(commander.panels.links[0].items)).is_greater_than(1)
        assert_that(commander.panels.links[0].items[0].href).is_not_none()

        synergy = commander.get_collection("highsynergycards")
        assert_that(synergy.items).is_length(10)
        assert isinstance(synergy.items[0], CollectionItemCardSynergy)
        assert_that(synergy.items[0].inclusion).is_greater_than(1000)
        assert_that(synergy.items[0].synergy).is_greater_than(0.5)
        assert_that(synergy.items[0].num_decks).is_greater_than(3000)
        assert_that(synergy.items[0].potential_decks).is_greater_than(3000)

    async def test_commander_for_sacrifice(self, static_client: EdhRecProxiedStatic):
        commander = await static_client.commander_async(
            "Gyome, Master Chef", subtype="Sacrifice"
        )

        assert_that(commander.get_collection_names()).is_equal_to(
            [
                "newcards",
                "highsynergycards",
                "topcards",
                "creatures",
                "instants",
                "sorceries",
                "utilityartifacts",
                "enchantments",
                "planeswalkers",
                "utilitylands",
                "manaartifacts",
                "lands",
            ]
        )

        assert isinstance(commander, PageCommander)
        assert_that(commander.header).is_equal_to(
            "Gyome, Master Chef (Commander) - Sacrifice Theme"
        )
        assert isinstance(commander.card, CollectionItemCompleteCard)
        assert_that(commander.card.name).is_equal_to("Gyome, Master Chef")

        assert isinstance(commander.panels, Panel)
        assert_that(commander.panels.mana_curve).contains_key(1)
        assert_that(commander.panels.mana_curve[1]).is_greater_than(0)
        assert_that(commander.panels.mana_curve).contains_key(2)
        assert_that(commander.panels.mana_curve[2]).is_greater_than(0)
        assert_that(commander.panels.mana_curve).contains_key(3)
        assert_that(commander.panels.mana_curve[3]).is_greater_than(0)
        assert_that(commander.panels.mana_curve).contains_key(4)
        assert_that(commander.panels.mana_curve[4]).is_greater_than(0)
        assert_that(commander.panels.mana_curve).contains_key(5)
        assert_that(commander.panels.mana_curve[5]).is_greater_than(0)
        assert_that(commander.panels.mana_curve).does_not_contain_key(10)
        assert_that(commander.panels.mana_curve).does_not_contain_key(20)

        assert isinstance(commander.panels.articles, list)
        assert_that(len(commander.panels.articles)).is_greater_than(1)

        assert isinstance(commander.panels.themes, list)
        assert_that(len(commander.panels.themes)).is_greater_than(1)
        assert_that(commander.panels.themes[0].count).is_greater_than(1000)

        assert isinstance(commander.panels.tags, list)
        assert_that(len(commander.panels.tags)).is_greater_than(1)
        assert_that(commander.panels.tags[0].count).is_greater_than(1000)

        assert isinstance(commander, EdhRecCommanderDistribution)
        assert_that(commander.artifact).is_greater_than(1)
        assert_that(commander.land).is_greater_than(20)
        assert_that(len(commander.panels.links)).is_greater_than(1)
        assert_that(len(commander.panels.links[0].items)).is_greater_than(1)
        assert_that(commander.panels.links[0].items[0].href).is_not_none()

    async def test_commander_for_expansive(self, static_client: EdhRecProxiedStatic):
        commander = await static_client.commander_async(
            "Gyome, Master Chef", cost=EnumCost.EXPENSIVE
        )

        assert_that(commander.get_collection_names()).is_equal_to(
            [
                "newcards",
                "highsynergycards",
                "topcards",
                "creatures",
                "instants",
                "sorceries",
                "utilityartifacts",
                "enchantments",
                "planeswalkers",
                "utilitylands",
                "manaartifacts",
                "lands",
            ]
        )

        assert isinstance(commander, PageCommander)
        assert_that(commander.header).is_equal_to(
            "Gyome, Master Chef (Commander) - Expensive "
        )
        assert isinstance(commander.card, CollectionItemCompleteCard)
        assert_that(commander.card.name).is_equal_to("Gyome, Master Chef")

        assert isinstance(commander.panels, Panel)
        assert_that(commander.panels.mana_curve).contains_key(1)
        assert_that(commander.panels.mana_curve[1]).is_greater_than(0)
        assert_that(commander.panels.mana_curve).contains_key(2)
        assert_that(commander.panels.mana_curve[2]).is_greater_than(0)
        assert_that(commander.panels.mana_curve).contains_key(3)
        assert_that(commander.panels.mana_curve[3]).is_greater_than(0)
        assert_that(commander.panels.mana_curve).contains_key(4)
        assert_that(commander.panels.mana_curve[4]).is_greater_than(0)
        assert_that(commander.panels.mana_curve).contains_key(5)
        assert_that(commander.panels.mana_curve[5]).is_greater_than(0)
        assert_that(commander.panels.mana_curve).does_not_contain_key(10)
        assert_that(commander.panels.mana_curve).does_not_contain_key(20)

        assert isinstance(commander.panels.articles, list)
        assert_that(len(commander.panels.articles)).is_greater_than(1)

        assert isinstance(commander.panels.themes, list)
        assert_that(len(commander.panels.themes)).is_greater_than(1)
        assert_that(commander.panels.themes[0].count).is_greater_than(1000)

        assert isinstance(commander.panels.tags, list)
        assert_that(len(commander.panels.tags)).is_greater_than(1)
        assert_that(commander.panels.tags[0].count).is_greater_than(1000)

        assert isinstance(commander, EdhRecCommanderDistribution)
        assert_that(commander.artifact).is_greater_than(1)
        assert_that(commander.land).is_greater_than(20)
        assert_that(len(commander.panels.links)).is_greater_than(1)
        assert_that(len(commander.panels.links[0].items)).is_greater_than(1)
        assert_that(commander.panels.links[0].items[0].href).is_not_none()

    async def test_commander_for_sacrifice_and_expansive(
        self, static_client: EdhRecProxiedStatic
    ):
        commander = await static_client.commander_async(
            "Gyome, Master Chef", cost=EnumCost.EXPENSIVE, subtype="sacrifice"
        )

        assert_that(commander.get_collection_names()).is_equal_to(
            [
                "newcards",
                "highsynergycards",
                "topcards",
                "creatures",
                "instants",
                "sorceries",
                "utilityartifacts",
                "enchantments",
                "planeswalkers",
                "utilitylands",
                "manaartifacts",
                "lands",
            ]
        )

        assert isinstance(commander, PageCommander)
        assert_that(commander.header).is_equal_to(
            "Gyome, Master Chef (Commander) - Expensive Sacrifice Theme"
        )
        assert isinstance(commander.card, CollectionItemCompleteCard)
        assert_that(commander.card.name).is_equal_to("Gyome, Master Chef")

        assert isinstance(commander.panels, Panel)
        assert_that(commander.panels.mana_curve).contains_key(1)
        assert_that(commander.panels.mana_curve[1]).is_greater_than(0)
        assert_that(commander.panels.mana_curve).contains_key(2)
        assert_that(commander.panels.mana_curve[2]).is_greater_than(0)
        assert_that(commander.panels.mana_curve).contains_key(3)
        assert_that(commander.panels.mana_curve[3]).is_greater_than(0)
        assert_that(commander.panels.mana_curve).contains_key(4)
        assert_that(commander.panels.mana_curve[4]).is_greater_than(0)
        assert_that(commander.panels.mana_curve).contains_key(5)
        assert_that(commander.panels.mana_curve[5]).is_greater_than(0)
        assert_that(commander.panels.mana_curve).does_not_contain_key(10)
        assert_that(commander.panels.mana_curve).does_not_contain_key(20)

        assert isinstance(commander.panels.articles, list)
        assert_that(len(commander.panels.articles)).is_greater_than(1)

        assert isinstance(commander.panels.themes, list)
        assert_that(len(commander.panels.themes)).is_greater_than(1)
        assert_that(commander.panels.themes[0].count).is_greater_than(1000)

        assert isinstance(commander.panels.tags, list)
        assert_that(len(commander.panels.tags)).is_greater_than(1)
        assert_that(commander.panels.tags[0].count).is_greater_than(1000)

        assert isinstance(commander, EdhRecCommanderDistribution)
        assert_that(commander.artifact).is_greater_than(1)
        assert_that(commander.land).is_greater_than(20)
        assert_that(len(commander.panels.links)).is_greater_than(1)
        assert_that(len(commander.panels.links[0].items)).is_greater_than(1)
        assert_that(commander.panels.links[0].items[0].href).is_not_none()

    async def test_typals(self, static_client: EdhRecProxiedStatic):
        typals = await static_client.typals_async()

        assert_that(typals.get_collection_names()).is_equal_to(["subtypes"])
        assert isinstance(typals, PageTypals)

        assert_that(len(typals.items)).is_greater_than(100)
        assert isinstance(typals.items[0], CollectionItemCard)
        assert_that(typals.items[0].name).is_equal_to("Dragons")
        assert_that(typals.items[0].sanitized).is_not_none()
        assert_that(typals.items[0].sanitized_wo).is_not_none()
        assert_that(typals.items[0].url).is_not_none()

        subtypes = typals.get_collection("subtypes")
        assert_that(subtypes.items).is_length(100)
        assert isinstance(subtypes.items[0], CollectionItemCardIncluded)
        assert_that(subtypes.items[0].name).is_equal_to("Dragons")
        assert_that(subtypes.items[0].num_decks).is_not_none()
        assert_that(subtypes.items[0].inclusion).is_not_none()

    async def test_typal_missing(self, static_client: EdhRecProxiedStatic):
        with pytest.raises(ServiceError):
            await static_client.typal_async("not-found")

    async def test_typal_dinosaur(self, static_client: EdhRecProxiedStatic):
        dinosaur = await static_client.typal_async("dinosaurs")

        assert isinstance(dinosaur, PageTypal)
        assert_that(dinosaur.get_collection_names()).is_equal_to(
            [
                "topcommanders",
                "newcards",
                "highsynergycards",
                "topcards",
                "creatures",
                "instants",
                "sorceries",
                "utilityartifacts",
                "enchantments",
                "battles",
                "planeswalkers",
                "utilitylands",
                "manaartifacts",
                "lands",
            ]
        )
        assert_that(dinosaur.header).is_equal_to("Dinosaurs")
        assert isinstance(dinosaur.related_info, RelatedInfoPageTheme)
        assert_that(dinosaur.related_info.colors[0].name).is_equal_to("Mono-White")
        assert_that(dinosaur.related_info.colors[0].url).is_equal_to(
            Path("/typal/dinosaurs/w")
        )

        top_commanders = dinosaur.get_collection("topcommanders")

        assert_that(len(dinosaur.items)).is_greater_than(100)
        assert isinstance(dinosaur.items[0], CollectionItemCard)
        assert_that(dinosaur.items[0].name).is_equal_to("Command Tower")
        assert_that(dinosaur.items[0].sanitized).is_not_none()
        assert_that(dinosaur.items[0].sanitized_wo).is_not_none()
        assert_that(dinosaur.items[0].url).is_not_none()

        assert_that(len(top_commanders.items)).is_greater_than(8)
        assert isinstance(top_commanders.items[0], CollectionItemCardIncluded)
        assert_that(top_commanders.items[0].name).is_equal_to("Gishath, Sun's Avatar")
        assert_that(top_commanders.items[0].num_decks).is_not_none()
        assert_that(top_commanders.items[0].inclusion).is_not_none()

    async def test_typal_dinosaur_rakdos(self, static_client: EdhRecProxiedStatic):
        dinosaur = await static_client.typal_async("dinosaurs", EnumIdentity.BR)

        assert isinstance(dinosaur, PageTypal)
        assert_that(dinosaur.get_collection_names()).is_equal_to(
            [
                "topcommanders",
                "highsynergycards",
                "topcards",
                "creatures",
                "instants",
                "sorceries",
                "utilityartifacts",
                "enchantments",
                "planeswalkers",
                "utilitylands",
                "manaartifacts",
                "lands",
            ]
        )
        assert_that(dinosaur.header).is_equal_to("Rakdos Dinosaurs")
        assert isinstance(dinosaur.related_info, RelatedInfoPageTheme)
        assert_that(dinosaur.related_info.colors[0].name).is_equal_to("Mono-White")
        assert_that(dinosaur.related_info.colors[0].url).is_equal_to(
            Path("/typal/dinosaurs/w")
        )
        assert_that(len(dinosaur.items)).is_greater_than(100)
        assert isinstance(dinosaur.items[0], CollectionItemCard)
        assert_that(dinosaur.items[0].name).is_equal_to("Olivia Voldaren")
        assert_that(dinosaur.items[0].sanitized).is_not_none()
        assert_that(dinosaur.items[0].sanitized_wo).is_not_none()
        assert_that(dinosaur.items[0].url).is_none()  # because that’s the current page

        top_commanders = dinosaur.get_collection("topcommanders")
        assert_that(top_commanders.items).is_length(1)
        assert isinstance(top_commanders.items[0], CollectionItemCardIncluded)
        assert_that(top_commanders.items[0].name).is_equal_to("Olivia Voldaren")
        assert_that(top_commanders.items[0].num_decks).is_not_none()
        assert_that(top_commanders.items[0].inclusion).is_not_none()

    async def test_themes(self, static_client: EdhRecProxiedStatic):
        themes = await static_client.themes_async()

        assert isinstance(themes, Page)
        assert_that(themes.get_collection_names()).is_equal_to(
            ["themesbypopularitysort"]
        )
        assert_that(len(themes.items)).is_greater_than(100)
        assert isinstance(themes.items[0], CollectionItemCard)
        assert_that(themes.items[0].name).is_equal_to("Artifacts")
        assert_that(themes.items[0].sanitized).is_not_none()
        assert_that(themes.items[0].sanitized_wo).is_not_none()
        assert_that(themes.items[0].url).is_not_none()

        popular = themes.get_collection("themesbypopularitysort")
        assert_that(popular.items).is_length(100)
        assert isinstance(popular.items[0], CollectionItemCardIncluded)
        assert_that(popular.items[0].name).is_equal_to("Artifacts")
        assert_that(popular.items[0].num_decks).is_not_none()
        assert_that(popular.items[0].inclusion).is_not_none()

    async def test_theme_missing(self, static_client: EdhRecProxiedStatic):
        with pytest.raises(ServiceError):
            await static_client.theme_async("not-found")

    async def test_theme_artifacts(self, static_client: EdhRecProxiedStatic):
        artifacts = await static_client.theme_async("artifacts")

        assert isinstance(artifacts, PageTheme)
        assert_that(artifacts.get_collection_names()).is_equal_to(
            [
                "topcommanders",
                "newcards",
                "highsynergycards",
                "topcards",
                "creatures",
                "instants",
                "sorceries",
                "utilityartifacts",
                "enchantments",
                "planeswalkers",
                "utilitylands",
                "manaartifacts",
                "lands",
            ]
        )
        assert_that(artifacts.header).is_equal_to("Artifact Theme")
        assert isinstance(artifacts.related_info, RelatedInfoPageTheme)
        assert_that(artifacts.related_info.colors[0].name).is_equal_to("Mono-White")
        assert_that(artifacts.related_info.colors[0].url).is_equal_to(
            Path("/themes/artifacts/w")
        )
        assert_that(len(artifacts.items)).is_greater_than(100)
        assert isinstance(artifacts.items[0], CollectionItemCard)
        assert_that(artifacts.items[0].name).is_equal_to("Sol Ring")
        assert_that(artifacts.items[0].sanitized).is_not_none()
        assert_that(artifacts.items[0].sanitized_wo).is_not_none()
        assert_that(artifacts.items[0].url).is_not_none()

        cards = artifacts.get_collection("creatures")
        assert_that(len(cards.items)).is_greater_than(40)
        assert isinstance(cards.items[0], CollectionItemCardIncluded)
        assert_that(cards.items[0].name).is_equal_to("Scrap Trawler")
        assert_that(cards.items[0].num_decks).is_not_none()
        assert_that(cards.items[0].inclusion).is_not_none()

    async def test_theme_artifacts_azorius(self, static_client: EdhRecProxiedStatic):
        artifacts = await static_client.theme_async("artifacts", EnumIdentity.WU)

        assert isinstance(artifacts, PageTheme)
        assert_that(artifacts.get_collection_names()).is_equal_to(
            [
                "topcommanders",
                "newcards",
                "highsynergycards",
                "topcards",
                "creatures",
                "instants",
                "sorceries",
                "utilityartifacts",
                "enchantments",
                "planeswalkers",
                "utilitylands",
                "manaartifacts",
                "lands",
            ]
        )
        assert_that(artifacts.header).is_equal_to("Azorius Artifact Theme")

        assert isinstance(artifacts.related_info, RelatedInfoPageTheme)
        assert_that(artifacts.related_info.colors[0].name).is_equal_to("Mono-White")
        assert_that(artifacts.related_info.colors[0].url).is_equal_to(
            Path("/themes/artifacts/w")
        )

        assert_that(len(artifacts.items)).is_greater_than(100)
        assert isinstance(artifacts.items[0], CollectionItemCard)
        assert_that(artifacts.items[0].name).is_equal_to("Sol Ring")
        assert_that(artifacts.items[0].sanitized).is_not_none()
        assert_that(artifacts.items[0].sanitized_wo).is_not_none()
        assert_that(artifacts.items[0].url).is_not_none()
        assert_that(artifacts.items[0].num_decks).is_not_none()

        cards = artifacts.get_collection("creatures")
        assert_that(len(cards.items)).is_greater_than(40)
        assert isinstance(cards.items[0], CollectionItemCardIncluded)
        assert_that(cards.items[0].name).is_equal_to("Esper Sentinel")
        assert_that(cards.items[0].num_decks).is_not_none()
        assert_that(cards.items[0].inclusion).is_not_none()

    async def test_set_guilds_of_ravnica(self, static_client: EdhRecProxiedStatic):
        grn = await static_client.set_async("grn")

        assert isinstance(grn, PageSet)
        assert_that(grn.get_collection_names()).is_equal_to(
            ["commanders", "cards", "reprints"]
        )
        assert_that(grn.header).is_equal_to("Guilds of Ravnica")

        assert isinstance(grn.items[0], CollectionItemCard)
        assert_that(grn.items[0].name).is_equal_to("Swamp")
        assert_that(grn.items[0].sanitized).is_not_none()
        assert_that(grn.items[0].sanitized_wo).is_not_none()
        assert_that(grn.items[0].url).is_not_none()
        assert_that(grn.items[0].num_decks).is_not_none()

        cards = grn.get_collection("cards")
        assert_that(len(cards.items)).is_greater_than(100)
        assert isinstance(cards.items[0], CollectionItemCardIncluded)
        assert_that(cards.items[0].name).is_equal_to("Assassin's Trophy")
        assert_that(cards.items[0].num_decks).is_not_none()
        assert_that(cards.items[0].inclusion).is_not_none()

    async def test_salt_no_year(self, static_client: EdhRecProxiedStatic):
        salt = await static_client.salt_async()

        assert isinstance(salt, PageSalts)
        assert_that(salt.get_collection_names()).is_equal_to([""])
        assert_that(salt.header).is_equal_to("Top 100 Saltiest Cards")

        assert_that(len(salt.items)).is_greater_than(10000)
        assert isinstance(salt.items[0], CollectionItemCard)
        assert_that(salt.items[0].name).is_equal_to("Sol Ring")
        assert_that(salt.items[0].num_decks).is_not_none()

        sub_list = salt.get_collection("")
        assert_that(sub_list.header).is_equal_to("")
        assert_that(sub_list.items).is_length(100)

        assert isinstance(sub_list.items[0], CollectionItemCardIncluded)
        assert_that(sub_list.items[0].name).is_equal_to("Winter Orb")
        assert_that(sub_list.items[0].num_decks).is_not_none()
        assert_that(sub_list.items[0].inclusion).is_not_none()

    async def test_salt_with_year(self, static_client: EdhRecProxiedStatic):
        salt = await static_client.salt_async(2022)

        assert isinstance(salt, PageSalts)
        assert_that(salt.get_collection_names()).is_equal_to([""])
        assert_that(salt.header).is_equal_to("Top 100 Saltiest Cards (2022)")

        assert_that(len(salt.items)).is_greater_than(10000)
        assert isinstance(salt.items[0], CollectionItemCard)
        assert_that(salt.items[0].name).is_equal_to("Sol Ring")
        assert_that(salt.items[0].num_decks).is_not_none()

        sub_list = salt.get_collection("")
        assert_that(sub_list.header).is_equal_to("")
        assert_that(sub_list.items).is_length(100)

        assert isinstance(sub_list.items[0], CollectionItemCardIncluded)
        assert_that(sub_list.items[0].name).is_equal_to("Stasis")
        assert_that(sub_list.items[0].num_decks).is_not_none()
        assert_that(sub_list.items[0].inclusion).is_not_none()

    async def test_top_cards_no_parameters(self, static_client):
        cards = await static_client.top_cards_async()

        assert isinstance(cards, PageTopCards)
        assert_that(cards.get_collection_names()).is_equal_to(["pastweek"])
        assert_that(cards.header).is_equal_to("Top Cards (Past Week)")
        assert_that(len(cards.items)).is_greater_than(10000)
        assert isinstance(cards.items[0], CollectionItemCard)
        assert_that(cards.items[0].name).is_equal_to("Sol Ring")
        assert_that(cards.items[0].num_decks).is_not_none()

        past_week_list = cards.get_collection("pastweek")
        assert_that(past_week_list.items).is_length(100)
        assert isinstance(past_week_list.items[0], CollectionItemCardIncluded)
        assert_that(past_week_list.items[0].name).is_equal_to("Sol Ring")
        assert_that(past_week_list.items[0].num_decks).is_not_none()
        assert_that(past_week_list.items[0].inclusion).is_not_none()

    async def test_top_cards_with_period(self, static_client):
        cards = await static_client.top_cards_async(period=EnumPeriod.PAST_2YEAR)

        assert isinstance(cards, PageTopCards)
        assert_that(cards.get_collection_names()).is_equal_to(["past2years"])

        assert_that(cards.header).is_equal_to("Top Cards (Past 2 Years)")
        assert_that(len(cards.items)).is_greater_than(500)
        assert isinstance(cards.items[0], CollectionItemCard)
        assert_that(cards.items[0].name).is_equal_to("Sol Ring")
        assert_that(cards.items[0].num_decks).is_not_none()

        past_week_list = cards.get_collection("past2years")
        assert_that(past_week_list.items).is_length(100)
        assert isinstance(past_week_list.items[0], CollectionItemCardIncluded)
        assert_that(past_week_list.items[0].name).is_equal_to("Sol Ring")
        assert_that(past_week_list.items[0].num_decks).is_not_none()
        assert_that(past_week_list.items[0].inclusion).is_not_none()

    async def test_top_cards_with_color(self, static_client):
        cards = await static_client.top_cards_async(color=EnumColor.U)

        assert isinstance(cards, PageTopCards)
        assert_that(cards.get_collection_names()).is_equal_to(
            [
                "topcards",
                "creatures",
                "instants",
                "sorceries",
                "enchantments",
                "battles",
                "planeswalkers",
                "utilityartifacts",
                "manaartifacts",
                "utilitylands",
                "color-fixinglands",
            ]
        )

        assert_that(cards.header).is_equal_to("Top Blue Cards")
        assert_that(len(cards.items)).is_greater_than(400)
        assert isinstance(cards.items[0], CollectionItemCard)
        assert_that(cards.items[0].name).is_equal_to("Island")
        assert_that(cards.items[0].num_decks).is_not_none()

        past_week_list = cards.get_collection("topcards")
        assert_that(past_week_list.items).is_length(100)
        assert isinstance(past_week_list.items[0], CollectionItemCardIncluded)
        assert_that(past_week_list.items[0].name).is_equal_to("Counterspell")
        assert_that(past_week_list.items[0].num_decks).is_not_none()
        assert_that(past_week_list.items[0].inclusion).is_not_none()

    async def test_top_cards_with_type(self, static_client):
        cards = await static_client.top_cards_async(type=EnumType.BATTLE)

        assert isinstance(cards, PageTopCards)
        assert_that(cards.get_collection_names()).is_equal_to(
            ["topbattles(past2years)"]
        )

        assert_that(cards.header).is_equal_to("Top Battles (Past 2 Years)")
        assert_that(len(cards.items)).is_greater_than(35)
        assert isinstance(cards.items[0], CollectionItemCard)
        assert_that(cards.items[0].name).is_equal_to("Invasion of Ikoria")
        assert_that(cards.items[0].num_decks).is_not_none()

        past_week_list = cards.get_collection("topbattles(past2years)")
        assert_that(len(past_week_list.items)).is_greater_than(35)
        assert isinstance(past_week_list.items[0], CollectionItemCardIncluded)
        assert_that(past_week_list.items[0].name).is_equal_to("Invasion of Ikoria")
        assert_that(past_week_list.items[0].num_decks).is_not_none()
        assert_that(past_week_list.items[0].inclusion).is_not_none()

    async def test_companions(self, static_client):
        page = await static_client.companions_async()

        assert isinstance(page, PageCompanions)
        assert_that(page.get_collection_names()).is_equal_to(["companions"])

        assert_that(page.header).is_equal_to("All Companions")
        assert_that(page.items).is_length(9)
        assert isinstance(page.items[0], CollectionItemCard)
        assert_that(page.items[0].name).is_equal_to("Kaheera, the Orphanguard")
        assert_that(page.items[0].num_decks).is_not_none()

        companions = page.get_collection("companions")
        assert_that(companions.items).is_length(9)
        assert isinstance(companions.items[0], CollectionItemCardIncluded)
        assert_that(companions.items[0].name).is_equal_to("Gyruda, Doom of Depths")
        assert_that(companions.items[0].num_decks).is_not_none()
        assert_that(companions.items[0].inclusion).is_not_none()

    async def test_companion_obosh(self, static_client):
        page = await static_client.companion_async(name="Obosh, the Preypiercer")

        assert isinstance(page, PageTheme)
        assert_that(page.get_collection_names()).is_equal_to(
            [
                "topcommanders",
                "newcards",
                "highsynergycards",
                "topcards",
                "creatures",
                "instants",
                "sorceries",
                "utilityartifacts",
                "enchantments",
                "battles",
                "planeswalkers",
                "utilitylands",
                "manaartifacts",
                "lands",
            ]
        )

        assert_that(page.header).is_equal_to("Obosh Companion Theme")
        assert_that(len(page.items)).is_greater_than(300)
        assert isinstance(page.items[0], CollectionItemCard)
        assert_that(page.items[0].name).is_equal_to("Sol Ring")
        assert_that(page.items[0].num_decks).is_not_none()

        companions = page.get_collection("creatures")
        assert_that(len(companions.items)).is_greater_than(40)
        assert isinstance(companions.items[0], CollectionItemCardIncluded)
        assert_that(companions.items[0].name).is_equal_to("Mother of Runes")
        assert_that(companions.items[0].num_decks).is_not_none()
        assert_that(companions.items[0].inclusion).is_not_none()

    async def test_partners_no_parameters(self, static_client):
        page = await static_client.partners_async()

        assert isinstance(page, PagePartners)
        assert_that(page.get_collection_names()).is_equal_to(
            ["doctors", "friendsforever", "partners"]
        )

        assert_that(page.header).is_equal_to("Partners")
        assert_that(len(page.items)).is_greater_than(100)
        assert isinstance(page.items[0], CollectionItemCard)
        assert_that(page.items[0].name).is_equal_to("Tymna the Weaver")
        assert_that(page.items[0].num_decks).is_not_none()

        companions = page.get_collection("friendsforever")
        assert_that(companions.items).is_length(7)
        assert isinstance(companions.items[0], CollectionItemCardIncluded)
        assert_that(companions.items[0].name).is_equal_to("Bjorna, Nightfall Alchemist")
        assert_that(companions.items[0].num_decks).is_not_none()
        assert_that(companions.items[0].inclusion).is_not_none()

    async def test_partner_anara(self, static_client):
        page = await static_client.partner_async(name="anara-wolvid-familiar")

        assert isinstance(page, PagePartner)
        assert_that(page.get_collection_names()).is_equal_to(["partners"])

        assert_that(page.header).is_equal_to("Anara, Wolvid Familiar (Pairings)")
        assert_that(page.items).is_length(52)
        assert isinstance(page.items[0], CollectionItemCard)
        assert_that(page.items[0].name).is_not_none()
        assert_that(page.items[0].num_decks).is_not_none()

        companions = page.get_collection("partners")
        assert_that(companions.items).is_length(52)
        assert isinstance(companions.items[0], CollectionItemCardIncluded)
        assert_that(companions.items[0].name).is_not_none()
        assert_that(companions.items[0].num_decks).is_not_none()
        assert_that(companions.items[0].inclusion).is_not_none()

    async def test_commanders_no_parameters(self, static_client):
        page = await static_client.commanders_async()

        assert isinstance(page, PageCommanders)
        assert_that(page.get_collection_names()).is_equal_to(["pastweek"])

        assert_that(page.header).is_equal_to("Top Commanders (Past Week)")
        assert_that(len(page.items)).is_greater_than(2500)
        assert isinstance(page.items[0], CollectionItemCard)
        assert_that(page.items[0].name).is_not_none()
        assert_that(page.items[0].num_decks).is_not_none()

        companions = page.get_collection("pastweek")
        assert_that(companions.items).is_length(100)
        assert isinstance(companions.items[0], CollectionItemCardIncluded)
        assert_that(companions.items[0].name).is_not_none()
        assert_that(companions.items[0].num_decks).is_not_none()
        assert_that(companions.items[0].inclusion).is_not_none()

    async def test_commanders_with_period(self, static_client):
        page = await static_client.commanders_async(period=EnumPeriod.PAST_2YEAR)

        assert isinstance(page, PageCommanders)
        assert_that(page.get_collection_names()).is_equal_to(["past2years"])

        assert_that(page.header).is_equal_to("Top Commanders (Past 2 Years)")
        assert_that(len(page.items)).is_greater_than(4000)
        assert isinstance(page.items[0], CollectionItemCard)
        assert_that(page.items[0].name).is_not_none()
        assert_that(page.items[0].num_decks).is_not_none()

        past2years = page.get_collection("past2years")
        assert_that(past2years.items).is_length(100)
        assert isinstance(past2years.items[0], CollectionItemCardIncluded)
        assert_that(past2years.items[0].name).is_not_none()
        assert_that(past2years.items[0].num_decks).is_not_none()
        assert_that(past2years.items[0].inclusion).is_not_none()

    async def test_commanders_with_identity(self, static_client):
        page = await static_client.commanders_async(identity=EnumIdentity.WU)

        assert isinstance(page, PageCommanders)
        assert_that(page.get_collection_names()).is_equal_to(["azoriuscommanders"])

        assert_that(page.header).is_equal_to("Top Azorius Commanders")
        assert_that(len(page.items)).is_greater_than(300)
        assert isinstance(page.items[0], CollectionItemCard)
        assert_that(page.items[0].name).is_not_none()
        assert_that(page.items[0].num_decks).is_not_none()

        azorius = page.get_collection("azoriuscommanders")
        assert_that(azorius.items).is_length(100)
        assert isinstance(azorius.items[0], CollectionItemCardIncluded)
        assert_that(azorius.items[0].name).is_not_none()
        assert_that(azorius.items[0].num_decks).is_not_none()
        assert_that(azorius.items[0].inclusion).is_not_none()

    async def test_combos_without_identity(self, static_client):
        page = await static_client.combos_async()

        assert isinstance(page, PageCombos)
        assert_that(page.get_collection_names()).is_length(0)

        assert_that(page.header).is_equal_to("Combos")
        assert_that(page.items).is_length(0)

        assert_that(page.related_info[0].header).is_equal_to("Monocolor")
        assert isinstance(page.related_info[0].items, list)
        assert_that(page.related_info[0].items[0].text).is_equal_to("Mono-White")

    async def test_combos_with_identity(self, static_client):
        page = await static_client.combos_async(identity=EnumIdentity.WU)

        assert isinstance(page, PageCombos)
        assert_that(len(page.get_collection_names())).is_greater_than(50)

        assert_that(page.header).is_equal_to("Azorius Combos")
        assert_that(len(page.items)).is_greater_than(100)
        assert isinstance(page.items[0], CollectionItem)
        assert_that(page.items[0].name).is_not_none()

        first_combo = page.container.data.collections[0]
        assert_that(first_combo.href).is_not_none()
        assert_that(len(first_combo.items)).is_greater_than(1)
        assert isinstance(first_combo.items[0], CollectionItem)
        assert_that(first_combo.items[0].name).is_not_none()

    async def test_combos_stream(self, static_client):
        combos = [
            item
            async for item in static_client.combos_stream_async(
                identity=EnumIdentity.WU, start=10, stop=16
            )
        ]

        assert_that(combos).is_length(5)
        assert isinstance(combos[0], PageCombo)

    async def test_combos_stream_with_matcher(self, static_client):
        def my_kitten_matcher(page: PageCombo):
            return any(
                [
                    "displacer kitten" in item.name.lower()
                    for item in page.items
                    if type(item) is CollectionItem
                ],
            )

        combos_with_kitten = [
            item
            async for item in static_client.combos_stream_async(
                identity=EnumIdentity.WU, stop=20, matcher=my_kitten_matcher
            )
        ]

        assert_that(len(combos_with_kitten)).is_less_than(20)
        assert isinstance(combos_with_kitten[0], PageCombo)

    async def test_combo(self, static_client):
        page = await static_client.combo_async(
            combo_id="1170-4761-5034", identity=EnumIdentity.WU
        )

        assert isinstance(page, PageCombo)
        assert_that(page.get_collection_names()).is_equal_to(
            [
                "",
                "topcommanders",
                "newcards",
                "highsynergycards",
                "topcards",
                "creatures",
                "instants",
                "sorceries",
                "utilityartifacts",
                "enchantments",
                "battles",
                "planeswalkers",
                "utilitylands",
                "manaartifacts",
                "lands",
            ]
        )

        assert_that(page.header).is_equal_to(
            "Teferi, Time Raveler + Displacer Kitten + Sol Ring"
        )
        assert_that(len(page.combo.process_txt)).is_greater_than(1)
        assert_that(page.combo.require_txt).is_not_none()
        assert_that(page.combo.results_txt).is_not_none()
        assert_that(len(page.items)).is_greater_than(100)
        assert isinstance(page.items[0], CollectionItem)
        assert_that(page.items[0].name).is_not_none()

        the_combo = page.get_collection("")
        assert_that(len(the_combo.items)).is_greater_than(1)
        assert isinstance(the_combo.items[0], CollectionItem)
        assert_that(the_combo.items[0].name).is_not_none()

    async def test_backgrounds_without_identity(self, static_client):
        page = await static_client.backgrounds_async()

        assert isinstance(page, PageBackgrounds)
        assert_that(page.get_collection_names()).is_equal_to(
            ["commanders", "backgrounds"]
        )

        assert_that(page.header).is_equal_to("Backgrounds")
        assert_that(len(page.items)).is_greater_than(20)
        assert isinstance(page.items[0], CollectionItem)
        assert_that(page.items[0].name).is_not_none()

        backgrounds = page.get_collection("backgrounds")
        assert_that(len(backgrounds.items)).is_greater_than(10)
        assert isinstance(backgrounds.items[0], CollectionItemCardIncluded)
        assert_that(backgrounds.items[0].name).is_not_none()
        assert_that(backgrounds.items[0].num_decks).is_not_none()
        assert_that(backgrounds.items[0].inclusion).is_not_none()

    async def test_background(self, static_client):
        page = await static_client.background_async("Clan Crafter")

        assert isinstance(page, PageBackground)
        assert_that(page.get_collection_names()).is_equal_to([""])

        assert_that(page.header).is_equal_to("Clan Crafter (Pairings)")
        assert_that(len(page.items)).is_greater_than(20)
        assert isinstance(page.items[0], CollectionItem)
        assert_that(page.items[0].name).is_not_none()

        collection = page.get_collection("")
        assert_that(len(collection.items)).is_greater_than(10)
        assert isinstance(collection.items[0], CollectionItemCardIncluded)
        assert_that(collection.items[0].name).is_not_none()
        assert_that(collection.items[0].num_decks).is_not_none()
        assert_that(collection.items[0].inclusion).is_not_none()

    async def test_average_deck_without_parameters(self, static_client):
        page = await static_client.average_deck_async("gyome-master-chef")

        assert isinstance(page, PageAverageDeck)
        assert_that(page.get_collection_names()).is_equal_to(
            [
                "creatures",
                "instants",
                "sorceries",
                "artifacts",
                "enchantments",
                "battles",
                "planeswalkers",
                "lands",
                "basics",
            ]
        )

        assert_that(page.header).is_equal_to("Average Deck for Gyome, Master Chef")
        assert_that(len(page.items)).is_greater_than(20)
        assert isinstance(page.items[0], CollectionItem)
        assert_that(page.items[0].name).is_not_none()

        creatures = page.get_collection("creatures")
        assert_that(len(creatures.items)).is_greater_than(10)
        assert isinstance(creatures.items[0], CollectionItem)
        assert_that(creatures.items[0].name).is_not_none()

        assert_that(len(page.deck)).is_greater_than(70)
        assert_that(page.deck[0]).is_equal_to("1 Gyome, Master Chef")

    async def test_average_deck_with_theme(self, static_client):
        page = await static_client.average_deck_async(
            "gyome-master-chef", theme="lifegain"
        )

        assert isinstance(page, PageAverageDeck)
        assert_that(page.get_collection_names()).is_equal_to(
            [
                "creatures",
                "instants",
                "sorceries",
                "artifacts",
                "enchantments",
                "battles",
                "planeswalkers",
                "lands",
                "basics",
            ]
        )

        assert_that(page.header).is_equal_to(
            "Average Deck for Gyome, Master Chef - Lifegain Theme"
        )
        assert_that(len(page.items)).is_greater_than(20)
        assert isinstance(page.items[0], CollectionItem)
        assert_that(page.items[0].name).is_not_none()

        creatures = page.get_collection("creatures")
        assert_that(len(creatures.items)).is_greater_than(10)
        assert isinstance(creatures.items[0], CollectionItem)
        assert_that(creatures.items[0].name).is_not_none()

        assert_that(len(page.deck)).is_greater_than(70)
        assert_that(page.deck[0]).is_equal_to("1 Gyome, Master Chef")

    async def test_average_deck_with_cost(self, static_client):
        page = await static_client.average_deck_async(
            "gyome-master-chef", cost=EnumCost.BUDGET
        )

        assert isinstance(page, PageAverageDeck)
        assert_that(page.get_collection_names()).is_equal_to(
            [
                "creatures",
                "instants",
                "sorceries",
                "artifacts",
                "enchantments",
                "battles",
                "planeswalkers",
                "lands",
                "basics",
            ]
        )

        assert_that(page.header).is_equal_to(
            "Average Deck for Gyome, Master Chef - Budget "
        )
        assert_that(len(page.items)).is_greater_than(20)
        assert isinstance(page.items[0], CollectionItem)
        assert_that(page.items[0].name).is_not_none()

        creatures = page.get_collection("creatures")
        assert_that(len(creatures.items)).is_greater_than(10)
        assert isinstance(creatures.items[0], CollectionItem)
        assert_that(creatures.items[0].name).is_not_none()

        assert_that(len(page.deck)).is_greater_than(70)
        assert_that(page.deck[0]).is_equal_to("1 Gyome, Master Chef")

    async def test_average_deck_with_cost_and_theme(self, static_client):
        page = await static_client.average_deck_async(
            "gyome-master-chef", cost=EnumCost.BUDGET, theme="sacrifice"
        )

        assert isinstance(page, PageAverageDeck)
        assert_that(page.get_collection_names()).is_equal_to(
            [
                "creatures",
                "instants",
                "sorceries",
                "artifacts",
                "enchantments",
                "battles",
                "planeswalkers",
                "lands",
                "basics",
            ]
        )

        assert_that(page.header).is_equal_to(
            "Average Deck for Gyome, Master Chef - Budget Sacrifice Theme"
        )
        assert_that(len(page.items)).is_greater_than(20)
        assert isinstance(page.items[0], CollectionItem)
        assert_that(page.items[0].name).is_not_none()

        creatures = page.get_collection("creatures")
        assert_that(len(creatures.items)).is_greater_than(10)
        assert isinstance(creatures.items[0], CollectionItem)
        assert_that(creatures.items[0].name).is_not_none()

        assert_that(len(page.deck)).is_greater_than(70)
        assert_that(page.deck[0]).is_equal_to("1 Gyome, Master Chef")

    async def test_decks_without_parameters(self, static_client):
        page = await static_client.decks_async("gyome-master-chef")

        assert isinstance(page, PageDecks)
        assert_that(page.get_collection_names()).is_equal_to([])

        assert_that(page.header).is_equal_to("Decks with Gyome, Master Chef")
        assert_that(len(page.items)).is_greater_than(1000)
        assert_that(page.card).is_not_none()

        assert_that(len(page.deck)).is_greater_than(70)
        assert_that(page.deck[0]).is_equal_to("1 Gyome, Master Chef")
        assert_that(page.similar).is_not_none()

    async def test_deck_with_theme(self, static_client):
        page = await static_client.decks_async("gyome-master-chef", theme="sacrifice")

        assert isinstance(page, PageDecks)
        assert_that(page.get_collection_names()).is_equal_to([])

        assert_that(page.header).is_equal_to(
            "Decks with Gyome, Master Chef - Sacrifice Theme"
        )
        assert_that(len(page.items)).is_greater_than(1000)
        assert_that(page.card).is_not_none()

        assert_that(len(page.deck)).is_greater_than(70)
        assert_that(page.deck[0]).is_equal_to("1 Gyome, Master Chef")
        assert_that(page.similar).is_not_none()

    async def test_deck_with_cost(self, static_client):
        page = await static_client.decks_async(
            "gyome-master-chef", cost=EnumCost.BUDGET
        )

        assert isinstance(page, PageDecks)
        assert_that(page.get_collection_names()).is_equal_to([])

        assert_that(page.header).is_equal_to("Decks with Gyome, Master Chef - Budget ")
        assert_that(len(page.items)).is_greater_than(300)
        assert_that(page.card).is_not_none()

        assert_that(len(page.deck)).is_greater_than(70)
        assert_that(page.deck[0]).is_equal_to("1 Gyome, Master Chef")
        assert_that(page.similar).is_none()

    async def test_decks_with_cost_and_theme(self, static_client):
        page = await static_client.decks_async(
            "gyome-master-chef", cost=EnumCost.BUDGET, theme="sacrifice"
        )

        assert isinstance(page, PageDecks)
        assert_that(page.get_collection_names()).is_equal_to([])

        assert_that(page.header).is_equal_to(
            "Decks with Gyome, Master Chef - Budget Sacrifice Theme"
        )
        assert_that(len(page.items)).is_greater_than(100)
        assert_that(page.card).is_not_none()

        assert_that(len(page.deck)).is_greater_than(70)
        assert_that(page.deck[0]).is_equal_to("1 Gyome, Master Chef")
        assert_that(page.similar).is_none()

    async def test_staples_naya(self, static_client):
        page = await static_client.staples(EnumIdentity.RGW)

        assert isinstance(page, PageStaples)
        assert_that(page.get_collection_names()).is_equal_to(["nayastaples"])

        assert_that(page.header).is_equal_to("Top Naya Staples")
        assert_that(len(page.items)).is_greater_than(50)
        assert isinstance(page.items[0], CollectionItem)
        assert_that(page.items[0].name).is_not_none()
        assert_that(page.items[0].num_decks).is_not_none()

        staples = page.get_collection("nayastaples")
        assert_that(len(staples.items)).is_greater_than(50)
        assert isinstance(staples.items[0], CollectionItemCardIncluded)
        assert isinstance(page.items[0], CollectionItemCard)
        assert_that(page.items[0].name).is_not_none()
        assert_that(page.items[0].num_decks).is_not_none()

    async def test_mana_staples_naya(self, static_client):
        page = await static_client.mana_staples_async(EnumIdentity.RGW)

        assert isinstance(page, PageStaples)
        assert_that(page.get_collection_names()).is_equal_to(["nayamanastaples"])

        assert_that(page.header).is_equal_to("Top Naya Mana Staples")
        assert_that(len(page.items)).is_greater_than(30)
        assert isinstance(page.items[0], CollectionItem)
        assert_that(page.items[0].name).is_not_none()
        assert_that(page.items[0].num_decks).is_not_none()

        staples = page.get_collection("nayamanastaples")
        assert_that(len(staples.items)).is_greater_than(30)
        assert isinstance(staples.items[0], CollectionItemCard)
        assert_that(page.items[0].name).is_not_none()
        assert_that(page.items[0].num_decks).is_not_none()

    async def test_deck_by_id_gyome(self, static_client):
        page = await static_client.deck_async("oLLDQi-BL9Vv1ufVxA8mJA")

        assert isinstance(page, PageDeck)
        assert_that(page.get_collection_names()).is_equal_to(
            [
                "creature",
                "instant",
                "sorcery",
                "artifact",
                "enchantment",
                "battle",
                "planeswalker",
                "land",
            ]
        )

        assert_that(page.header).is_equal_to("Deck with Gyome, Master Chef")
        assert_that(len(page.items)).is_greater_than(80)
        assert_that(page.card).is_not_none()

        assert_that(page.created_at).is_not_none()
        assert_that(page.scraped_at).is_not_none()
        assert_that(page.similar).is_not_none()
        assert_that(page.cedh).is_not_none()

    async def test_deck_by_id_kenrith(self, static_client):
        page = await static_client.deck_async("PFA9Leohe7dZHkv5VRXlrw")

        assert isinstance(page, PageDeck)
        assert_that(page.get_collection_names()).is_equal_to(
            [
                "creature",
                "instant",
                "sorcery",
                "artifact",
                "enchantment",
                "battle",
                "planeswalker",
                "land",
            ]
        )

        assert_that(page.header).is_equal_to("Deck with Kenrith, the Returned King")
        assert_that(len(page.items)).is_greater_than(80)
        assert_that(page.card).is_not_none()

        assert_that(page.created_at).is_not_none()
        assert_that(page.scraped_at).is_not_none()
        assert_that(page.similar).is_not_none()
        assert_that(page.cedh).is_not_none()

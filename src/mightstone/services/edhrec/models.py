import datetime
import re
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
from uuid import UUID

from pydantic import Field, field_validator, model_validator
from pydantic_core import Url

from mightstone.common import generate_uuid_from_string
from mightstone.core import (
    MightstoneDocument,
    MightstoneModel,
    MightstoneSerializableDocument,
)

salt_parser = re.compile(r"Salt Score: (?P<salt>[\d.]+)\n")


class EnumType(str, Enum):
    CREATURE = "creatures"
    INSTANT = "instants"
    SORCERY = "sorceries"
    ARTIFACT = "artifacts"
    ARTIFACT_EQUIPMENT = "equipment"
    ARTIFACT_UTILITY = "utility-artifacts"
    ARTIFACT_MANA = "mana-artifacts"
    ENCHANTMENT = "enchantments"
    ENCHANTMENT_AURA = "auras"
    PLANESWALKER = "planeswalker"
    LAND = "lands"
    LAND_UTILITY = "utility-lands"
    LAND_FIXING = "color-fixing-lands"
    BATTLE = "battles"


class EnumPeriod(Enum):
    PAST_WEEK = "pastweek"
    PAST_MONTH = "pastmonth"
    PAST_2YEAR = "past2years"


class FilterOperator(Enum):
    GREATER_THAN = "gt"
    LESS_THAN = "lt"
    EQUAL = "eq"
    NOT_EQUAL = "ne"


class FilterType(Enum):
    CREATURE = "c"
    INSTANT = "i"
    SORCERY = "s"
    ARTIFACT = "a"
    ENCHANTMENT = "e"
    PLANESWALKER = "p"
    LANDS = "l"
    PRICE = "d"


class EdhRecCardRef(MightstoneModel):
    name: str
    url: str


class ColorReference(MightstoneModel):
    colors: list[str]
    count: int
    text: str = Field(alias="textLeft")
    url: Path


class ColorReferenceCollection(MightstoneModel):
    header: str
    items: list[ColorReference]


class ThemeReference(MightstoneModel):
    image: dict[str, Url] = {}
    count: int
    text: str = Field(alias="text_left")
    url: Path


class ThemeReferenceCollection(MightstoneModel):
    header: str
    items: list[ThemeReference]


class CommanderSubtype(MightstoneModel):
    count: int
    suffix: Path = Field(alias="href-suffix")
    value: str


class CommanderPartner(MightstoneModel):
    count: int
    href: Path
    value: str


class CommanderTag(MightstoneModel):
    count: int
    slug: str
    value: str


class CommanderIllustratedRelatedInfo(MightstoneModel):
    name: str
    count: int
    art_crop: Url
    url: Path


class EdhRecCommanderDistribution(MightstoneModel):
    artifact: int = 0
    creature: int = 0
    enchantment: int = 0
    instant: int = 0
    land: int = 0
    planeswalker: int = 0
    sorcery: int = 0
    battle: int = 0


class PriceSlug(MightstoneModel):
    price: Optional[float] = None
    slug: str


class PriceUrl(MightstoneModel):
    price: Optional[float] = None
    url: Url


class ImageUri(MightstoneModel):
    normal: Optional[Url] = None
    art_crop: Optional[Url] = None


class CollectionItem(MightstoneModel):
    """
    Representation of a basic list item
    """

    name: str
    sanitized: str
    sanitized_wo: str
    url: Optional[Path] = None

    @property
    def complete_url(self) -> Url:
        return Url(f"https://json.edhrec.com/pages{self.url}.json")


class CollectionItemCompleteCard(CollectionItem):
    cmc: int
    image_uris: list[ImageUri] = []
    layout: str
    prices: Optional[dict[str, Union[PriceUrl, PriceSlug, None]]]
    primary_type: str
    rarity: str
    salt: float
    type: str
    combos: bool
    legal_commander: Optional[bool] = False
    aetherhub_uri: Optional[str] = None
    archidekt_uri: Optional[str] = None
    deckstats_uri: Optional[str] = None
    moxfield_uri: Optional[str] = None
    mtggoldfish_uri: Optional[str] = None
    scryfall_uri: Optional[str] = None
    spellbook_uri: Optional[str] = None


class CollectionItemCard(CollectionItem):
    num_decks: int
    cards: Optional[list[EdhRecCardRef]] = None
    is_partner: Optional[bool] = False
    names: Optional[list[str]] = None


class CollectionItemCardIncluded(CollectionItemCard):
    label: str
    inclusion: int

    @property
    def salt(self) -> Optional[float]:
        match = salt_parser.match(self.label)
        if not match:
            return None
        try:
            return float(match.group("salt"))
        except ValueError:
            return None


class CollectionItemCardSynergy(CollectionItemCardIncluded):
    synergy: float
    potential_decks: int


all_sort_of_items = Union[
    CollectionItemCompleteCard,
    CollectionItemCardSynergy,
    CollectionItemCardIncluded,
    CollectionItemCard,
    CollectionItem,
]


class Collection(MightstoneModel):
    header: str
    tag: str
    items: list[all_sort_of_items] = Field(alias="cardviews")
    href: Optional[Path] = None
    more: Optional[Path] = None


class JsonDict(MightstoneModel):
    collections: Optional[list[Collection]] = Field(alias="cardlists", default=None)
    card: Optional["CollectionItemCompleteCard"] = None


class Container(MightstoneModel):
    breadcrumb: Optional[list[dict[str, str]]] = None
    description: Optional[str] = None
    data: JsonDict = Field(alias="json_dict")
    keywords: str
    title: str


class Page(MightstoneDocument):
    id: Optional[UUID] = None  # type: ignore
    header: str
    description: str
    container: Container
    items: list[all_sort_of_items] = Field(alias="cardlist", default=[])

    @model_validator(mode="wrap")
    @classmethod
    def enforce_id(cls, value: Any, handler) -> "Page":
        """
        EDHREC page are identified by their headers

        Mightstone transforms this value as a UUID.
        """
        doc = handler(value)

        if not isinstance(value, Dict):
            return doc

        if not doc.id and "id" not in value:
            if "header" in value:
                doc.id = generate_uuid_from_string(value["header"])

        return doc

    @property
    def card(self) -> Optional["CollectionItemCompleteCard"]:
        return self.container.data.card

    def get_collection_names(self) -> list[str]:
        if not self.container.data.collections:
            return []
        return [card_list.tag for card_list in self.container.data.collections]

    def get_collection(self, name: str) -> Collection:
        if not self.container.data.collections:
            raise Exception(
                f"Unknown collection '{name}'. There is no available collection."
            )

        try:
            return [
                card_list
                for card_list in self.container.data.collections
                if card_list.tag == name
            ][0]
        except IndexError:
            raise Exception(
                f"Unknown collection '{name}'. Available collections: {' '.join(self.get_collection_names())}"
            )


class LinkItem(MightstoneModel):
    current: bool = False
    href: Path
    value: str


class Link(MightstoneModel):
    header: str
    items: list[LinkItem] = []
    separator: bool = False


class ComboReference(MightstoneModel):
    value: str
    alt: str
    href: Path


class Author(MightstoneModel):
    avatar: Url
    id: int
    link: Url
    name: str


class ArticleSite(MightstoneModel):
    api: Url
    auth: str
    id: str
    name: str
    parent_page_id: Optional[int] = None
    tags: bool = False


class Article(MightstoneModel):
    alt: str
    date: datetime.date
    href: Url
    value: str
    author: Author
    site: ArticleSite

    @field_validator("date", mode="before")
    @classmethod
    def parse_date(cls, value):
        if isinstance(value, str):
            return datetime.datetime.strptime(value, "%b %d, %Y").date()
        return value


class Panel(MightstoneModel):
    links: list[Link]
    deckinfo: Optional[dict] = None
    articles: Optional[list[Article]] = None
    tags: Optional[list[CommanderTag]] = Field(alias="taglinks", default=None)
    themes: Optional[list[CommanderSubtype]] = Field(alias="tribelinks", default=None)
    mana_curve: Dict[int, int] = {i: 0 for i in range(0, 11)}
    combos: Optional[list[ComboReference]] = Field(alias="combocounts", default=None)


class RelatedInfoPageThemeColor(MightstoneModel):
    count: int
    icons: str
    name: str
    url: Path


class RelatedInfoPageTheme(MightstoneModel):
    colors: list[RelatedInfoPageThemeColor]
    name: str
    singular: str
    articles_tag: Optional[str] = Field(alias="articlestag", default=None)
    brief: Optional[str] = None
    breadcrumb: Optional[list[dict[str, str]]] = None


class PageTheme(Page):
    id: Optional[UUID] = None  # type: ignore
    related_info: Optional[RelatedInfoPageTheme] = Field(
        alias="relatedinfo", default=None
    )


class SerializablePageTheme(PageTheme, MightstoneSerializableDocument):
    id: Optional[UUID] = None  # type: ignore


class PageThemes(Page):
    id: Optional[UUID] = None  # type: ignore
    related_info: Optional[ThemeReferenceCollection] = Field(
        alias="relatedinfo", default=None
    )


class SerializablePageThemes(PageThemes, MightstoneSerializableDocument):
    id: Optional[UUID] = None  # type: ignore


class PageTypal(Page):
    id: Optional[UUID] = None  # type: ignore
    related_info: Optional[RelatedInfoPageTheme] = Field(
        alias="relatedinfo", default=None
    )


class SerializablePageTypal(PageTypal, MightstoneSerializableDocument):
    id: Optional[UUID] = None  # type: ignore


class PageTypals(Page):
    id: Optional[UUID] = None  # type: ignore
    related_info: Optional[ThemeReferenceCollection] = Field(
        alias="relatedinfo", default=None
    )


class SerializablePageTypals(PageTypals, MightstoneSerializableDocument):
    id: Optional[UUID] = None  # type: ignore


class PageCard(Page):
    id: Optional[UUID] = None  # type: ignore
    similar: Optional[list[CollectionItemCompleteCard]] = None
    panels: Panel


class SerializablePageCard(PageCard, MightstoneSerializableDocument):
    id: Optional[UUID] = None  # type: ignore


class PageSet(Page):
    id: Optional[UUID] = None  # type: ignore


class SerializablePageSet(PageCard, MightstoneSerializableDocument):
    id: Optional[UUID] = None  # type: ignore


class PageSets(Page):
    id: Optional[UUID] = None  # type: ignore


class SerializablePageSets(PageCard, MightstoneSerializableDocument):
    id: Optional[UUID] = None  # type: ignore


class PageSalts(Page):
    id: Optional[UUID] = None  # type: ignore


class SerializablePageSalts(PageCard, MightstoneSerializableDocument):
    id: Optional[UUID] = None  # type: ignore


class PageTopCards(Page):
    id: Optional[UUID] = None  # type: ignore


class SerializablePageTopCards(PageTopCards, MightstoneSerializableDocument):
    id: Optional[UUID] = None  # type: ignore


class PageCompanions(Page):
    id: Optional[UUID] = None  # type: ignore


class SerializablePageCompanions(PageCompanions, MightstoneSerializableDocument):
    id: Optional[UUID] = None  # type: ignore


class PagePartners(Page):
    id: Optional[UUID] = None  # type: ignore


class SerializablePagePartners(PagePartners, MightstoneSerializableDocument):
    id: Optional[UUID] = None  # type: ignore


class PagePartner(Page):
    id: Optional[UUID] = None  # type: ignore
    partners: list[CommanderPartner] = Field(alias="partnercounts")
    related_info: Optional[RelatedInfoPageTheme] = Field(
        alias="relatedinfo", default=None
    )


class SerializablePagePartner(PagePartner, MightstoneSerializableDocument):
    id: Optional[UUID] = None  # type: ignore


class CommandersRelatedInfo(MightstoneModel):
    singular: str
    plural: str
    colors: list
    tribes: list[CommanderIllustratedRelatedInfo]
    themes: list[CommanderIllustratedRelatedInfo]


class PageCommanders(Page):
    id: Optional[UUID] = None  # type: ignore
    related_info: Optional[CommandersRelatedInfo] = Field(
        alias="relatedinfo", default=None
    )


class SerializablePageCommanders(PageCommanders, MightstoneSerializableDocument):
    id: Optional[UUID] = None  # type: ignore


class PageCommander(Page, EdhRecCommanderDistribution, MightstoneModel):
    id: Optional[UUID] = None  # type: ignore
    panels: Panel
    similar: Optional[list[CollectionItemCompleteCard]] = None


class SerializablePageCommander(PageCommanders, MightstoneSerializableDocument):
    id: Optional[UUID] = None  # type: ignore


class PageStaples(Page):
    id: Optional[UUID] = None  # type: ignore
    related_info: Optional[list[CommandersRelatedInfo]] = None


class SerializablePageStaples(PageStaples, MightstoneSerializableDocument):
    id: Optional[UUID] = None  # type: ignore


class PageManaStaples(Page):
    id: Optional[UUID] = None  # type: ignore
    related_info: Optional[list[CommandersRelatedInfo]] = None


class SerializablePageManaStaples(PageManaStaples, MightstoneSerializableDocument):
    id: Optional[UUID] = None  # type: ignore


class DeckItem(EdhRecCommanderDistribution):
    urlhash: str
    savedate: datetime.date
    price: int
    tribe: Optional[str]
    theme: Optional[str]
    salt: float

    @property
    def url(self):
        return f"/deckpreview/{self.urlhash}"


class PageDecks(Page, EdhRecCommanderDistribution, MightstoneModel):
    panels: Panel
    items: list[DeckItem] = Field(alias="table", default=[])  # type: ignore
    deck: list[str]
    similar: Optional[list[CollectionItemCompleteCard]] = None


class SerializablePageDecks(PageDecks, MightstoneSerializableDocument):
    id: Optional[UUID] = None  # type: ignore


class PageAverageDeck(Page, EdhRecCommanderDistribution, MightstoneModel):
    id: Optional[UUID] = None  # type: ignore
    panels: Panel
    deck: list[str]


class SerializablePageAverageDeck(PageAverageDeck, MightstoneSerializableDocument):
    id: Optional[UUID] = None  # type: ignore


class PageDeck(Page, EdhRecCommanderDistribution, MightstoneModel):
    panels: Panel
    items: list[str] = Field(alias="cards", default=[])  # type: ignore
    cedh: bool
    color_identity: list[str] = Field(alias="coloridentity")
    commanders: list[Union[str, None]]
    created_at: datetime.date = Field(alias="deckage")
    scraped_at: datetime.date = Field(alias="savedate")
    edhrec_tags: list[str] = Field(alias="edhrectags")
    tags: list[str]
    price: float
    salt: float
    theme: Optional[str]
    tribe: Optional[str]
    url: Url
    url_hash: str = Field(alias="urlhash")
    similar: list[Any] = Field(alias="similardecks")
    description: str


class SerializablePageDeck(PageDeck, MightstoneSerializableDocument):
    id: Optional[UUID] = None  # type: ignore


class PageCombos(Page):
    id: Optional[UUID] = None  # type: ignore
    related_info: Optional[list[ColorReferenceCollection]] = None


class SerializablePageCombos(PageCombos, MightstoneSerializableDocument):
    id: Optional[UUID] = None  # type: ignore


class ComboDescription(MightstoneModel):
    combo_id: str
    process_txt: list[str]
    require_txt: str
    results_txt: str


class PageCombo(Page):
    combo: ComboDescription


class SerializablePageCombo(PageCombo, MightstoneSerializableDocument):
    id: Optional[UUID] = None  # type: ignore


class PageBackgrounds(Page):
    id: Optional[UUID] = None  # type: ignore


class SerializablePageBackgrounds(PageBackgrounds, MightstoneSerializableDocument):
    id: Optional[UUID] = None  # type: ignore


class PageBackground(Page):
    partners: list[CommanderPartner] = Field(alias="partnercounts")


class SerializablePageBackground(PageBackground, MightstoneSerializableDocument):
    id: Optional[UUID] = None  # type: ignore


class FilterComparator(MightstoneModel):
    value: int = 0
    operator: FilterOperator = FilterOperator.EQUAL

    def __str__(self):
        return f"{self.operator.value}={self.value}"


class FilterQuery(MightstoneModel):
    card_in: List[str] = []
    card_out: List[str] = []
    count: Dict[FilterType, FilterComparator] = {}

    def __str__(self):
        filters = []
        filters.extend([f"Out={card}" for card in self.card_out])
        filters.extend([f"In={card}" for card in self.card_in])
        filters.extend(
            [f"{field.value}:{comparator}" for field, comparator in self.count.items()]
        )
        return ";".join(filters)


class Recommendation(MightstoneModel):
    name: str
    names: list[str]
    primary_type: str
    salt: float
    score: Optional[int] = None


class Recommendations(MightstoneModel):
    commanders: List[Recommendation] = []
    deck: dict[str, int] = {}
    in_recs: List[Recommendation] = Field(alias="inRecs", default=[])
    out_recs: List[Recommendation] = Field(alias="outRecs", default=[])
    more: bool = False


def slugify(string: Optional[str]):
    import slugify

    if string is None:
        return None
    return slugify.slugify(
        string, separator="-", replacements=[("'", ""), ("+", "plus-")]
    )

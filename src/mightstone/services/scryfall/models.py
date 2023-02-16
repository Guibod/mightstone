import datetime
from decimal import Decimal
from enum import Enum
from typing import Dict, List, Optional
from uuid import UUID, uuid4

from pydantic import AnyUrl, Field
from typing_extensions import TypedDict

from mightstone.core import MightstoneModel


class Color(str):
    WHITE = "W"
    BLUE = "U"
    BLACK = "B"
    RED = "R"
    GREEN = "G"
    COLORLESS = "C"

    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def __modify_schema__(cls, field_schema):
        # __modify_schema__ should mutate the dict it receives in place,
        # the returned value will be ignored
        field_schema.update(
            # simplified regex here for brevity, see the wikipedia link above
            pattern="^[WUBRG]$",
            # some example postcodes
            examples=["U", "W"],
        )

    @classmethod
    def validate(cls, v):
        if not isinstance(v, str):
            raise TypeError("string required")
        if v not in [cls.WHITE, cls.BLUE, cls.BLACK, cls.RED, cls.GREEN, cls.COLORLESS]:
            raise TypeError("string is not a legal color code")

        return v

    def __repr__(self):
        return f"Color({super().__repr__()})"


class ScryfallList(MightstoneModel):
    data: List
    """An array of the requested objects, in a specific order."""
    has_more: bool = False
    """if this List is paginated and there is a page beyond the current page."""
    next_page: AnyUrl = None
    """If there is a page beyond the current page, this field will contain a full API
    URI to that page. You may submit a HTTP GET request to that URI to continue
    paginating forward on this List."""
    total_cards: int = None
    """If this is a list of Card objects, this field will contain the total number
    of cards found across all pages."""
    warnings: List[str] = []
    """An array of human-readable warnings issued when generating this list, as
    strings. Warnings are non-fatal issues that the API discovered with your input.
    In general, they indicate that the List will not contain the all of the information
    you requested. You should fix the warnings and re-submit your request."""


class Error(MightstoneModel):
    status: int
    """An integer HTTP status code for this error."""
    code: str
    """A computer-friendly string representing the appropriate HTTP status code."""
    details: str
    """A human-readable string explaining the error."""
    type: str = None
    """A computer-friendly string that provides additional context for the main error.
    For example, an endpoint many generate HTTP 404 errors for different kinds of
    input. This field will provide a label for the specific kind of 404 failure,
    such as ambiguous."""
    warnings: List[str] = []
    """If your input also generated non-failure warnings, they will be provided as
     human-readable strings in this array."""


class RelatedObject(TypedDict, total=False):
    id: UUID
    object: str
    """A content type for this object, always related_card."""
    component: str
    """A field explaining what role this card plays in this relationship, one of:
     token, meld_part, meld_result, or combo_piece."""
    name: str
    """The name of this particular related card."""
    type_line: str
    """The type line of this card."""
    uri: AnyUrl
    """A URI where you can retrieve a full object describing this card on Scryfall’s
    API. """


class CardImagery(TypedDict, total=False):
    png: Optional[AnyUrl]
    """A transparent, rounded full card PNG. This is the best image to use for videos
    or other high-quality content. """
    border_crop: Optional[AnyUrl]
    """A full card image with the rounded corners and the majority of the border
    cropped off. Designed for dated contexts where rounded images can’t be used. """
    art_crop: Optional[AnyUrl]
    """A rectangular crop of the card’s art only. Not guaranteed to be perfect for cards
    with outlier designs or strange frame arrangements"""
    large: Optional[AnyUrl]
    """A large full card image"""
    normal: Optional[AnyUrl]
    """A medium-sized full card image"""
    small: Optional[AnyUrl]
    """A small full card image. Designed for use as thumbnail or list icon."""


class CardFace(TypedDict, total=False):
    artist: Optional[str]
    """The name of the illustrator of this card face. Newly spoiled cards may not
    have this field yet. """
    cmc: Optional[Decimal]
    """The mana value of this particular face, if the card is reversible."""
    color_indicator: Optional[List[Color]]
    """The colors in this face’s color indicator, if any."""
    colors: Optional[List[Color]]
    """This face’s colors, if the game defines colors for the individual face of this
    card. """
    flavor_text: Optional[str]
    """The flavor text printed on this face, if any."""
    illustration_id: Optional[UUID]
    """A unique identifier for the card face artwork that remains consistent across
    reprints. Newly spoiled cards may not have this field yet. """
    image_uris: Optional[CardImagery]
    """An object providing URIs to imagery for this face, if this is a double-sided
    card. If this card is not double-sided, then the image_uris property will be part
    of the parent object instead. """
    layout: Optional[str]
    """The layout of this card face, if the card is reversible."""
    loyalty: Optional[str]
    """This face’s loyalty, if any."""
    mana_cost: str
    """The mana cost for this face. This value will be any empty string
    if the cost is absent. Remember that per the game rules, a missing mana cost and
    a mana cost of {0} are different values."""
    name: str
    object: str
    """A content type for this object, always card_face."""
    oracle_id: Optional[UUID]
    """The Oracle ID of this particular face, if the card is reversible."""
    oracle_text: Optional[str]
    """The Oracle text for this face, if any."""
    power: Optional[str]
    """This face’s power, if any. Note that some cards have powers that are not
    numeric, such as *."""
    printed_name: Optional[str]
    """The localized name printed on this face, if any."""
    printed_text: Optional[str]
    """The localized text printed on this face, if any."""
    printed_type_line: Optional[str]
    """The localized type line printed on this face, if any."""
    toughness: Optional[str]
    """This face’s toughness, if any."""
    type_line: Optional[str]
    """The type line of this particular face, if the card is reversible."""
    watermark: Optional[str]
    """The watermark on this particulary card face, if any."""


class Preview(TypedDict, total=False):
    previewed_at: Optional[datetime.date]
    """The date this card was previewed"""
    source_uri: Optional[str]
    """A link to the preview for this card."""
    source: Optional[str]
    """The name of the source that previewed this card."""


class BulkTagType(Enum):
    ORACLE = "oracle"
    ILLUSTRATION = "illustration"


class Tag(MightstoneModel):
    object: str
    id: UUID = Field(default_factory=uuid4)
    label: str
    type: str
    description: Optional[str]
    oracle_ids: List[UUID]

    class Settings:
        name = "tags"


class Card(MightstoneModel):
    arena_id: Optional[int] = None
    """This card’s Arena ID, if any. A large percentage of cards are not available on
    Arena and do not have this ID. """

    id: UUID = Field(default_factory=uuid4)
    """A unique ID for this card in Scryfall’s database."""
    lang: str
    """A language code for this printing."""
    mtgo_id: Optional[int]
    """This card’s Magic Online ID (also known as the Catalog ID), if any. A large
    percentage of cards are not available on Magic Online and do not have this ID."""
    mtgo_foil_id: Optional[int]
    """This card’s foil Magic Online ID (also known as the Catalog ID), if any. A
    large percentage of cards are not available on Magic Online and do not have this
    ID."""
    multiverse_ids: Optional[List[int]]
    """This card’s multiverse IDs on Gatherer, if any, as an array of integers.
    Note that Scryfall includes many promo cards, tokens, and other esoteric objects
    that do not have these identifiers."""
    tcgplayer_id: Optional[int]
    """This card’s ID on TCGplayer’s API, also known as the productId."""
    tcgplayer_etched_id: Optional[int]
    """This card’s ID on TCGplayer’s API, for its etched version if that version is a
     separate product."""
    cardmarket_id: Optional[int]
    """This card’s ID on Cardmarket’s API, also known as the idProduct."""
    object: str
    """A content type for this object, always card."""
    oracle_id: UUID
    """A unique ID for this card’s oracle identity.
    This value is consistent across reprinted card editions, and unique among
    different cards with the same name (tokens, Unstable variants, etc)."""
    prints_search_uri: str
    """A link to where you can begin paginating all re/prints for this card
    on Scryfall’s API."""
    rulings_uri: AnyUrl
    """A link to this card’s rulings list on Scryfall’s API."""
    scryfall_uri: AnyUrl
    """A link to this card’s permapage on Scryfall’s website."""
    uri: AnyUrl
    """A link to this card object on Scryfall’s API."""

    all_parts: Optional[List[dict]]
    """If this card is closely related to other cards, this property will be an array
    with Related Card Objects. """
    card_faces: Optional[List[dict]]
    """An array of Card Face objects, if this card is multifaced."""
    cmc: Decimal
    """The card’s converted mana cost. Note that some funny cards have fractional
    mana costs. """
    color_identity: List[Color]
    """This card’s color identity."""
    color_indicator: Optional[List[Color]]
    """The colors in this card’s color indicator, if any.
    A null value for this field indicates the card does not have one."""
    colors: Optional[List[Color]]
    """This card’s colors, if the overall card has colors defined by the rules.
    Otherwise the colors will be on the card_faces objects, see below."""
    edhrec_rank: Optional[int]
    """This card’s overall rank/popularity on EDHREC. Not all cards are ranked."""
    hand_modifier: Optional[str]
    """This card’s hand modifier, if it is Vanguard card. This value will contain a
    delta, such as -1. """
    keywords: List[str]
    """An array of keywords that this card uses, such as 'Flying' and 'Cumulative
    upkeep'. """
    layout: str
    """A code for this card’s layout."""
    legalities: dict
    """An object describing the legality of this card across play formats.
    Possible legalities are legal, not_legal, restricted, and banned."""
    life_modifier: Optional[str]
    """This card’s life modifier, if it is Vanguard card. This value will contain a
    delta, such as +2. """
    loyalty: Optional[str]
    """This loyalty if any. Note that some cards have loyalties that are not numeric,
    such as X. """
    mana_cost: Optional[str]
    """The mana cost for this card. This value will be any empty string "" if the
    cost is absent. Remember that per the game rules, a missing mana cost and a mana
    cost of {0} are different values. Multi-faced cards will report this value in
    card faces. """
    name: str
    """The name of this card. If this card has multiple faces, this field will
    contain both names separated by ␣//␣. """
    oracle_text: Optional[str]
    """The Oracle text for this card, if any."""
    oversized: bool
    """True if this card is oversized."""
    penny_rank: Optional[int]
    """This card’s rank/popularity on Penny Dreadful. Not all cards are ranked."""
    power: Optional[str]
    """This card’s power, if any. Note that some cards have powers that are not
    numeric, such as *. """
    produced_mana: Optional[List[str]]
    """Colors of mana that this card could produce."""
    reserved: bool
    """True if this card is on the Reserved List."""
    toughness: Optional[str]
    """This card’s toughness, if any. Note that some cards have toughnesses that are
    not numeric, such as *. """
    type_line: str
    """The type line of this card."""

    artist: Optional[str]
    """The name of the illustrator of this card. Newly spoiled cards may not have
    this field yet. """
    attraction_lights: Optional[List[str]]
    """The lit Unfinity attractions lights on this card, if any."""
    booster: bool
    """Whether this card is found in boosters."""
    border_color: str
    """This card’s border color: black, white, borderless, silver, or gold."""
    card_back_id: Optional[UUID]
    """The Scryfall ID for the card back design present on this card."""
    collector_number: str
    """This card’s collector number. Note that collector numbers can contain
    non-numeric characters, such as letters or ★. """
    content_warning: Optional[bool]
    """True if you should consider avoiding use of this print downstream."""
    digital: bool
    """	True if this card was only released in a video game."""
    finishes: List[str]
    """An array of computer-readable flags that indicate if this card can come in
    foil, nonfoil, or etched finishes. """
    flavor_name: Optional[str]
    """The just-for-fun name printed on the card (such as for Godzilla series cards)."""
    flavor_text: Optional[str]
    """The flavor text, if any."""
    frame_effects: Optional[List[str]]
    """This card’s frame effects, if any."""
    frame: str
    """This card’s frame layout."""
    full_art: bool
    """True if this card’s artwork is larger than normal."""
    games: List[str]
    """A list of games that this card print is available in, paper, arena,
    and/or mtgo. """
    highres_image: bool
    """True if this card’s imagery is high resolution."""
    illustration_id: Optional[UUID]
    """A unique identifier for the card artwork that remains consistent across reprints.
    Newly spoiled cards may not have this field yet."""
    image_status: str
    """A computer-readable indicator for the state of this card’s image, one of :
    missing, placeholder, lowres, or highres_scan."""
    image_uris: Optional[CardImagery]
    """An object listing available imagery for this card. See the Card Imagery
    article for more information. """
    prices: Dict[str, Optional[str]]
    """An object containing daily price information for this card, including:
     usd, usd_foil, usd_etched, eur, and tix prices, as strings."""
    printed_name: Optional[str]
    """The localized name printed on this card, if any."""
    printed_text: Optional[str]
    """The localized text printed on this card, if any."""
    printed_type_line: Optional[str]
    """The localized type line printed on this card, if any."""
    promo: bool
    """True if this card is a promotional print."""
    promo_types: Optional[List[str]]
    """An array of strings describing what categories of promo cards this card falls
    into. """
    purchase_uris: Optional[Dict[str, str]]
    """An object providing URIs to this card’s listing on major marketplaces."""
    rarity: str
    """This card’s rarity. One of common, uncommon, rare, special, mythic, or bonus."""
    related_uris: Dict[str, AnyUrl]
    """An object providing URIs to this card’s listing on other Magic: The Gathering
    online resources. """
    released_at: datetime.date
    """The date this card was first released."""
    reprint: bool
    """True if this card is a reprint."""
    scryfall_set_uri: AnyUrl
    """A link to this card’s set on Scryfall’s website."""
    set_name: str
    """This card’s full set name."""
    set_search_uri: AnyUrl
    """A link to where you can begin paginating this card’s set on the Scryfall API."""
    set_type: str
    """The type of set this printing is in."""
    set_uri: AnyUrl
    """A link to this card’s set object on Scryfall’s API."""
    set_code: str = Field(alias="set")
    """This card’s set code."""
    set_id: UUID
    """This card’s Set object UUID."""
    story_spotlight: bool
    """True if this card is a Story Spotlight."""
    textless: bool
    """True if the card is printed without text."""
    variation: bool
    """Whether this card is a variation of another printing."""
    variation_of: Optional[UUID]
    """The printing ID of the printing this card is a variation of."""
    security_stamp: Optional[str]
    """The security stamp on this card, if any. One of oval, triangle, acorn, circle,
    arena, or heart. """
    watermark: Optional[str]
    """This card’s watermark, if any."""
    preview: Optional[Preview]

    class Settings:
        name = "cards"
        bson_encoders = {
            datetime.date: lambda dt: datetime.datetime(
                year=dt.year, month=dt.month, day=dt.day, hour=0, minute=0, second=0
            )
        }


class SetType(Enum):
    CORE = "core"
    """A yearly Magic core set (Tenth Edition, etc)"""
    EXPANSION = "expansion"
    """A rotational expansion set in a block (Zendikar, etc)"""
    MASTERS = "masters"
    """A reprint set that contains no new cards (Modern Masters, etc)"""
    ALCHEMY = "alchemy"
    """An Arena set designed for Alchemy"""
    MASTERPIECE = "masterpiece"
    """Masterpiece Series premium foil cards"""
    ARSENAL = "arsenal"
    """A Commander-oriented gift set"""
    VAULT = "from_the_vault"
    """From the Vault gift sets"""
    SPELLBOOK = "spellbook"
    """Spellbook series gift sets"""
    PREMIUM = "premium_deck"
    """Premium Deck Series decks"""
    DUEL = "duel_deck"
    """Duel Decks"""
    DRAFT_INNOVATION = "draft_innovation"
    """Special draft sets, like Conspiracy and Battlebond"""
    TREASURE_CHEST = "treasure_chest"
    """Magic Online treasure chest prize sets"""
    COMMANDER = "commander"
    """Commander preconstructed decks"""
    PLANECHASE = "planechase"
    """Planechase sets"""
    ARCHENEMY = "archenemy"
    """Archenemy sets"""
    VANGUARD = "vanguard"
    """Vanguard card sets"""
    FUNNY = "funny"
    """A funny un-set or set with funny promos (Unglued, Happy Holidays, etc)"""
    STARTER = "starter"
    """A starter/introductory set (Portal, etc)"""
    BOX = "box"
    """A gift box set"""
    PROMO = "promo"
    """A set that contains purely promotional cards"""
    TOKEN = "token"  # nosec, damnit bandit, that’s not a security issue
    """A set made up of tokens and emblems."""
    MEMO = "memorabilia"
    """A set made up of gold-bordered, oversize, or trophy cards that are not legal"""


class Set(MightstoneModel):
    """
    A Set object represents a group of related Magic cards. All Card objects on Scryfall
     belong to exactly one set.

    Due to Magic’s long and complicated history, Scryfall includes many un-official sets
     as a way to group promotional or outlier cards together. Such sets will likely have
      a code that begins with p or t, such as pcel or tori.

    Official sets always have a three-letter set code, such as zen.
    """

    id: UUID
    """A unique ID for this set on Scryfall that will not change."""
    code: str
    "The unique three to five-letter code for this set."
    mtgo_code: str = None
    """The unique code for this set on MTGO, which may differ from the regular code."""
    tcgplayer_id: int = None
    """This set’s ID on TCGplayer’s API, also known as the groupId."""
    name: str
    """The English name of the set."""
    set_type: SetType
    """A computer-readable classification for this set. See below."""
    released_at: datetime.date = None
    """The date the set was released or the first card was printed in the set (in
    GMT-8 Pacific time). """
    block_code: str = None
    """The block code for this set, if any."""
    block: str = None
    """The block or group name code for this set, if any."""
    parent_set_code: str = None
    """The set code for the parent set, if any. promo and token sets often have a
    parent set. """
    card_count: int
    """The number of cards in this set."""
    printed_size: int = None
    """The denominator for the set’s printed collector numbers."""
    digital: bool
    """True if this set was only released in a video game."""
    foil_only: bool
    """True if this set contains only foil cards."""
    nonfoil_only: bool
    """True if this set contains only nonfoil cards."""
    scryfall_uri: AnyUrl
    """A link to this set’s permapage on Scryfall’s website."""
    uri: AnyUrl
    """A link to this set object on Scryfall’s API."""
    icon_svg_uri: AnyUrl
    """A URI to an SVG file for this set’s icon on Scryfall’s CDN.
    Hotlinking this image isn’t recommended, because it may change slightly over time.
    You should download it and use it locally for your particular user interface
    needs."""
    search_uri: AnyUrl
    """A Scryfall API URI that you can request to begin paginating over the cards
    in this set."""


class Symbol(MightstoneModel):
    """
    A Card Symbol object represents an illustrated symbol that may appear in card’s
    mana cost or Oracle text. Symbols are based on the notation used in the
    Comprehensive Rules.
    For more information about how the Scryfall API represents mana and costs, see the
    colors and costs overview.
    """

    symbol: str
    """The plaintext symbol. Often surrounded with curly braces {}. Note that not all
     symbols are ASCII text (for example, {∞})."""
    loose_variant: str = None
    """An alternate version of this symbol, if it is possible to write it without
    curly braces."""
    english: str
    """An English snippet that describes this symbol. Appropriate for use in alt text
    or other accessible communication formats."""
    transposable: bool
    """True if it is possible to write this symbol “backwards”.
    For example, the official symbol {U/P} is sometimes written as {P/U} or {P\\U} in
    informal settings.
    Note that the Scryfall API never writes symbols backwards in other responses. This
    field is provided for informational purposes."""
    represents_mana: bool
    """True if this is a mana symbol."""
    cmc: Decimal = None
    """A decimal number representing this symbol’s converted mana cost. Note that mana
    symbols from funny sets can have fractional converted mana costs."""
    appears_in_mana_costs: bool
    """True if this symbol appears in a mana cost on any Magic card. For example {20}
    has this field set to false because {20} only appears in Oracle text, not mana
    costs."""
    funny: bool
    """True if this symbol is only used on funny cards or Un-cards."""
    colors: List[Color] = []
    """An array of colors that this symbol represents."""
    gatherer_alternates: List[str] = None
    """An array of plaintext versions of this symbol that Gatherer uses on old cards
    to describe original printed text. For example: {W} has ["oW", "ooW"] as
    alternates."""
    svg_uri: AnyUrl = None
    """A URI to an SVG image of this symbol on Scryfall’s CDNs."""


class ManaCost(MightstoneModel):
    cost: str
    """The normalized cost, with correctly-ordered and wrapped mana symbols."""
    cmc: Decimal
    """The converted mana cost. If you submit Un-set mana symbols, this decimal
     could include fractional parts."""
    colors: List[Color]
    """The colors of the given cost."""
    colorless: bool
    """True if the cost is colorless."""
    monocolored: bool
    """True if the cost is monocolored."""
    multicolored: bool
    """True if the cost is multicolored."""


class Migration(MightstoneModel):
    uri: AnyUrl
    """A link to the current object on Scryfall’s API."""
    id: UUID
    """This migration’s unique UUID."""
    created_at: datetime.date = None
    """The date this migration was performed."""
    migration_strategy: str
    """A computer-readable indicator of the migration strategy."""
    old_scryfall_id: UUID
    """The id of the affected API Card object."""
    new_scryfall_id: UUID = None
    """The replacement id of the API Card object if this is a merge."""
    note: str = None
    """A note left by the Scryfall team about this migration."""


class UniqueStrategy(Enum):
    CARDS = "cards"
    """
    Removes duplicate gameplay objects (cards that share a name and have the same
    functionality). For example, if your search matches more than one print of Pacifism,
     only one copy of Pacifism will be returned.
    """
    ART = "art"
    """
    Returns only one copy of each unique artwork for matching cards. For example, if
    your search matches more than one print of Pacifism, one card with each different
    illustration for Pacifism will be returned, but any cards that duplicate artwork
    already in the results will be omitted.
    """
    PRINTS = "prints"
    """
    Returns all prints for all cards matched (disables rollup). For example,
    if your search matches more than one print of Pacifism, all matching prints will
    be returned.
    """


class SortStrategy(Enum):
    NAME = "name"
    """Sort cards by name, A → Z"""
    SET = "set"
    """Sort cards by their set and collector number: AAA/#1 → ZZZ/#999"""
    RELEASED = "released"
    """Sort cards by their release date: Newest → Oldest"""
    RARITY = "rarity"
    """Sort cards by their rarity: Common → Mythic"""
    COLOR = "color"
    """Sort cards by their color and color identity: WUBRG → multicolor → colorless"""
    USD = "usd"
    """Sort cards by their lowest known U.S. Dollar price: 0.01 → highest, null last"""
    TIX = "tix"
    """Sort cards by their lowest known TIX price: 0.01 → highest, null last"""
    EUR = "eur"
    """Sort cards by their lowest known Euro price: 0.01 → highest, null last"""
    CMC = "cmc"
    """Sort cards by their converted mana cost: 0 → highest"""
    POWER = "power"
    """Sort cards by their power: null → highest"""
    TOUGHNESS = "toughness"
    """Sort cards by their toughness: null → highest"""
    EDHREC = "edhrec"
    """Sort cards by their EDHREC ranking: lowest → highest"""
    PENNY = "penny"
    """Sort cards by their Penny Dreadful ranking: lowest → highest"""
    ARTIST = "artist"
    """Sort cards by their front-side artist name: A → Z"""
    REVIEW = "review"
    """Sort cards how podcasts review sets, usually color & CMC, lowest → highest,
    with Booster Fun cards at the end """


class DirectionStrategy(Enum):
    AUTO = "auto"
    """Scryfall will automatically choose the most inuitive direction to sort"""
    ASC = "asc"
    """Sort ascending (the direction of the arrows in the previous table)"""
    DESC = "desc"
    """Sort descending (flip the direction of the arrows in the previous table)"""


class CardIdentifierPath(Enum):
    SCRYFALL = None
    CODE_NUMBER = "code-number"
    CARDMARKET = "cardmarket"
    TCG_PLAYER = "tcgplayer"
    MTGO = "mtgo"
    ARENA = "arena"
    MULTIVERSE = "multiverse"


class RulingIdentifierPath(Enum):
    SCRYFALL = None
    CODE_NUMBER = "code-number"
    MTGO = "mtgo"
    ARENA = "arena"
    MULTIVERSE = "multiverse"


class CatalogType(Enum):
    CARDS = "card-names"
    """Returns a list of all nontoken English card names in Scryfall’s database.
    Values are updated as soon as a new card is entered for spoiler seasons. """
    ARTISTS = "artist-names"
    """Returns a list of all canonical artist names in Scryfall’s database. This
    catalog won’t include duplicate, misspelled, or funny names for artists. Values
    are updated as soon as a new card is entered for spoiler seasons. """
    WORDS = "word-bank"
    """Returns a Catalog of all English words, of length 2 or more, that could appear
    in a card name. Values are drawn from cards currently in Scryfall’s database.
    Values are updated as soon as a new card is entered for spoiler seasons. """
    CREATURE_TYPES = "creature-types"
    """Returns a Catalog of all creature types in Scryfall’s database. Values are
    updated as soon as a new card is entered for spoiler seasons. """
    PLANESWALKER_TYPES = "planeswalker-types"
    """Returns a Catalog of all Planeswalker types in Scryfall’s database. Values are
    updated as soon as a new card is entered for spoiler seasons. """
    LAND_TYPES = "land-types"
    """Returns a Catalog of all Land types in Scryfall’s database. Values are updated
    as soon as a new card is entered for spoiler seasons. """
    ARTIFACT_TYPES = "artifact-types"
    """Returns a Catalog of all artifact types in Scryfall’s database. Values are
    updated as soon as a new card is entered for spoiler seasons. """
    ENCHANTMENT_TYPES = "enchantment-types"
    """Returns a Catalog of all enchantment types in Scryfall’s database. Values are
    updated as soon as a new card is entered for spoiler seasons. """
    SPELL_TYPES = "spell-types"
    """Returns a Catalog of all spell types in Scryfall’s database. Values are
    updated as soon as a new card is entered for spoiler seasons. """
    POWERS = "powers"
    """Returns a Catalog of all possible values for a creature or vehicle’s power in
    Scryfall’s database. Values are updated as soon as a new card is entered for
    spoiler seasons. """
    TOUGHNESSES = "toughnesses"
    """Returns a Catalog of all possible values for a creature or vehicle’s toughness
    in Scryfall’s database. Values are updated as soon as a new card is entered for
    spoiler seasons. """
    LOYALTIES = "loyalties"
    """Returns a Catalog of all possible values for a Planeswalker’s loyalty in
    Scryfall’s database. Values are updated as soon as a new card is entered for
    spoiler seasons. """
    WATERMARKS = "watermarks"
    """Returns a Catalog of all card watermarks in Scryfall’s database. Values are
    updated as soon as a new card is entered for spoiler seasons. """
    KEYWORD_ABILITIES = "keyword-abilities"
    """Returns a Catalog of all keyword abilities in Scryfall’s database. Values are
    updated as soon as a new card is entered for spoiler seasons. """
    KEYWORD_ACTIONS = "keyword-actions"
    """Returns a Catalog of all keyword actions in Scryfall’s database. Values are
    updated as soon as a new card is entered for spoiler seasons. """
    ABILITY_WORDS = "ability-words"
    """Returns a Catalog of all ability words in Scryfall’s database. Values are
    updated as soon as a new card is entered for spoiler seasons. """


class Catalog(MightstoneModel):
    uri: AnyUrl = None
    """A link to the current catalog on Scryfall’s API."""
    total_values: int
    """The number of items in the data array."""
    data: List[str]
    """An array of datapoints, as strings."""


class IdentifierId(TypedDict):
    """Finds a card with the specified Scryfall id."""

    id: UUID


class IdentifierMtgId(TypedDict):
    """Finds a card with the specified mtgo_id or mtgo_foil_id."""

    mtgo_id: int


class IdentifierMultiverseId(TypedDict):
    """Finds a card with the specified value among its multiverse_ids."""

    multiverse_id: int


class IdentifierOracleId(TypedDict):
    """Finds the newest edition of cards with the specified oracle_id."""

    oracle_id: UUID


class IdentifierIllustrationId(TypedDict):
    """Finds the preferred scans of cards with the specified illustration_id."""

    illustration_id: UUID


class IdentifierName(TypedDict):
    """Finds the newest edition of a card with the specified name."""

    name: str


class IdentifierNameSet(TypedDict):
    name: str
    set: str


class IdentifierCollectorNumberSet(TypedDict):
    """Finds a card matching the specified name and set."""

    collector_number: int
    set: str


class Ruling(MightstoneModel):
    """
    Rulings represent Oracle rulings, Wizards of the Coast set release notes,
    or Scryfall notes for a particular card.

    If two cards have the same name, they will have the same set of rulings objects.
    If a card has rulings, it usually has more than one.

    Rulings with a scryfall source have been added by the Scryfall team, either to
    provide additional context for the card, or explain how the card works in an
    unofficial format (such as Duel Commander).
    """

    oracle_id: UUID
    """
    Oracle unique identifier
    """
    source: str
    """A computer-readable string indicating which company produced this ruling,
    either wotc or scryfall. """
    published_at: datetime.date
    """The date when the ruling or note was published."""
    comment: str
    """The text of the ruling."""

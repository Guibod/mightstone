"""
MTGJSON models
"""

import datetime
import sys

if sys.version_info < (3, 11):
    from typing import Dict, List, Optional, Union

    from typing_extensions import NotRequired, TypedDict
else:
    from typing import List, Optional, Union, TypedDict, Dict, NotRequired

from pydantic import Field
from pydantic.types import UUID

from mightstone.core import MightstoneModel


class Types(MightstoneModel):
    """
    The Types Data Model describes all types available on a Card.
    """

    sub_types: List[str] = Field(since="v4.0.0", alias="subTypes")
    """A list of all available subtypes of a type.
    Examples: "Abian", "Adventure", "Advisor", "Aetherborn", "Ajani" """
    super_types: List[str] = Field(since="v4.0.0", alias="superTypes")
    """A list of all available supertypes of a type.
    Examples: "Basic", "Host", "Legendary", "Ongoing", "Snow" """


class CardTypes(MightstoneModel):
    """
    The Card Types Data Model describes card types that a card may have.
    """

    artifact: Types = Field(since="v4.0.0", alias="artifact")
    """All possible subtypes and supertypes for Artifact cards."""

    conspiracy: Types = Field(since="v4.0.0", alias="conspiracy")
    """All possible subtypes and supertypes for Conspiracy cards."""

    creature: Types = Field(since="v4.0.0", alias="creature")
    """All possible subtypes and supertypes for Creature cards."""

    enchantment: Types = Field(since="v4.0.0", alias="enchantment")
    """All possible subtypes and supertypes for Enchantment cards."""

    instant: Types = Field(since="v4.0.0", alias="instant")
    """All possible subtypes and supertypes for Instant cards."""

    land: Types = Field(since="v4.0.0", alias="land")
    """All possible subtypes and supertypes for Land cards."""

    phenomenon: Types = Field(since="v4.0.0", alias="phenomenon")
    """All possible subtypes and supertypes for Phenomenon cards."""

    plane: Types = Field(since="v4.0.0", alias="plane")
    """All possible subtypes and supertypes for Plane cards."""

    planeswalker: Types = Field(since="v4.0.0", alias="planeswalker")
    """All possible subtypes and supertypes for Planeswalker."""

    scheme: Types = Field(since="v4.0.0", alias="scheme")
    """All possible subtypes and supertypes for Scheme cards."""

    sorcery: Types = Field(since="v4.0.0", alias="sorcery")
    """All possible subtypes and supertypes for Sorcery cards."""

    tribal: Types = Field(since="v4.0.0", alias="tribal")
    """All possible subtypes and supertypes for Tribal cards."""

    vanguard: Types = Field(since="v4.0.0", alias="vanguard")
    """All possible subtypes and supertypes for Vanguard cards."""


class DeckList(MightstoneModel):
    """
    The Deck List Data Model describes a metadata-like model for a Deck.
    """

    code: str = Field(since="v4.3.0", alias="code")
    """The set code for the deck."""

    file_name: str = Field(since="v4.3.0", alias="fileName")
    """The file name for the deck. Combines the name and code fields to avoid 
    namespace collisions and are given a delimiter of _. Examples: 
    "SpiritSquadron_VOC" """

    name: str = Field(since="v4.3.0", alias="name")
    """The name of the deck."""

    release_date: Optional[datetime.date] = Field(since="v4.3.0", alias="releaseDate")
    """The release date in ISO 8601 format for the set. Returns 
    null if the set was not formally released as a product. """

    type: str = Field(since="v4.3.0", alias="type")
    """The type of deck. Examples: "Advanced Deck", "Advanced Pack", "Archenemy 
    Deck", "Basic Deck", "Brawl Deck" """


class ForeignData(MightstoneModel):
    """
    The Foreign Data Data Model describes a list of properties for various Card Data
    Models in alternate languages.
    """

    face_name: Optional[str] = Field(since="v5.0.1", alias="faceName")
    """The foreign name on the face of the card."""

    flavor_text: Optional[str] = Field(since="v4.0.0", alias="flavorText")
    """The foreign flavor text of the card."""

    language: str = Field(since="v4.0.0", alias="language")
    """The foreign language of card. Examples: "Ancient Greek", "Arabic", "Chinese 
    Simplified", "Chinese Traditional", "French" """

    multiverse_id: Optional[int] = Field(since="v4.0.0", alias="multiverseId")
    """The foreign multiverse identifier of the card."""

    name: str = Field(since="v4.0.0", alias="name")
    """The foreign name of the card."""

    text: Optional[str] = Field(since="v4.0.0", alias="text")
    """The foreign text ruling of the card."""

    type: Optional[str] = Field(since="v4.0.0", alias="type")
    """The foreign type of the card. Includes any supertypes and subtypes."""


class Identifiers(MightstoneModel):
    card_kingdom_etched_id: Optional[str] = Field(
        since="v5.2.0", alias="cardKingdomEtchedId"
    )
    """The Card Kingdom etched card identifier."""

    card_kingdom_foil_id: Optional[str] = Field(
        since="v5.0.0", alias="cardKingdomFoilId"
    )
    """The Card Kingdom foil card identifier."""

    card_kingdom_id: Optional[str] = Field(since="v5.0.0", alias="cardKingdomId")
    """The Card Kingdom card identifier."""

    cardsphere_id: Optional[str] = Field(since="v5.2.1", alias="cardsphereId")
    """The Cardsphere card identifier."""

    mcm_id: Optional[str] = Field(since="v4.4.0", alias="mcmId")
    """The Card Market card identifier."""

    mcm_meta_id: Optional[str] = Field(since="v4.4.0", alias="mcmMetaId")
    """The Card Market card meta identifier."""

    mtg_arena_id: Optional[str] = Field(since="v4.5.0", alias="mtgArenaId")
    """The Magic: The Gathering Arena card identifier."""

    mtgo_foil_id: Optional[str] = Field(since="v4.5.0", alias="mtgoFoilId")
    """The Magic: The Gathering Online card foil identifier."""

    mtgo_id: Optional[str] = Field(since="v4.5.0", alias="mtgoId")
    """The Magic: The Gathering Online card identifier."""

    mtgjson_v4_id: Optional[str] = Field(since="v5.0.0", alias="mtgjsonV4Id")
    """The universal unique identifier generated by MTGJSON. Each entry is unique. 
    Entries are for MTGJSON v4 uuid generation. """

    multiverse_id: Optional[str] = Field(since="v4.0.0", alias="multiverseId")
    """The Wizards of the Coast card identifier used in conjunction with Gatherer."""

    scryfall_id: Optional[str] = Field(since="v4.0.0", alias="scryfallId")
    """The universal unique identifier generated by Scryfall. Note that cards with 
    multiple faces are not unique. """

    scryfall_oracle_id: Optional[str] = Field(since="v4.3.1", alias="scryfallOracleId")
    """The unique identifier generated by Scryfall for this card's oracle identity. 
    This value is consistent across reprinted card editions, and unique among 
    different cards with the same name (tokens, Unstable variants, etc). """

    scryfall_illustration_id: Optional[str] = Field(
        since="v4.3.1", alias="scryfallIllustrationId"
    )
    """The unique identifier generated by Scryfall for the card artwork that remains 
    consistent across reprints. Newly spoiled cards may not have this field yet. """

    tcgplayer_product_id: Optional[str] = Field(
        since="v4.2.1", alias="tcgplayerProductId"
    )
    """The TCGplayer card identifier."""

    tcgplayer_etched_product_id: Optional[str] = Field(
        since="v5.2.0", alias="tcgplayerEtchedProductId"
    )
    """The TCGplayer etched card identifier."""


class Keywords(MightstoneModel):
    ability_words: List[str] = Field(since="v4.3.0", alias="abilityWords")
    """A list of ability words found in rules text on cards.
    Examples: "Adamant", "Addendum", "Alliance", "Battalion", "Bloodrush" """

    keyword_abilities: List[str] = Field(since="v4.3.0", alias="keywordAbilities")
    """A list of keyword abilities found in rules text on cards
    Examples: "Absorb", "Affinity", "Afflict", "Afterlife", "Aftermath" """

    keyword_actions: List[str] = Field(since="v4.3.0", alias="keywordActions")
    """A list of keyword actions found in rules text on cards.
    Examples: "Abandon", "Activate", "Adapt", "Amass", "Assemble" """


class LeadershipSkills(MightstoneModel):
    brawl: bool = Field(since="v4.5.1", alias="brawl")
    """If the card can be your commander in the Brawl format."""

    commander: bool = Field(since="v4.5.1", alias="commander")
    """If the card can be your commander in the Commander/EDH format."""

    oathbreaker: bool = Field(since="v4.5.1", alias="oathbreaker")
    """If the card can be your commander in the Oathbreaker format."""


class Legalities(MightstoneModel):
    brawl: Optional[str] = Field(since="v4.0.0", alias="brawl")
    """If the card is legal in the Brawl play format."""

    commander: Optional[str] = Field(since="v4.0.0", alias="commander")
    """If the card is legal in the Commander play format."""

    duel: Optional[str] = Field(since="v4.0.0", alias="duel")
    """If the card is legal in the Duel Commander play format."""

    future: Optional[str] = Field(since="v4.0.0", alias="future")
    """If the card is legal in the future for the Standard play format."""

    frontier: Optional[str] = Field(since="v4.0.0", alias="frontier")
    """If the card is legal in the Frontier play format."""

    gladiator: Optional[str] = Field(since="v5.2.0", alias="gladiator")
    """If the card is legal in the Gladiator play format."""

    historic: Optional[str] = Field(since="v5.1.0", alias="historic")
    """If the card is legal in the Historic play format."""

    historicbrawl: Optional[str] = Field(since="v5.2.0", alias="historicbrawl")
    """If the card is legal in the Historic Brawl play format."""

    legacy: Optional[str] = Field(since="v4.0.0", alias="legacy")
    """If the card is legal in the Legacy play format."""

    modern: Optional[str] = Field(since="v4.0.0", alias="modern")
    """If the card is legal in the Modern play format."""

    oldschool: Optional[str] = Field(since="v5.2.0", alias="oldschool")
    """If the card is legal in the Old School play format."""

    pauper: Optional[str] = Field(since="v5.2.0", alias="pauper")
    """If the card is legal in the Pauper play format."""

    paupercommander: Optional[str] = Field(since="v5.2.0", alias="paupercommander")
    """If the card is legal in the Pauper Commander play format."""

    penny: Optional[str] = Field(since="v4.0.0", alias="penny")
    """If the card is legal in the Penny Dreadful play format."""

    pioneer: Optional[str] = Field(since="v4.6.0", alias="pioneer")
    """If the card is legal in the Pioneer play format."""

    premodern: Optional[str] = Field(since="v5.2.0", alias="premodern")
    """If the card is legal in the Pre-Modern play format."""

    standard: Optional[str] = Field(since="v4.0.0", alias="standard")
    """If the card is legal in the Standard play format."""

    vintage: Optional[str] = Field(since="v4.0.0", alias="vintage")
    """If the card is legal in the Vintage play format."""


class Meta(MightstoneModel):
    date: datetime.date = Field(since="v4.0.0", alias="date")
    """The current release date in ISO 8601 format for the MTGJSON build."""

    version: str = Field(since="v4.0.0", alias="version")
    """The current SemVer version for the MTGJSON build appended with the build date."""


class PurchaseUrls(MightstoneModel):
    card_kingdom: Optional[str] = Field(since="v5.0.0", alias="cardKingdom")
    """The URL to purchase a product on Card Kingdom."""

    card_kingdom_etched: Optional[str] = Field(
        since="v5.2.0", alias="cardKingdomEtched"
    )
    """The URL to purchase an etched product on Card Kingdom."""

    card_kingdom_foil: Optional[str] = Field(since="v5.0.0", alias="cardKingdomFoil")
    """The URL to purchase a foil product on Card Kingdom."""

    cardmarket: Optional[str] = Field(since="v4.4.0", alias="cardmarket")
    """"The URL to purchase a product on Cardmarket."""

    tcgplayer: Optional[str] = Field(since="v4.4.0", alias="tcgplayer")
    """The URL to purchase a product on TCGplayer."""

    tcgplayer_etched: Optional[str] = Field(since="v5.2.0", alias="tcgplayerEtched")
    """The URL to purchase an etched product on TCGplayer."""


class Rulings(MightstoneModel):
    date: Optional[datetime.date] = Field(since="v4.0.0", alias="date")
    """The release date in ISO 8601 format for the rule."""
    text: Optional[str] = Field(since="v4.0.0", alias="text")
    """The text ruling of the card."""


class SealedProduct(MightstoneModel):
    identifiers: Identifiers = Field(since="v5.2.0", alias="identifiers")
    """A list of identifiers associated to a product. See the Identifiers Data Model."""
    name: str = Field(since="v5.2.0", alias="name")
    """The name of the product."""
    purchase_urls: PurchaseUrls = Field(since="v5.2.0", alias="purchaseUrls")
    """Links that navigate to websites where the product can be purchased. See the 
    Purchase Urls Data Model. """
    release_date: Optional[datetime.date] = Field(since="v5.2.0", alias="releaseDate")
    """The release date in ISO 8601 format for the product."""
    uuid: UUID = Field(since="v5.2.0", alias="uuid")
    """The universal unique identifier (v5) generated by MTGJSON. Each entry is 
    unique. """


class TcgPlayerSKU(MightstoneModel):
    condition: str = Field(since="v5.1.0", alias="condition")
    """The condition of the card. Examples: "DAMAGED", "HEAVILY_PLAYED", 
    "LIGHTLY_PLAYED", "MODERATELY_PLAYED", "NEAR_MINT" """

    finishes: Optional[List[str]] = Field(since="v5.2.0", alias="finishes")
    """The finishes of the card.
    Examples: "FOIL_ETCHED" """

    language: str = Field(since="v5.1.0", alias="language")
    """The language of the card. Examples: "CHINESE_SIMPLIFIED", 
    "CHINESE_TRADITIONAL", "ENGLISH", "FRENCH", "GERMAN" """

    printing: str = Field(since="v5.1.0", alias="printing")
    """The printing style of the card.
    Examples: "FOIL", "NON_FOIL" """

    product_id: str = Field(since="v5.1.0", alias="productId")
    """The product identifier of the card."""

    sku_id: str = Field(since="v5.1.0", alias="skuId")
    """The SKU identifier of the card."""


class Translations(MightstoneModel):
    """
    The Translations Data Model describes a Set name translated per available language.
    """

    ancient_greek: Optional[str] = Field(since="v4.6.0", alias="Ancient Greek")
    """The set name translation in Ancient Greek."""

    arabic: Optional[str] = Field(since="v4.6.0", alias="Arabic")
    """The set name translation in Arabic."""

    chineese_simplified: Optional[str] = Field(
        since="v4.0.0", alias="Chinese Simplified"
    )
    """The set name translation in Chinese Simplified."""

    chineese_traditional: Optional[str] = Field(
        since="v4.6.0", alias="Chinese Traditional"
    )
    """The set name translation in Chinese Traditional."""

    french: Optional[str] = Field(since="v4.0.0", alias="French")
    """The set name translation in French."""

    german: Optional[str] = Field(since="v4.0.0", alias="German")
    """The set name translation in German."""

    hebrew: Optional[str] = Field(since="v4.6.0", alias="Hebrew")
    """The set name translation in Hebrew."""

    italian: Optional[str] = Field(since="v4.0.0", alias="Italian")
    """The set name translation in Italian."""

    japanese: Optional[str] = Field(since="v4.0.0", alias="Japanese")
    """The set name translation in Japanese."""

    korean: Optional[str] = Field(since="v4.0.0", alias="Korean")
    """The set name translation in Korean."""

    latin: Optional[str] = Field(since="v4.6.0", alias="Latin")
    """The set name translation in Latin."""

    phyrexian: Optional[str] = Field(since="v4.7.0", alias="Phyrexian")
    """The set name translation in Phyrexian."""

    portuguese_brazil: Optional[str] = Field(
        since="v4.0.0", alias="Portuguese (Brazil)"
    )
    """The set name translation in Portuguese (Brazil)."""

    russian: Optional[str] = Field(since="v4.0.0", alias="Russian")
    """The set name translation in Russian."""

    sanskrit: Optional[str] = Field(since="v4.6.0", alias="Sanskrit")
    """The set name translation in Sanskrit."""

    spanish: Optional[str] = Field(since="v4.0.0", alias="Spanish")
    """The set name translation in Spanish."""


class CardAtomic(MightstoneModel):
    """
    The Card (Atomic) Data Model describes the properties of a single atomic card,
    an oracle-like entity of a Magic: The Gathering card that only stores evergreen
    data that would never change from printing to printing.
    """

    ascii_name: Optional[str] = Field(since="v5.0.0", alias="asciiName")
    """The ASCII (Basic/128) code formatted card name with no 
    special unicode characters. """

    color_identity: List[str] = Field(since="v4.0.0", alias="colorIdentity")
    """A list of all the colors found in manaCost, colorIndicator, and text.
    Examples: "B", "G", "R", "U", "W" """

    color_indicator: Optional[List[str]] = Field(since="v4.0.2", alias="colorIndicator")
    """A list of all the colors in the color indicator (The symbol prefixed to a 
    card's types). Examples: "B", "G", "R", "U", "W" """

    colors: List[str] = Field(since="v4.0.0", alias="colors")
    """A list of all the colors in manaCost and colorIndicator. Some cards may not 
    have values, such as cards with "Devoid" in its text. Examples: "B", "G", "R", 
    "U", "W" """

    converted_mana_cost: float = Field(
        since="v4.0.0", alias="convertedManaCost", deprecated=True
    )
    """The converted mana cost of the card. Use the manaValue property."""

    edhrec_rank: Optional[int] = Field(since="v4.5.0", alias="edhrecRank")
    """The card rank on EDHRec."""

    face_converted_mana_cost: Optional[float] = Field(
        since="v4.1.1", alias="faceConvertedManaCost", deprecated=True
    )
    """The converted mana cost or mana value for the face for either half or part of 
    the card. Use the faceManaValue property. """

    face_mana_value: Optional[float] = Field(since="v5.2.0", alias="faceManaValue")
    """The mana value of the face for either half or part of the card. Formally known 
    as "converted mana cost". """

    face_name: Optional[str] = Field(since="v5.0.0", alias="faceName")
    """The name on the face of the card."""

    foreign_data: List[ForeignData] = Field(since="v4.0.0", alias="foreignData")
    """A list of data properties in other languages. See the Foreign Data Data Model."""

    hand: Optional[str] = Field(since="v4.2.1", alias="hand")
    """The starting maximum hand size total modifier. A + or - character precedes an 
    integer. """

    has_alternative_deck_limit: Optional[bool] = Field(
        since="v5.0.0", alias="hasAlternativeDeckLimit"
    )
    """If the card allows a value other than 4 copies in a deck."""

    identifiers: Identifiers = Field(since="v5.0.0", alias="identifiers")
    """A list of identifiers associated to a card. See the Identifiers Data Model."""

    is_funny: Optional[bool] = Field(since="v5.2.0", alias="isFunny")
    """If the card is part of a funny set."""
    is_reserved: Optional[bool] = Field(since="v4.0.1", alias="isReserved")
    """If the card is on the Magic: The Gathering Reserved List."""
    keywords: Optional[List[str]] = Field(since="v5.1.0", alias="keywords")
    """A list of keywords found on the card."""

    layout: str = Field(since="v4.0.0", alias="layout")
    """The type of card layout. For a token card, this will be "token".
    Examples: "adventure", "aftermath", "art_series", "augment", "class" """

    leadership_skills: Optional[LeadershipSkills] = Field(
        since="v4.5.1", alias="leadershipSkills"
    )
    """A list of formats the card is legal to be a commander in. See the Leadership 
    Skills Data Model. """

    legalities: Legalities = Field(since="v4.0.0", alias="legalities")
    """A list of play formats the card the card is legal in. See the Legalities Data 
    Model. """

    life: Optional[str] = Field(since="v4.2.1", alias="life")
    """The starting life total modifier. A plus or minus character precedes an 
    integer. Used only on cards with "Vanguard" in its types. """

    loyalty: Optional[str] = Field(since="v4.0.0", alias="loyalty")
    """The starting loyalty value of the card. Used only on cards with "Planeswalker" 
    in its types. """

    mana_cost: Optional[str] = Field(since="v4.0.0", alias="manaCost")
    """The mana cost of the card wrapped in brackets for each value.
    Example: "{1}{B}" """

    mana_value: float = Field(since="v5.2.0", alias="manaValue")
    """The mana value of the card. Formally known as "converted mana cost"."""

    name: str = Field(since="v4.0.0", alias="name")
    """The name of the card. Cards with multiple faces, like "Split" and "Meld" cards 
    are given a delimiter. Example: "Wear // Tear" """

    power: Optional[str] = Field(since="v4.0.0", alias="power")
    """The power of the card."""

    printings: Optional[List[str]] = Field(since="v4.0.0", alias="printings")
    """A list of set printing codes the card was printed in, formatted in uppercase."""

    purchase_urls: PurchaseUrls = Field(since="v4.4.0", alias="purchaseUrls")
    """Links that navigate to websites where the card can be purchased. See the 
    Purchase Urls Data Model. """

    rulings: List[Rulings] = Field(since="v4.0.0", alias="rulings")
    """The official rulings of the card. See the Rulings Data Model."""

    side: Optional[str] = Field(since="v4.1.0", alias="side")
    """The identifier of the card side. Used on cards with multiple faces on the same 
    card. Examples: "a", "b", "c", "d", "e" """

    subtypes: List[str] = Field(since="v4.0.0", alias="subtypes")
    """A list of card subtypes found after em-dash.
    Examples: "Abian", "Adventure", "Advisor", "Aetherborn", "Ajani" """

    supertypes: List[str] = Field(since="v4.0.0", alias="supertypes")
    """A list of card supertypes found before em-dash.
    Examples: "Basic", "Host", "Legendary", "Ongoing", "Snow" """

    text: Optional[str] = Field(since="v4.0.0", alias="text")
    """The rules text of the card."""

    toughness: Optional[str] = Field(since="v4.0.0", alias="toughness")
    """The toughness of the card."""

    type: str = Field(since="v4.0.0", alias="type")
    """The type of the card as visible, including any supertypes and subtypes."""

    types: List[str] = Field(since="v4.0.0", alias="types")
    """A list of all card types of the card, including Un‑sets and gameplay variants.
    Examples: "Artifact", "Card", "Conspiracy", "Creature", "Dragon" """


class CardDeck(MightstoneModel):
    artist: Optional[str] = Field(since="v4.0.0", alias="artist")
    """The name of the artist that illustrated the card art."""

    ascii_name: Optional[str] = Field(since="v5.0.0", alias="asciiName")
    """The ASCII (Basic/128) code formatted card name with no special unicode 
    characters. """

    availability: List[str] = Field(since="v5.0.0", alias="availability")
    """A list of the card's available printing types.
    Examples: "arena", "dreamcast", "mtgo", "paper", "shandalar" """

    booster_types: Optional[List[str]] = Field(since="v5.2.1", alias="boosterTypes")
    """A list of types this card is in a booster pack.
    Examples: "deck", "draft" """

    border_color: str = Field(since="v4.0.0", alias="borderColor")
    """The color of the card border.
    Examples: "black", "borderless", "gold", "silver", "white" """

    card_parts: Optional[List[str]] = Field(since="v5.2.0", alias="cardParts")
    """A list of card names associated to this card, such as "Meld" card face names."""

    color_identity: Optional[List[str]] = Field(since="v4.0.0", alias="colorIdentity")
    """A list of all the colors found in manaCost, colorIndicator, and text.
    Examples: "B", "G", "R", "U", "W" """

    color_indicator: Optional[List[str]] = Field(since="v4.0.2", alias="colorIndicator")
    """A list of all the colors in the color indicator (The symbol prefixed to a 
    card's types). Examples: "B", "G", "R", "U", "W" """

    colors: List[str] = Field(since="v4.0.0", alias="colors")
    """A list of all the colors in manaCost and colorIndicator. Some cards may not 
    have values, such as cards with "Devoid" in its text. Examples: "B", "G", "R", 
    "U", "W" """

    converted_mana_cost: float = Field(
        since="v4.0.0", alias="convertedManaCost", deprecated=True
    )
    """The converted mana cost of the card. Use the manaValue property."""

    count: int = Field(since="v4.4.1", alias="count")
    """The count of how many of this card exists in a relevant deck."""

    duel_deck: Optional[str] = Field(since="v4.2.0", alias="duelDeck")
    """The indicator for which duel deck the card is in.
    Examples: "a", "b" """

    edhrec_rank: Optional[int] = Field(since="v4.5.0", alias="edhrecRank")
    """The card rank on EDHRec."""

    face_converted_mana_cost: Optional[float] = Field(
        since="v4.1.1", alias="faceConvertedManaCost", deprecated=True
    )
    """The converted mana cost or mana value for the face for either half or part of 
    the card. Use the faceManaValue property. """

    face_flavor_name: Optional[str] = Field(since="v5.2.0", alias="faceFlavorName")
    """The flavor name on the face of the card."""

    face_mana_value: Optional[float] = Field(since="v5.2.0", alias="faceManaValue")
    """The mana value of the face for either half or part of the card. Formally known 
    as "converted mana cost". """

    face_name: Optional[str] = Field(since="v5.0.0", alias="faceName")
    """The name on the face of the card."""

    finishes: List[str] = Field(since="v5.2.0", alias="finishes")
    """The finishes of the card.
    Examples: "etched", "foil", "nonfoil", "signed" """

    flavor_name: Optional[str] = Field(since="v5.0.0", alias="flavorName")
    """The promotional card name printed above the true card name on special cards 
    that has no game function. See this card for an example. """

    flavor_text: Optional[str] = Field(since="v4.0.0", alias="flavorText")
    """The italicized text found below the rules text that has no game function."""

    foreign_data: List[ForeignData] = Field(since="v4.0.0", alias="foreignData")
    """A list of data properties in other languages. See the Foreign Data Data Model."""

    frame_effects: Optional[List[str]] = Field(since="v4.6.0", alias="frameEffects")
    """The visual frame effects.
    Examples: "colorshifted", "companion", "compasslanddfc", "convertdfc", "devoid"
    """
    frame_version: str = Field(since="v4.0.0", alias="frameVersion")
    """The version of the card frame style.
    Examples: "1993", "1997", "2003", "2015", "future" """

    hand: Optional[str] = Field(since="v4.2.1", alias="hand")
    """The starting maximum hand size total modifier. A + or - character precedes an 
    integer. """

    has_alternative_deck_limit: Optional[bool] = Field(
        since="v5.0.0", alias="hasAlternativeDeckLimit"
    )
    """If the card allows a value other than 4 copies in a deck."""

    has_content_warning: Optional[bool] = Field(
        since="v5.0.0", alias="hasContentWarning"
    )
    """If the card marked by Wizards of the Coast for having sensitive content. Cards 
    with this property may have missing or degraded properties and values. See this 
    official article for more information. """

    has_foil: bool = Field(since="v4.0.0", alias="hasFoil", deprecated=True)
    """If the card can be found in foil. Use the finishes property."""

    has_non_foil: bool = Field(since="v4.0.0", alias="hasNonFoil", deprecated=True)
    """If the card can be found in non-foil. Use the finishes property."""

    identifiers: Identifiers = Field(since="v5.0.0", alias="identifiers")
    """A list of identifiers associated to a card. See the Identifiers Data Model."""

    is_alternative: Optional[bool] = Field(since="v4.2.0", alias="isAlternative")
    """If the card is an alternate variation to an original printing."""

    is_foil: bool = Field(since="v5.0.0", alias="isFoil")
    """If the card is in foil."""

    is_full_art: Optional[bool] = Field(since="v4.4.2", alias="isFullArt")
    """If the card has full artwork."""

    is_funny: Optional[bool] = Field(since="v5.2.0", alias="isFunny")
    """If the card is part of a funny set."""

    is_online_only: Optional[bool] = Field(since="v4.0.1", alias="isOnlineOnly")
    """If the card is only available in online game variations."""

    is_oversized: Optional[bool] = Field(since="v4.0.0", alias="isOversized")
    """If the card is oversized."""

    is_promo: Optional[bool] = Field(since="v4.4.2", alias="isPromo")
    """If the card is a promotional printing."""

    is_rebalanced: Optional[bool] = Field(since="v5.2.0", alias="isRebalanced")
    """If the card is rebalanced for the Alchemy play format."""

    is_reprint: Optional[bool] = Field(since="v4.4.2", alias="isReprint")
    """If the card has been reprinted."""

    is_reserved: Optional[bool] = Field(since="v4.0.1", alias="isReserved")
    """If the card is on the Magic: The Gathering Reserved List."""

    is_starter: Optional[bool] = Field(since="v4.0.0", alias="isStarter")
    """If the card is found in a starter deck such as Planeswalker/Brawl decks."""

    is_story_spotlight: Optional[bool] = Field(since="v4.4.2", alias="isStorySpotlight")
    """If the card is a Story Spotlight card."""

    is_textless: Optional[bool] = Field(since="v4.4.2", alias="isTextless")
    """If the card does not have a text box."""

    is_timeshifted: Optional[bool] = Field(since="v4.4.1", alias="isTimeshifted")
    """If the card is "timeshifted", a feature of certain sets where a card will have 
    a different frameVersion. """

    keywords: Optional[List[str]] = Field(since="v5.0.0", alias="keywords")
    """A list of keywords found on the card."""

    language: str = Field(since="v5.2.1", alias="language")
    """The language the card is printed in. Examples: "Ancient Greek", "Arabic", 
    "Chinese Simplified", "Chinese Traditional", "English" """
    layout: str = Field(since="v4.0.0", alias="layout")
    """The type of card layout. For a token card, this will be "token".
    Examples: "adventure", "aftermath", "art_series", "augment", "class"
    """

    leadership_skills: Optional[LeadershipSkills] = Field(
        since="v4.5.1", alias="leadershipSkills"
    )
    """A list of formats the card is legal to be a commander in. See the Leadership 
    Skills Data Model. """

    legalities: Legalities = Field(since="v4.0.0", alias="legalities")
    """A list of play formats the card the card is legal in. See the Legalities Data 
    Model. """

    life: Optional[str] = Field(since="v4.2.1", alias="life")
    """The starting life total modifier. A plus or minus character precedes an 
    integer. Used only on cards with "Vanguard" in its types. """

    loyalty: Optional[str] = Field(since="v4.0.0", alias="loyalty")
    """The starting loyalty value of the card. Used only on cards with "Planeswalker" 
    in its types. """

    mana_cost: Optional[str] = Field(since="v4.0.0", alias="manaCost")
    """The mana cost of the card wrapped in brackets for each value.
    Example: "{1}{B}" """

    mana_value: float = Field(since="v5.2.0", alias="manaValue")
    """The mana value of the card. Formally known as "converted mana cost"."""

    name: str = Field(since="v4.0.0", alias="name")
    """The name of the card. Cards with multiple faces, like "Split" and "Meld" cards 
    are given a delimiter. Example: "Wear // Tear" """

    number: str = Field(since="v4.0.0", alias="number")
    """The number of the card. Can be prefixed or suffixed with a * or other 
    characters for promotional sets. """

    original_printings: Optional[List[str]] = Field(
        since="v5.2.0", alias="originalPrintings"
    )
    """A list of card UUID's to original printings of the card if this card is 
    somehow different from its original, such as rebalanced cards. """

    original_release_date: Optional[str] = Field(
        since="v5.1.0", alias="originalReleaseDate"
    )
    """The original release date in ISO 8601 format for a 
    promotional card printed outside of a cycle window, such as Secret Lair Drop 
    promotions. """

    original_text: Optional[str] = Field(since="v4.0.0", alias="originalText")
    """The text on the card as originally printed."""

    original_type: Optional[str] = Field(since="v4.0.0", alias="originalType")
    """The type of the card as originally printed. Includes any supertypes and 
    subtypes. """

    other_face_ids: Optional[List[str]] = Field(since="v4.6.1", alias="otherFaceIds")
    """A list of card UUID's to this card's counterparts, such as transformed or 
    melded faces. """

    power: Optional[str] = Field(since="v4.0.0", alias="power")
    """The power of the card. """

    printings: Optional[List[str]] = Field(since="v4.0.0", alias="printings")
    """A list of set printing codes the card was printed in, formatted in uppercase."""

    promo_types: Optional[List[str]] = Field(since="v5.0.0", alias="promoTypes")
    """A list of promotional types for a card.
    Examples: "alchemy", "arenaleague", "boosterfun", "boxtopper", "brawldeck" """

    purchaseUrls: PurchaseUrls = Field(since="v4.4.0", alias="purchaseUrls")
    """Links that navigate to websites where the card can be purchased. See the 
    Purchase Urls Data Model. """

    rarity: str = Field(since="v4.0.0", alias="rarity")
    """The card printing rarity. Rarity bonus relates to cards that have an alternate 
    availability in booster packs, while special relates to "Timeshifted" cards. 
    Examples: "bonus", "common", "mythic", "rare", "special" """

    rebalanced_printings: Optional[List[str]] = Field(
        since="v5.2.0", alias="rebalancedPrintings"
    )
    """A list of card UUID's to printings that are rebalanced 
    versions of this card. """

    rulings: List[Rulings] = Field(since="v4.0.0", alias="rulings")
    """The official rulings of the card. See the Rulings Data Model."""

    security_stamp: Optional[str] = Field(since="v5.2.0", alias="securityStamp")
    """The security stamp printed on the card.
    Examples: "acorn", "arena", "circle", "heart", "oval" """

    set_code: str = Field(since="v5.0.1", alias="setCode")
    """The set printing code that the card is from."""

    side: Optional[str] = Field(since="v4.1.0", alias="side")
    """The identifier of the card side. Used on cards with multiple faces on the same 
    card. Examples: "a", "b", "c", "d", "e" """

    signature: Optional[str] = Field(since="v5.2.0", alias="signature")
    """The name of the signature on the card."""

    subtypes: List[str] = Field(since="v4.0.0", alias="subtypes")
    """A list of card subtypes found after em-dash.
    Examples:
    "Abian", "Adventure", "Advisor", "Aetherborn", "Ajani" """

    supertypes: List[str] = Field(since="v4.0.0", alias="supertypes")
    """A list of card supertypes found before em-dash.
    Examples: "Basic", "Host", "Legendary", "Ongoing", "Snow" """

    text: Optional[str] = Field(since="v4.0.0", alias="text")
    """The rules text of the card."""

    toughness: Optional[str] = Field(since="v4.0.0", alias="toughness")
    """The toughness of the card."""

    type: str = Field(since="v4.0.0", alias="type")
    """The type of the card as visible, including any supertypes and subtypes."""

    types: List[str] = Field(since="v4.0.0", alias="types")
    """A list of all card types of the card, including Un‑sets and gameplay variants.
    Examples: "Artifact", "Card", "Conspiracy", "Creature", "Dragon" """

    uuid: UUID = Field(since="v4.0.0", alias="uuid")
    """The universal unique identifier (v5) generated by MTGJSON. Each entry is 
    unique. """

    variations: Optional[List[UUID]] = Field(since="v4.1.2", alias="variations")
    """A list of card UUID's of this card with alternate printings in the same set. 
    Excludes Un‑sets. """

    watermark: Optional[str] = Field(since="v4.0.0", alias="watermark")
    """The name of the watermark on the card.
    Examples: "abzan", "agentsofsneak", "arena", "atarka", "azorius" """


class CardSet(MightstoneModel):
    """
    The Card (Set) Data Model describes the properties of a single card in a ``Set``
    Data Model.
    """

    artist: Optional[str] = Field(since="v4.0.0", alias="artist")
    """The name of the artist that illustrated the card art."""

    ascii_name: Optional[str] = Field(since="v5.0.0", alias="asciiName")
    """The ASCII (Basic/128) code formatted card name with no 
    special unicode characters. """

    availability: List[str] = Field(since="v5.0.0", alias="availability")
    """A list of the card's available printing types.
    Examples: "arena", "dreamcast", "mtgo", "paper", "shandalar"
    """

    booster_types: Optional[List[str]] = Field(since="v5.2.1", alias="boosterTypes")
    """A list of types this card is in a booster pack.
    Examples: "deck", "draft" """

    border_color: str = Field(since="v4.0.0", alias="borderColor")
    """The color of the card border.
    Examples: "black", "borderless", "gold", "silver", "white" """

    card_parts: Optional[List[str]] = Field(since="v5.2.0", alias="cardParts")
    """A list of card names associated to this card, such as "Meld" card face names."""

    color_identity: List[str] = Field(since="v4.0.0", alias="colorIdentity")
    """A list of all the colors found in manaCost, colorIndicator, and text.
    Examples: "B", "G", "R", "U", "W" """

    color_indicator: Optional[List[str]] = Field(since="v4.0.2", alias="colorIndicator")
    """A list of all the colors in the color indicator (The symbol prefixed to a 
    card's types). Examples: "B", "G", "R", "U", "W" """

    colors: List[str] = Field(since="v4.0.0", alias="colors")
    """A list of all the colors in manaCost and colorIndicator. Some cards may not 
    have values, such as cards with "Devoid" in its text. Examples: "B", "G", "R", 
    "U", "W" """

    converted_mana_cost: float = Field(
        since="v4.0.0", alias="convertedManaCost", deprecated=True
    )
    """The converted mana cost of the card. Use the manaValue property."""

    edhrec_rank: Optional[int] = Field(since="v4.5.0", alias="edhrecRank")
    """The card rank on EDHRec."""

    face_converted_mana_cost: Optional[float] = Field(
        since="v4.1.1", alias="faceConvertedManaCost", deprecated=True
    )
    """The converted mana cost or mana value for the face for either half or part of 
    the card. Use the faceManaValue property. """

    face_flavor_name: Optional[str] = Field(since="v5.2.0", alias="faceFlavorName")
    """The flavor name on the face of the card."""

    face_mana_value: Optional[float] = Field(since="v5.2.0", alias="faceManaValue")
    """The mana value of the face for either half or part of the card. Formally known 
    as "converted mana cost". """

    face_name: Optional[str] = Field(since="v5.0.0", alias="faceName")
    """The name on the face of the card."""

    finishes: List[str] = Field(since="v5.2.0", alias="finishes")
    """The finishes of the card.
    Examples: "etched", "foil", "nonfoil", "signed" """

    flavor_name: Optional[str] = Field(since="v5.0.0", alias="flavorName")
    """The promotional card name printed above the true card name on special cards 
    that has no game function. See this card for an example. """

    flavor_text: Optional[str] = Field(since="v4.0.0", alias="flavorText")
    """The italicized text found below the rules text that has no game function."""

    foreign_data: List[ForeignData] = Field(since="v4.0.0", alias="foreignData")
    """A list of data properties in other languages. See the Foreign Data Data Model."""

    frame_effects: Optional[List[str]] = Field(since="v4.6.0", alias="frameEffects")
    """The visual frame effects.
    Examples: "colorshifted", "companion", "compasslanddfc", "convertdfc", "devoid" """

    frame_version: str = Field(since="v4.0.0", alias="frameVersion")
    """The version of the card frame style.
    Examples: "1993", "1997", "2003", "2015", "future" """

    hand: Optional[str] = Field(since="v4.2.1", alias="hand")
    """The starting maximum hand size total modifier. A + or - character precedes an 
    integer. """

    has_alternative_deck_limit: Optional[bool] = Field(
        since="v5.0.0", alias="hasAlternativeDeckLimit"
    )
    """If the card allows a value other than 4 copies in a deck."""

    has_content_warning: Optional[bool] = Field(
        since="v5.0.0", alias="hasContentWarning"
    )
    """If the card marked by Wiz""ards of the Coast for having 
    sensitive content. Cards with this property may have missing or degraded 
    properties and values. See this official article for more 
    information."" """

    has_foil: bool = Field(since="v4.0.0", alias="hasFoil", deprecated=True)
    """If the card can be found in foil. Use the finishes property."""

    has_non_foil: bool = Field(since="v4.0.0", alias="hasNonFoil", deprecated=True)
    """If the card can be found in non-foil. Use the finishes property."""

    identifiers: Identifiers = Field(since="v5.0.0", alias="identifiers")
    """A list of identifiers associated to a card. See the Identifiers Data Model."""

    is_alternative: Optional[bool] = Field(since="v4.2.0", alias="isAlternative")
    """If the card is an alternate variation to an original printing."""

    is_full_art: Optional[bool] = Field(since="v4.4.2", alias="isFullArt")
    """If the card has full artwork."""

    is_funny: Optional[bool] = Field(since="v5.2.0", alias="isFunny")
    """If the card is part of a funny set."""

    is_online_only: Optional[bool] = Field(since="v4.0.1", alias="isOnlineOnly")
    """If the card is only available in online game variations."""

    is_oversized: Optional[bool] = Field(since="v4.0.0", alias="isOversized")
    """If the card is oversized."""

    is_promo: Optional[bool] = Field(since="v4.4.2", alias="isPromo")
    """If the card is a promotional printing."""

    is_rebalanced: Optional[bool] = Field(since="v5.2.0", alias="isRebalanced")
    """If the card is rebalanced for the Alchemy 
    play format. """

    is_reprint: Optional[bool] = Field(since="v4.4.2", alias="isReprint")
    """If the card has been reprinted."""

    is_reserved: Optional[bool] = Field(since="v4.0.1", alias="isReserved")
    """If the card is on the Magic: The Gathering Reserved List."""

    is_starter: Optional[bool] = Field(since="v4.0.0", alias="isStarter")
    """If the card is found in a starter deck such as Planeswalker/Brawl decks."""

    is_story_spotlight: Optional[bool] = Field(since="v4.4.2", alias="isStorySpotlight")
    """If the card is a Story Spotlight card."""

    is_textless: Optional[bool] = Field(since="v4.4.2", alias="isTextless")
    """If the card does not have a text box."""

    is_timeshifted: Optional[bool] = Field(since="v4.4.1", alias="isTimeshifted")
    """If the card is "timeshifted", a feature of certain sets where a card will have 
    a different frameVersion. """

    keywords: Optional[List[str]] = Field(since="v5.0.0", alias="keywords")
    """A list of keywords found on the card"""

    language: str = Field(since="v5.2.1", alias="language")
    """The language the card is printed in. Examples: "Ancient Greek", "Arabic", 
    "Chinese Simplified", "Chinese Traditional", "English" """

    layout: str = Field(since="v4.0.0", alias="layout")
    """The type of card layout. For a token card, this will be "token".
    Examples: "adventure", "aftermath", "art_series", "augment", "class" """

    leadershipSkills: Optional[LeadershipSkills] = Field(
        since="v4.5.1", alias="leadershipSkills"
    )
    """A list of formats the card is legal to be a commander in. See the Leadership 
    Skills Data Model. """

    legalities: Legalities = Field(since="v4.0.0", alias="legalities")
    """A list of play formats the card the card is legal in. See the Legalities Data 
    Model. """

    life: Optional[str] = Field(since="v4.2.1", alias="life")
    """The starting life total modifier. A plus or minus character precedes an 
    integer. Used only on cards with "Vanguard" in its types. """

    loyalty: Optional[str] = Field(since="v4.0.0", alias="loyalty")
    """The starting loyalty value of the card. Used only on cards with "Planeswalker" 
    in its types. """

    mana_cost: Optional[str] = Field(since="v4.0.0", alias="manaCost")
    """The mana cost of the card wrapped in brackets for each value.
    Example: "{1}{B}" """

    mana_value: float = Field(since="v5.2.0", alias="manaValue")
    """The mana value of the card. Formally known as "converted mana cost"."""

    name: str = Field(since="v4.0.0", alias="name")
    """The name of the card. Cards with multiple faces, like "Split" and "Meld" cards 
    are given a delimiter of //. Example: "Wear // Tear" """

    number: str = Field(since="v4.0.0", alias="number")
    """The number of the card. Can be prefixed or suffixed with a * or other 
    characters for promotional sets. """

    original_printings: Optional[List[str]] = Field(
        since="v5.2.0", alias="originalPrintings"
    )
    """A list of card UUID's to original printings of the card if this card is 
    somehow different from its original, such as rebalanced cards. """

    original_release_date: Optional[str] = Field(
        since="v5.1.0", alias="originalReleaseDate"
    )
    """The original release date in ISO 8601 format for a promotional card printed 
    outside of a cycle window, such as Secret Lair Drop promotions. """

    original_text: Optional[str] = Field(since="v4.0.0", alias="originalText")
    """The text on the card as originally printed."""

    original_type: Optional[str] = Field(since="v4.0.0", alias="originalType")
    """The type of the card as originally printed. Includes any supertypes and 
    subtypes. """

    other_face_ids: Optional[List[str]] = Field(since="v4.6.1", alias="otherFaceIds")
    """A list of card UUID's to this card's counterparts, such as transformed or 
    melded faces. """

    power: Optional[str] = Field(since="v4.0.0", alias="power")
    """The power of the card."""

    printings: Optional[List[str]] = Field(since="v4.0.0", alias="printings")
    """A list of set printing codes the card was printed in, formatted in uppercase."""

    promo_types: Optional[List[str]] = Field(since="v5.0.0", alias="promoTypes")
    """A list of promotional types for a card.
    Examples: "alchemy", "arenaleague", "boosterfun", "boxtopper", "brawldeck"
    """

    purchase_urls: PurchaseUrls = Field(since="v4.4.0", alias="purchaseUrls")
    """Links that navigate to websites where the card can be purchased. See the 
    Purchase Urls Data Model. """

    rarity: str = Field(since="v4.0.0", alias="rarity")
    """The card printing rarity. Rarity bonus relates to cards that have an alternate 
    availability in booster packs, while special relates to "Timeshifted" cards. 
    Examples: "bonus", "common", "mythic", "rare", "special" """

    rebalanced_printings: Optional[List[UUID]] = Field(
        since="v5.2.0", alias="rebalancedPrintings"
    )
    """A list of card UUID's to printings that are rebalanced versions of this card."""

    rulings: List[Rulings] = Field(since="v4.0.0", alias="rulings")
    """The official rulings of the card. See the Rulings Data Model."""

    security_stamp: Optional[str] = Field(since="v5.2.0", alias="securityStamp")
    """The security stamp printed on the card.
    Examples: "acorn", "arena", "circle", "heart", "oval" """

    set_code: str = Field(since="v5.0.1", alias="setCode")
    """The set printing code that the card is from."""

    side: Optional[str] = Field(since="v4.1.0", alias="side")
    """The identifier of the card side. Used on cards with multiple faces on the same 
    card. Examples: "a", "b", "c", "d", "e" """

    signature: Optional[str] = Field(since="v5.2.0", alias="signature")
    """The name of the signature on the card."""

    subtypes: List[str] = Field(since="v4.0.0", alias="subtypes")
    """A list of card subtypes found after em-dash.
    Examples: "Abian", "Adventure", "Advisor", "Aetherborn", "Ajani" """

    supertypes: List[str] = Field(since="v4.0.0", alias="supertypes")
    """A list of card supertypes found before em-dash.
    Examples: "Basic", "Host", "Legendary", "Ongoing", "Snow" """

    text: Optional[str] = Field(since="v4.0.0", alias="text")
    """The rules text of the card."""

    toughness: Optional[str] = Field(since="v4.0.0", alias="toughness")
    """The toughness of the card."""

    type: str = Field(since="v4.0.0", alias="type")
    """Type of the card as visible, including any supertypes and subtypes."""

    types: List[str] = Field(since="v4.0.0", alias="types")
    """A list of all card types of the card, including Un‑sets and gameplay variants.
    Examples: "Artifact", "Card", "Conspiracy", "Creature", "Dragon" """

    uuid: UUID = Field(since="v4.0.0", alias="uuid")
    """The universal unique identifier (v5) generated by MTGJSON. Each entry is 
    unique. """

    variations: Optional[List[UUID]] = Field(since="v4.1.2", alias="variations")
    """A list of card UUID's of this card with alternate printings in the same set. 
    Excludes Un‑sets. """

    watermark: Optional[str] = Field(since="v4.0.0", alias="watermark")
    """The name of the watermark on the card.
    Examples: "abzan", "agentsofsneak", "arena", "atarka", "azorius" """


class CardToken(MightstoneModel):
    artist: Optional[str] = Field(since="v4.0.0", alias="artist")
    """The name of the artist that illustrated the card art."""

    ascii_name: Optional[str] = Field(since="v5.0.0", alias="asciiName")
    """The ASCII (Basic/128) code formatted card name with no special unicode 
    characters. """

    availability: List[str] = Field(since="v5.0.0", alias="availability")
    """A list of the card's available printing types.
    Examples: "arena", "dreamcast", "mtgo", "paper", "shandalar" """

    booster_types: Optional[List[str]] = Field(since="v5.2.1", alias="boosterTypes")
    """A list of types this card is in a booster pack.
    Examples: "deck", "draft" """

    border_color: str = Field(since="v4.0.0", alias="borderColor")
    """The color of the card border.
    Examples: "black", "borderless", "gold", "silver", "white" """

    card_parts: Optional[List[str]] = Field(since="v5.2.0", alias="cardParts")
    """A list of card names associated to this card, such as "Meld" card face names."""

    color_identity: List[str] = Field(since="v4.0.0", alias="colorIdentity")
    """A list of all the colors found in manaCost, colorIndicator, and text.
    Examples: "B", "G", "R", "U", "W" """

    color_indicator: Optional[List[str]] = Field(since="v4.0.2", alias="colorIndicator")
    """A list of all the colors in the color indicator (The symbol prefixed to a 
    card's types). Examples: "B", "G", "R", "U", "W" """

    colors: List[str] = Field(since="v4.0.0", alias="colors")
    """A list of all the colors in manaCost and colorIndicator. Some cards may not 
    have values, such as cards with "Devoid" in its text. Examples: "B", "G", "R", 
    "U", "W" """

    face_name: Optional[str] = Field(since="v5.0.0", alias="faceName")
    """The name on the face of the card."""

    face_flavor_name: Optional[str] = Field(since="v5.2.0", alias="faceFlavorName")
    """The flavor name on the face of the card."""

    finishes: List[str] = Field(since="v5.2.0", alias="finishes")
    """The finishes of the card.
    Examples: "etched", "foil", "nonfoil", "signed" """

    flavor_text: Optional[str] = Field(since="v4.0.0", alias="flavorText")
    """The italicized text found below the rules text that has no game function."""

    frame_effects: Optional[List[str]] = Field(since="v4.6.0", alias="frameEffects")
    """The visual frame effects.
    Examples: "colorshifted", "companion", "compasslanddfc", "convertdfc", "devoid" """

    frame_version: str = Field(since="v4.0.0", alias="frameVersion")
    """The version of the card frame style.
    Examples: "1993", "1997", "2003", "2015", "future" """

    has_foil: bool = Field(since="v4.0.0", alias="hasFoil", deprecated=True)
    """If the card can be found in foil. Use the finishes property."""

    has_non_foil: bool = Field(since="v4.0.0", alias="hasNonFoil", deprecated=True)
    """If the card can be found in non-foil. Use the finishes property."""

    identifiers: Identifiers = Field(since="v5.0.0", alias="identifiers")
    """A list of identifiers associated to a card. See the Identifiers Data Model."""

    is_full_art: Optional[bool] = Field(since="v4.4.2", alias="isFullArt")
    """If the card has full artwork."""

    is_funny: Optional[bool] = Field(since="v5.2.0", alias="isFunny")
    """If the card is part of a funny set."""

    is_online_only: Optional[bool] = Field(since="v4.0.1", alias="isOnlineOnly")
    """If the card is only available in online game variations."""

    is_promo: Optional[bool] = Field(since="v4.4.2", alias="isPromo")
    """If the card is a promotional printing."""

    is_reprint: Optional[bool] = Field(since="v4.4.2", alias="isReprint")
    """If the card has been reprinted."""

    keywords: Optional[List[str]] = Field(since="v5.0.0", alias="keywords")
    """A list of keywords found on the card."""

    language: str = Field(since="v5.2.1", alias="language")
    """The language the card is printed in. Examples: "Ancient Greek", "Arabic", 
    "Chinese Simplified", "Chinese Traditional", "English" """

    layout: str = Field(since="v4.0.0", alias="layout")
    """The type of card layout. For a token card, this will be "token".
    Examples: "adventure", "aftermath", "art_series", "augment", "class" """

    loyalty: Optional[str] = Field(since="v4.0.0", alias="loyalty")
    """The starting loyalty value of the card. Used only on cards with "Planeswalker" 
    in its types. """

    name: str = Field(since="v4.0.0", alias="name")
    """The name of the card. Cards with multiple faces, like "Split" and "Meld" cards 
    are given a delimiter. Example: "Wear // Tear" """

    number: str = Field(since="v4.0.0", alias="number")
    """The number of the card. Can be prefixed or suffixed with a * or other 
    characters for promotional sets. """

    other_face_ids: Optional[List[str]] = Field(since="v4.6.1", alias="otherFaceIds")
    """A list of card UUID's to this card's counterparts, such as transformed or 
    melded faces. """

    power: Optional[str] = Field(since="v4.0.0", alias="power")
    """The power of the card."""

    promo_types: Optional[List[str]] = Field(since="v5.0.0", alias="promoTypes")
    """A list of promotional types for a card.
    Examples: "alchemy", "arenaleague", "boosterfun", "boxtopper", "brawldeck" """

    reverse_related: List[str] = Field(since="v4.0.0", alias="reverseRelated")
    """The names of the cards that produce this card."""

    security_stamp: Optional[str] = Field(since="v5.2.0", alias="securityStamp")
    """The security stamp printed on the card.
    Examples: "acorn", "arena", "circle", "heart", "oval" """

    set_code: str = Field(since="v5.0.1", alias="setCode")
    """The set printing code that the card is from."""

    side: Optional[str] = Field(since="v4.1.0", alias="side")
    """The identifier of the card side. Used on cards with multiple faces on the same 
    card. Examples: "a", "b", "c", "d", "e" """

    signature: Optional[str] = Field(since="v5.2.0", alias="signature")
    """The name of the signature on the card."""

    subtypes: List[str] = Field(since="v4.0.0", alias="subtypes")
    """A list of card subtypes found after em-dash.
    Examples: "Abian", "Adventure", "Advisor", "Aetherborn", "Ajani" """

    supertypes: List[str] = Field(since="v4.0.0", alias="supertypes")
    """A list of card supertypes found before em-dash.
    Examples: "Basic", "Host", "Legendary", "Ongoing", "Snow" """

    text: Optional[str] = Field(since="v4.0.0", alias="text")
    """The rules text of the card."""

    toughness: Optional[str] = Field(since="v4.0.0", alias="toughness")
    """The toughness of the card."""

    type: str = Field(since="v4.0.0", alias="type")
    """The type of the card as visible, including any supertypes and subtypes."""

    types: List[str] = Field(since="v4.0.0", alias="types")
    """A list of all card types of the card, including Un‑sets and gameplay variants.
    Examples: "Artifact", "Card", "Conspiracy", "Creature", "Dragon" """

    uuid: UUID = Field(since="v4.0.0", alias="uuid")
    """The universal unique identifier (v5) generated by MTGJSON. Each entry is 
    unique. """

    watermark: Optional[str] = Field(since="v4.0.0", alias="watermark")
    """The name of the watermark on the card.
    Examples: "abzan", "agentsofsneak", "arena", "atarka", "azorius" """


class Deck(MightstoneModel):
    """
    The Deck Data Model describes a complete deck reference.
    """

    code: str = Field(since="v4.3.0", alias="code")
    """The set code for the deck."""

    file_name: Optional[str] = Field(since="v4.3.0", alias="fileName")
    """The file name for the deck. Combines the name and code fields to avoid 
    namespace collisions and are given a delimiter of _. Examples: 
    "SpiritSquadron_VOC" """

    name: str = Field(since="v4.3.0", alias="name")
    """The name of the deck."""

    release_date: Optional[datetime.date] = Field(since="v4.3.0", alias="releaseDate")
    """The release date in ISO 8601 format for the set. Returns 
    null if the set was not formally released as a product. """

    type: str = Field(since="v4.3.0", alias="type")
    """The type of deck. Examples: "Advanced Deck", "Advanced Pack", "Archenemy 
    Deck", "Basic Deck", "Brawl Deck" """

    commander: Optional[List[CardDeck]] = Field(since="v5.1.0", alias="commander")
    """The card that is the Commander in this deck. See the Card (Deck) Data Model."""

    main_board: List[CardDeck] = Field(since="v4.3.0", alias="mainBoard")
    """The cards in the main-board. See the Card (Deck) Data Model."""

    side_board: List[CardDeck] = Field(since="v4.3.0", alias="sideBoard")
    """The cards in the side-board. See the Card (Deck) Data Model."""


class Set(MightstoneModel):
    baseSetSize: int = Field(since="v4.1.0", alias="baseSetSize")
    """The number of cards in the set. This will default to totalSetSize if not 
    available. Wizards of the Coast sometimes prints extra cards 
    beyond the set size into promos or supplemental products. """

    block: Optional[str] = Field(since="v4.0.0", alias="block")
    """The block name the set was in."""

    booster: Optional[dict] = Field(since="v5.0.0", alias="booster")
    """A breakdown of possibilities and weights of cards in a booster pack. See the 
    Booster abstract model. """

    cards: List[CardSet] = Field(since="v4.0.0", alias="cards")
    """The list of cards in the set. See the Card (Set) Data Model."""

    cardsphere_set_id: Optional[int] = Field(since="v5.2.1", alias="cardsphereSetId")
    """The Cardsphere set identifier."""

    code: str = Field(since="v4.0.0", alias="code")
    """The set code for the set."""

    code_v3: Optional[str] = Field(since="v4.2.1", alias="codeV3")
    """The alternate set code Wizards of the Coast uses for a select few duel deck 
    sets. """

    is_foreign_only: Optional[bool] = Field(since="v4.4.1", alias="isForeignOnly")
    """If the set is available only outside the United States of America."""

    is_foil_only: bool = Field(since="v4.0.0", alias="isFoilOnly")
    """If the set is only available in foil."""

    is_non_foil_only: Optional[bool] = Field(since="v5.0.0", alias="isNonFoilOnly")
    """If the set is only available in non-foil."""

    is_online_only: bool = Field(since="v4.0.0", alias="isOnlineOnly")
    """If the set is only available in online game variations."""

    is_paper_only: Optional[bool] = Field(since="v4.6.2", alias="isPaperOnly")
    """If the set is available only in paper."""

    is_partial_preview: Optional[bool] = Field(since="v4.4.2", alias="isPartialPreview")
    """If the set is still in preview (spoiled). Preview sets do not have complete 
    data. """

    keyrune_code: str = Field(since="v4.3.2", alias="keyruneCode")
    """The matching Keyrune code for set image icons."""

    mcm_id: Optional[int] = Field(since="v4.4.0", alias="mcmId")
    """The Magic Card Market set identifier."""

    mcmIdExtras: Optional[int] = Field(since="v5.1.0", alias="mcmIdExtras")
    """The split Magic Card Market set identifier if a set is printed in two sets. 
    This identifier represents the second set's identifier. """

    mcmName: Optional[str] = Field(since="v4.4.0", alias="mcmName")
    """The Magic Card Market set name."""

    mtgoCode: Optional[str] = Field(since="v4.0.0", alias="mtgoCode")
    """The set code for the set as it appears on Magic: The Gathering Online."""

    name: str = Field(since="v4.0.0", alias="name")
    """The name of the set."""

    parent_code: Optional[str] = Field(since="v4.3.0", alias="parentCode")
    """The parent set code for set variations like promotions, guild kits, etc."""

    release_date: datetime.date = Field(since="v4.0.0", alias="releaseDate")
    """The release date in ISO 8601 format for the set."""

    sealed_product: Optional[List[SealedProduct]] = Field(
        since="v5.2.0", alias="sealedProduct"
    )
    """The sealed product information for the set. See the Sealed Product Data Model."""

    tcgplayerGroupId: Optional[int] = Field(since="v4.2.1", alias="tcgplayerGroupId")
    """The group identifier of the set on TCGplayer."""

    tokens: List[CardToken] = Field(since="v4.0.0", alias="tokens")
    """The tokens available to the set. See the Card (Token) Data Model."""

    totalSetSize: int = Field(since="v4.1.0", alias="totalSetSize")
    """The total number of cards in the set, including promotional and related 
    supplemental products but excluding Alchemy modifications - however those cards 
    are included in the set itself. """

    translations: Translations = Field(since="v4.3.2", alias="translations")
    """The translated set name by language. See the Translations Data Model."""

    type: str = Field(since="v4.0.0", alias="type")
    """The expansion type of the set.
    Examples: "alchemy", "archenemy", "arsenal", "box", "commander" """


class SetList(MightstoneModel):
    """
    The Set List Data Model describes a metadata-like properties and values for an
    individual Set.
    """

    baseSetSize: int = Field(since="v4.1.0", alias="baseSetSize")
    """The number of cards in the set. This will default to totalSetSize if not 
    available. Wizards of the Coast sometimes prints extra cards beyond the set size 
    into promos or supplemental products. """

    block: Optional[str] = Field(since="v4.0.0", alias="block")
    """The block name the set was in."""

    code: str = Field(since="v4.0.0", alias="code")
    """The set code for the set."""

    code_v3: Optional[str] = Field(since="v4.2.1", alias="codeV3")
    """The alternate set code Wizards of the Coast uses for a select few duel deck 
    sets. """

    is_foreign_only: Optional[bool] = Field(since="v4.4.1", alias="isForeignOnly")
    """If the set is available only outside the United States of America."""

    is_foil_only: bool = Field(since="v4.0.0", alias="isFoilOnly")
    """If the set is only available in foil."""

    is_non_foil_only: Optional[bool] = Field(since="v5.0.0", alias="isNonFoilOnly")
    """If the set is only available in non-foil."""

    is_online_only: bool = Field(since="v4.0.0", alias="isOnlineOnly")
    """If the set is only available in online game variations."""

    is_paper_only: Optional[bool] = Field(since="v4.6.2", alias="isPaperOnly")
    """If the set is only available in paper."""

    is_partial_preview: Optional[bool] = Field(since="v4.4.2", alias="isPartialPreview")
    """If the set is still in preview (spoiled). Preview sets do not have complete
    data. """

    keyrune_code: str = Field(since="v4.3.2", alias="keyruneCode")
    """The matching Keyrune code for set image icons."""

    mcm_id: Optional[int] = Field(since="v4.4.0", alias="mcmId")
    """The Magic Card Market set identifier."""

    mcm_id_extras: Optional[int] = Field(since="v5.1.0", alias="mcmIdExtras")
    """The split Magic Card Market set identifier if a set is printed in two sets.
    This identifier represents the second set's identifier. """

    mcm_name: Optional[str] = Field(since="v4.4.0", alias="mcmName")
    """The Magic Card Market set name."""

    mtgo_code: Optional[str] = Field(since="v4.0.0", alias="mtgoCode")
    """The set code for the set as it appears on Magic: The Gathering Online."""

    name: str = Field(since="v4.0.0", alias="name")
    """The name of the set."""

    parent_code: Optional[str] = Field(since="v4.3.0", alias="parentCode")
    """The parent set code for set variations like promotions, guild kits, etc."""

    release_date: datetime.date = Field(since="v4.0.0", alias="releaseDate")
    """The release date in ISO 8601 format for the set."""

    sealed_product: Optional[List[SealedProduct]] = Field(
        since="v5.1.0", alias="sealedProduct"
    )
    """The sealed product information for the set. See the Sealed Product Data Model."""

    tcgplayer_group_id: Optional[int] = Field(since="v4.2.1", alias="tcgplayerGroupId")
    """The group identifier of the set on TCGplayer."""

    total_set_size: int = Field(since="v4.1.0", alias="totalSetSize")
    """The total number of cards in the set, including promos and related
    supplemental products. """

    translations: Translations = Field(since="v4.3.2", alias="translations")
    """The translated set name by language. See the Translations Data Model."""

    type: str = Field(since="v4.0.0", alias="type")
    """The expansion type of the set.
    Examples: "alchemy", "archenemy", "arsenal", "box", "commander" """


class Card(MightstoneModel):
    """
    A card either a Card from a set, or a token
    """

    __root__: Union[CardSet, CardToken]


class RetailPrices(TypedDict):
    buylist: NotRequired[Dict[str, Dict[datetime.date, float]]]
    currency: str
    retail: Dict[str, Dict[datetime.date, float]]


class CardPrices(MightstoneModel):
    """
    A representation of the abstract model for card prices in MTGJSON
    """

    uuid: UUID
    mtgo: Optional[Dict[str, RetailPrices]]
    paper: Optional[Dict[str, RetailPrices]]


class CardAtomicGroup(MightstoneModel):
    """
    A representation of a group of Atomic Card such as returned by every _atomic
    methods of MtgJson client
    """

    name: str
    prints: List[CardAtomic]


class TcgPlayerSKUs(MightstoneModel):
    """
    A representation of a TcgPlayerSKU list associated to a card unique ID
    """

    uuid: UUID
    skus: List[TcgPlayerSKU]

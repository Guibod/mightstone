"""
MTGJSON models
"""

import datetime
from typing import Any, Dict, List, Optional

from pydantic import Field, RootModel, model_validator
from pydantic.types import UUID

from mightstone.common import generate_uuid_from_string
from mightstone.core import MightstoneDocument, MightstoneModel


class MtgJsonDocument(MightstoneDocument):
    id: Optional[UUID] = None  # type: ignore

    @model_validator(mode="wrap")
    @classmethod
    def enforce_id(cls, value: Any, handler) -> "MtgJsonDocument":
        """
        MTGJson entities don’t always have a uuid, plus the field name is not id, but
        may vary.

        We infer a UUID from the uuid field, then fall back by creating a uuid through
        lowercased ascii_name field if present, then on name field.
        """
        doc = handler(value)

        if not isinstance(value, Dict):
            return doc

        if not doc.id and "id" not in value:
            if "uuid" in value:
                doc.id = value["uuid"]
            elif "code" in value:
                doc.id = generate_uuid_from_string(value["code"])
            elif "asciiName" in value:
                doc.id = generate_uuid_from_string(value["asciiName"])
            elif "name" in value:
                doc.id = generate_uuid_from_string(value["name"])

        return doc


class Types(MightstoneModel):
    """
    The Types Data Model describes all types available on a Card.
    """

    sub_types: List[str] = Field(
        json_schema_extra={"since": "v4.0.0"}, alias="subTypes"
    )
    """A list of all available subtypes of a type.
    Examples: "Abian", "Adventure", "Advisor", "Aetherborn", "Ajani" """
    super_types: List[str] = Field(
        json_schema_extra={"since": "v4.0.0"}, alias="superTypes"
    )
    """A list of all available supertypes of a type.
    Examples: "Basic", "Host", "Legendary", "Ongoing", "Snow" """


class CardTypes(MightstoneModel):
    """
    The Card Types Data Model describes card types that a card may have.
    """

    artifact: Types = Field(json_schema_extra={"since": "v4.0.0"}, alias="artifact")
    """All possible subtypes and supertypes for Artifact cards."""

    conspiracy: Types = Field(json_schema_extra={"since": "v4.0.0"}, alias="conspiracy")
    """All possible subtypes and supertypes for Conspiracy cards."""

    creature: Types = Field(json_schema_extra={"since": "v4.0.0"}, alias="creature")
    """All possible subtypes and supertypes for Creature cards."""

    enchantment: Types = Field(
        json_schema_extra={"since": "v4.0.0"}, alias="enchantment"
    )
    """All possible subtypes and supertypes for Enchantment cards."""

    instant: Types = Field(json_schema_extra={"since": "v4.0.0"}, alias="instant")
    """All possible subtypes and supertypes for Instant cards."""

    land: Types = Field(json_schema_extra={"since": "v4.0.0"}, alias="land")
    """All possible subtypes and supertypes for Land cards."""

    phenomenon: Types = Field(json_schema_extra={"since": "v4.0.0"}, alias="phenomenon")
    """All possible subtypes and supertypes for Phenomenon cards."""

    plane: Types = Field(json_schema_extra={"since": "v4.0.0"}, alias="plane")
    """All possible subtypes and supertypes for Plane cards."""

    planeswalker: Types = Field(
        json_schema_extra={"since": "v4.0.0"}, alias="planeswalker"
    )
    """All possible subtypes and supertypes for Planeswalker."""

    scheme: Types = Field(json_schema_extra={"since": "v4.0.0"}, alias="scheme")
    """All possible subtypes and supertypes for Scheme cards."""

    sorcery: Types = Field(json_schema_extra={"since": "v4.0.0"}, alias="sorcery")
    """All possible subtypes and supertypes for Sorcery cards."""

    tribal: Types = Field(json_schema_extra={"since": "v4.0.0"}, alias="tribal")
    """All possible subtypes and supertypes for Tribal cards."""

    vanguard: Types = Field(json_schema_extra={"since": "v4.0.0"}, alias="vanguard")
    """All possible subtypes and supertypes for Vanguard cards."""


class DeckList(MightstoneModel):
    """
    The Deck List Data Model describes a metadata-like model for a Deck.
    """

    code: str = Field(json_schema_extra={"since": "v4.3.0"}, alias="code")
    """The set code for the deck."""

    file_name: str = Field(json_schema_extra={"since": "v4.3.0"}, alias="fileName")
    """The file name for the deck. Combines the name and code fields to avoid 
    namespace collisions and are given a delimiter of _. Examples: 
    "SpiritSquadron_VOC" """

    name: str = Field(json_schema_extra={"since": "v4.3.0"}, alias="name")
    """The name of the deck."""

    release_date: Optional[datetime.date] = Field(
        json_schema_extra={"since": "v4.3.0"}, alias="releaseDate", default=None
    )
    """The release date in ISO 8601 format for the set. Returns 
    null if the set was not formally released as a product. """

    type: str = Field(json_schema_extra={"since": "v4.3.0"}, alias="type")
    """The type of deck. Examples: "Advanced Deck", "Advanced Pack", "Archenemy 
    Deck", "Basic Deck", "Brawl Deck" """


class ForeignData(MightstoneModel):
    """
    The Foreign Data Data Model describes a list of properties for various Card Data
    Models in alternate languages.
    """

    face_name: Optional[str] = Field(
        json_schema_extra={"since": "v5.0.1"}, alias="faceName", default=None
    )
    """The foreign name on the face of the card."""

    flavor_text: Optional[str] = Field(
        json_schema_extra={"since": "v4.0.0"}, alias="flavorText", default=None
    )
    """The foreign flavor text of the card."""

    language: str = Field(json_schema_extra={"since": "v4.0.0"}, alias="language")
    """The foreign language of card. Examples: "Ancient Greek", "Arabic", "Chinese 
    Simplified", "Chinese Traditional", "French" """

    multiverse_id: Optional[int] = Field(
        json_schema_extra={"since": "v4.0.0"}, alias="multiverseId", default=None
    )
    """The foreign multiverse identifier of the card."""

    name: str = Field(json_schema_extra={"since": "v4.0.0"}, alias="name")
    """The foreign name of the card."""

    text: Optional[str] = Field(
        json_schema_extra={"since": "v4.0.0"}, alias="text", default=None
    )
    """The foreign text ruling of the card."""

    type: Optional[str] = Field(
        json_schema_extra={"since": "v4.0.0"}, alias="type", default=None
    )
    """The foreign type of the card. Includes any supertypes and subtypes."""


class Identifiers(MightstoneModel):
    card_kingdom_etched_id: Optional[str] = Field(
        json_schema_extra={"since": "v5.2.0"}, alias="cardKingdomEtchedId", default=None
    )
    """The Card Kingdom etched card identifier."""

    card_kingdom_foil_id: Optional[str] = Field(
        json_schema_extra={"since": "v5.0.0"}, alias="cardKingdomFoilId", default=None
    )
    """The Card Kingdom foil card identifier."""

    card_kingdom_id: Optional[str] = Field(
        json_schema_extra={"since": "v5.0.0"}, alias="cardKingdomId", default=None
    )
    """The Card Kingdom card identifier."""

    cardsphere_id: Optional[str] = Field(
        json_schema_extra={"since": "v5.2.1"}, alias="cardsphereId", default=None
    )
    """The Cardsphere card identifier."""

    mcm_id: Optional[str] = Field(
        json_schema_extra={"since": "v4.4.0"}, alias="mcmId", default=None
    )
    """The Card Market card identifier."""

    mcm_meta_id: Optional[str] = Field(
        json_schema_extra={"since": "v4.4.0"}, alias="mcmMetaId", default=None
    )
    """The Card Market card meta identifier."""

    mtg_arena_id: Optional[str] = Field(
        json_schema_extra={"since": "v4.5.0"}, alias="mtgArenaId", default=None
    )
    """The Magic: The Gathering Arena card identifier."""

    mtgjson_foil_version_id: Optional[str] = Field(
        json_schema_extra={"since": "v5.2.1"},
        alias="mtgjsonFoilVersionId",
        default=None,
    )
    """The universal unique identifier (v4) generated by MTGJSON for the foil version 
    of the card."""

    mtgjson_non_foil_version_id: Optional[str] = Field(
        json_schema_extra={"since": "v5.2.1"},
        alias="mtgjsonNonFoilVersionId",
        default=None,
    )
    """The universal unique identifier (v4) generated by MTGJSON for the non-foil 
    version of the card."""

    mtgo_foil_id: Optional[str] = Field(
        json_schema_extra={"since": "v4.5.0"}, alias="mtgoFoilId", default=None
    )
    """The Magic: The Gathering Online card foil identifier."""

    mtgo_id: Optional[str] = Field(
        json_schema_extra={"since": "v4.5.0"}, alias="mtgoId", default=None
    )
    """The Magic: The Gathering Online card identifier."""

    mtgjson_v4_id: Optional[str] = Field(
        json_schema_extra={"since": "v5.0.0"}, alias="mtgjsonV4Id", default=None
    )
    """The universal unique identifier generated by MTGJSON. Each entry is unique. 
    Entries are for MTGJSON v4 uuid generation. """

    multiverse_id: Optional[str] = Field(
        json_schema_extra={"since": "v4.0.0"}, alias="multiverseId", default=None
    )
    """The Wizards of the Coast card identifier used in conjunction with Gatherer."""

    scryfall_id: Optional[str] = Field(
        json_schema_extra={"since": "v4.0.0"}, alias="scryfallId", default=None
    )
    """The universal unique identifier generated by Scryfall. Note that cards with 
    multiple faces are not unique. """

    scryfall_oracle_id: Optional[str] = Field(
        json_schema_extra={"since": "v4.3.1"}, alias="scryfallOracleId", default=None
    )
    """The unique identifier generated by Scryfall for this card's oracle identity. 
    This value is consistent across reprinted card editions, and unique among 
    different cards with the same name (tokens, Unstable variants, etc). """

    scryfall_illustration_id: Optional[str] = Field(
        json_schema_extra={"since": "v4.3.1"},
        alias="scryfallIllustrationId",
        default=None,
    )
    """The unique identifier generated by Scryfall for the card artwork that remains 
    consistent across reprints. Newly spoiled cards may not have this field yet. """

    tcgplayer_product_id: Optional[str] = Field(
        json_schema_extra={"since": "v4.2.1"}, alias="tcgplayerProductId", default=None
    )
    """The TCGplayer card identifier."""

    tcgplayer_etched_product_id: Optional[str] = Field(
        json_schema_extra={"since": "v5.2.0"},
        alias="tcgplayerEtchedProductId",
        default=None,
    )
    """The TCGplayer etched card identifier."""


class Keywords(MightstoneModel):
    ability_words: List[str] = Field(
        json_schema_extra={"since": "v4.3.0"}, alias="abilityWords"
    )
    """A list of ability words found in rules text on cards.
    Examples: "Adamant", "Addendum", "Alliance", "Battalion", "Bloodrush" """

    keyword_abilities: List[str] = Field(
        json_schema_extra={"since": "v4.3.0"}, alias="keywordAbilities"
    )
    """A list of keyword abilities found in rules text on cards
    Examples: "Absorb", "Affinity", "Afflict", "Afterlife", "Aftermath" """

    keyword_actions: List[str] = Field(
        json_schema_extra={"since": "v4.3.0"}, alias="keywordActions"
    )
    """A list of keyword actions found in rules text on cards.
    Examples: "Abandon", "Activate", "Adapt", "Amass", "Assemble" """


class LeadershipSkills(MightstoneModel):
    brawl: bool = Field(json_schema_extra={"since": "v4.5.1"}, alias="brawl")
    """If the card can be your commander in the Brawl format."""

    commander: bool = Field(json_schema_extra={"since": "v4.5.1"}, alias="commander")
    """If the card can be your commander in the Commander/EDH format."""

    oathbreaker: bool = Field(
        json_schema_extra={"since": "v4.5.1"}, alias="oathbreaker"
    )
    """If the card can be your commander in the Oathbreaker format."""


class Legalities(MightstoneModel):
    brawl: Optional[str] = Field(
        json_schema_extra={"since": "v4.0.0"}, alias="brawl", default=None
    )
    """If the card is legal in the Brawl play format."""

    commander: Optional[str] = Field(
        json_schema_extra={"since": "v4.0.0"}, alias="commander", default=None
    )
    """If the card is legal in the Commander play format."""

    duel: Optional[str] = Field(
        json_schema_extra={"since": "v4.0.0"}, alias="duel", default=None
    )
    """If the card is legal in the Duel Commander play format."""

    explorer: Optional[str] = Field(
        json_schema_extra={"since": "v5.2.1"}, alias="explorer", default=None
    )
    """Legality of the card in the Explorer play format."""

    future: Optional[str] = Field(
        json_schema_extra={"since": "v4.0.0"}, alias="future", default=None
    )
    """If the card is legal in the future for the Standard play format."""

    gladiator: Optional[str] = Field(
        json_schema_extra={"since": "v5.2.0"}, alias="gladiator", default=None
    )
    """If the card is legal in the Gladiator play format."""

    historic: Optional[str] = Field(
        json_schema_extra={"since": "v5.1.0"}, alias="historic", default=None
    )
    """If the card is legal in the Historic play format."""

    historicbrawl: Optional[str] = Field(
        json_schema_extra={"since": "v5.2.0"}, alias="historicbrawl", default=None
    )
    """If the card is legal in the Historic Brawl play format."""

    legacy: Optional[str] = Field(
        json_schema_extra={"since": "v4.0.0"}, alias="legacy", default=None
    )
    """If the card is legal in the Legacy play format."""

    modern: Optional[str] = Field(
        json_schema_extra={"since": "v4.0.0"}, alias="modern", default=None
    )
    """If the card is legal in the Modern play format."""

    oldschool: Optional[str] = Field(
        json_schema_extra={"since": "v5.2.0"}, alias="oldschool", default=None
    )
    """If the card is legal in the Old School play format."""

    pauper: Optional[str] = Field(
        json_schema_extra={"since": "v5.2.0"}, alias="pauper", default=None
    )
    """If the card is legal in the Pauper play format."""

    paupercommander: Optional[str] = Field(
        json_schema_extra={"since": "v5.2.0"}, alias="paupercommander", default=None
    )
    """If the card is legal in the Pauper Commander play format."""

    penny: Optional[str] = Field(
        json_schema_extra={"since": "v4.0.0"}, alias="penny", default=None
    )
    """If the card is legal in the Penny Dreadful play format."""

    pioneer: Optional[str] = Field(
        json_schema_extra={"since": "v4.6.0"}, alias="pioneer", default=None
    )
    """If the card is legal in the Pioneer play format."""

    predh: Optional[str] = Field(
        json_schema_extra={"since": "v5.2.1"}, alias="predh", default=None
    )
    """Legality of the card in the PreDH play format."""

    premodern: Optional[str] = Field(
        json_schema_extra={"since": "v5.2.0"}, alias="premodern", default=None
    )
    """If the card is legal in the Pre-Modern play format."""

    standard: Optional[str] = Field(
        json_schema_extra={"since": "v4.0.0"}, alias="standard", default=None
    )
    """If the card is legal in the Standard play format."""

    vintage: Optional[str] = Field(
        json_schema_extra={"since": "v4.0.0"}, alias="vintage", default=None
    )
    """If the card is legal in the Vintage play format."""


class Meta(MightstoneModel):
    date: datetime.date = Field(json_schema_extra={"since": "v4.0.0"}, alias="date")
    """The current release date in ISO 8601 format for the MTGJSON build."""

    version: str = Field(json_schema_extra={"since": "v4.0.0"}, alias="version")
    """The current SemVer version for the MTGJSON build appended with the build date."""


class PurchaseUrls(MightstoneModel):
    card_kingdom: Optional[str] = Field(
        json_schema_extra={"since": "v5.0.0"}, alias="cardKingdom", default=None
    )
    """The URL to purchase a product on Card Kingdom."""

    card_kingdom_etched: Optional[str] = Field(
        json_schema_extra={"since": "v5.2.0"}, alias="cardKingdomEtched", default=None
    )
    """The URL to purchase an etched product on Card Kingdom."""

    card_kingdom_foil: Optional[str] = Field(
        json_schema_extra={"since": "v5.0.0"}, alias="cardKingdomFoil", default=None
    )
    """The URL to purchase a foil product on Card Kingdom."""

    cardmarket: Optional[str] = Field(
        json_schema_extra={"since": "v4.4.0"}, alias="cardmarket", default=None
    )
    """"The URL to purchase a product on Cardmarket."""

    tcgplayer: Optional[str] = Field(
        json_schema_extra={"since": "v4.4.0"}, alias="tcgplayer", default=None
    )
    """The URL to purchase a product on TCGplayer."""

    tcgplayer_etched: Optional[str] = Field(
        json_schema_extra={"since": "v5.2.0"}, alias="tcgplayerEtched", default=None
    )
    """The URL to purchase an etched product on TCGplayer."""


class RelatedCards(MightstoneModel):
    reverse_related: Optional[List[str]] = Field(
        json_schema_extra={"since": "v5.2.1"}, alias="reverseRelated", default=None
    )
    """A list of card names associated to a card, such as "meld" cards and token 
    creation."""

    spellbook: Optional[List[str]] = Field(
        json_schema_extra={"since": "v5.2.1"}, alias="spellbook", default=None
    )
    """A list of card names associated to a card's Spellbook mechanic."""


class Rulings(MightstoneModel):
    date: Optional[datetime.date] = Field(
        json_schema_extra={"since": "v4.0.0"}, alias="date", default=None
    )
    """The release date in ISO 8601 format for the rule."""
    text: Optional[str] = Field(
        json_schema_extra={"since": "v4.0.0"}, alias="text", default=None
    )
    """The text ruling of the card."""


class SealedProduct(MightstoneModel):
    category: Optional[str] = Field(
        json_schema_extra={"since": "v5.2.1"}, alias="category", default=None
    )
    """The category of this product."""

    identifiers: Identifiers = Field(
        json_schema_extra={"since": "v5.2.0"}, alias="identifiers"
    )
    """A list of identifiers associated to a product. See the Identifiers Data Model."""

    name: str = Field(json_schema_extra={"since": "v5.2.0"}, alias="name")
    """The name of the product."""

    product_size: Optional[int] = Field(
        json_schema_extra={"since": "v5.2.1"}, alias="productSize", default=None
    )
    """The size of the product."""

    purchase_urls: PurchaseUrls = Field(
        json_schema_extra={"since": "v5.2.0"}, alias="purchaseUrls"
    )
    """Links that navigate to websites where the product can be purchased. See the 
    Purchase Urls Data Model. """

    release_date: Optional[datetime.date] = Field(
        json_schema_extra={"since": "v5.2.0"}, alias="releaseDate", default=None
    )
    """The release date in ISO 8601 format for the product."""

    subtype: Optional[str] = Field(
        json_schema_extra={"since": "v5.2.1"}, alias="subtype", default=None
    )
    """The category subtype of this product."""

    uuid: UUID = Field(json_schema_extra={"since": "v5.2.0"}, alias="uuid")
    """The universal unique identifier (v5) generated by MTGJSON. Each entry is 
    unique. """


class TcgPlayerSKU(MightstoneModel):
    condition: str = Field(json_schema_extra={"since": "v5.1.0"}, alias="condition")
    """The condition of the card. Examples: "DAMAGED", "HEAVILY_PLAYED", 
    "LIGHTLY_PLAYED", "MODERATELY_PLAYED", "NEAR_MINT" """

    finishes: Optional[List[str]] = Field(
        json_schema_extra={"since": "v5.2.0"}, alias="finishes", default=None
    )
    """The finishes of the card.
    Examples: "FOIL_ETCHED" """

    language: str = Field(json_schema_extra={"since": "v5.1.0"}, alias="language")
    """The language of the card. Examples: "CHINESE_SIMPLIFIED", 
    "CHINESE_TRADITIONAL", "ENGLISH", "FRENCH", "GERMAN" """

    printing: str = Field(json_schema_extra={"since": "v5.1.0"}, alias="printing")
    """The printing style of the card.
    Examples: "FOIL", "NON_FOIL" """

    product_id: Optional[str] = Field(
        json_schema_extra={"since": "v5.1.0"},
        alias="productId",
        default=None,
        coerce_numbers_to_str=True,
    )
    """The product identifier of the card."""

    sku_id: Optional[str] = Field(
        json_schema_extra={"since": "v5.1.0"},
        alias="skuId",
        default=None,
        coerce_numbers_to_str=True,
    )
    """The SKU identifier of the card."""


class Translations(MightstoneModel):
    """
    The Translations Data Model describes a Set name translated per available language.
    """

    ancient_greek: Optional[str] = Field(
        json_schema_extra={"since": "v4.6.0"}, alias="Ancient Greek", default=None
    )
    """The set name translation in Ancient Greek."""

    arabic: Optional[str] = Field(
        json_schema_extra={"since": "v4.6.0"}, alias="Arabic", default=None
    )
    """The set name translation in Arabic."""

    chineese_simplified: Optional[str] = Field(
        json_schema_extra={"since": "v4.0.0"}, alias="Chinese Simplified", default=None
    )
    """The set name translation in Chinese Simplified."""

    chineese_traditional: Optional[str] = Field(
        json_schema_extra={"since": "v4.6.0"}, alias="Chinese Traditional", default=None
    )
    """The set name translation in Chinese Traditional."""

    french: Optional[str] = Field(
        json_schema_extra={"since": "v4.0.0"}, alias="French", default=None
    )
    """The set name translation in French."""

    german: Optional[str] = Field(
        json_schema_extra={"since": "v4.0.0"}, alias="German", default=None
    )
    """The set name translation in German."""

    hebrew: Optional[str] = Field(
        json_schema_extra={"since": "v4.6.0"}, alias="Hebrew", default=None
    )
    """The set name translation in Hebrew."""

    italian: Optional[str] = Field(
        json_schema_extra={"since": "v4.0.0"}, alias="Italian", default=None
    )
    """The set name translation in Italian."""

    japanese: Optional[str] = Field(
        json_schema_extra={"since": "v4.0.0"}, alias="Japanese", default=None
    )
    """The set name translation in Japanese."""

    korean: Optional[str] = Field(
        json_schema_extra={"since": "v4.0.0"}, alias="Korean", default=None
    )
    """The set name translation in Korean."""

    latin: Optional[str] = Field(
        json_schema_extra={"since": "v4.6.0"}, alias="Latin", default=None
    )
    """The set name translation in Latin."""

    phyrexian: Optional[str] = Field(
        json_schema_extra={"since": "v4.7.0"}, alias="Phyrexian", default=None
    )
    """The set name translation in Phyrexian."""

    portuguese_brazil: Optional[str] = Field(
        json_schema_extra={"since": "v4.0.0"}, alias="Portuguese (Brazil)", default=None
    )
    """The set name translation in Portuguese (Brazil)."""

    russian: Optional[str] = Field(
        json_schema_extra={"since": "v4.0.0"}, alias="Russian", default=None
    )
    """The set name translation in Russian."""

    sanskrit: Optional[str] = Field(
        json_schema_extra={"since": "v4.6.0"}, alias="Sanskrit", default=None
    )
    """The set name translation in Sanskrit."""

    spanish: Optional[str] = Field(
        json_schema_extra={"since": "v4.0.0"}, alias="Spanish", default=None
    )
    """The set name translation in Spanish."""


class CardFace(MightstoneModel):
    """
    The Card (Atomic) Data Model describes the properties of a single atomic card,
    an oracle-like entity of a Magic: The Gathering card that only stores evergreen
    data that would never change from printing to printing.
    """

    attraction_lights: Optional[List[str]] = Field(
        json_schema_extra={"since": "v5.2.1"}, alias="attractionLights", default=None
    )
    """A list of attraction lights found on a card, available only to cards printed in 
    certain Un-sets."""

    color_identity: List[str] = Field(
        json_schema_extra={"since": "v4.0.0"}, alias="colorIdentity"
    )
    """A list of all the colors found in manaCost, colorIndicator, and text.
    Examples: "B", "G", "R", "U", "W" """

    color_indicator: Optional[List[str]] = Field(
        json_schema_extra={"since": "v4.0.2"}, alias="colorIndicator", default=None
    )
    """A list of all the colors in the color indicator (The symbol prefixed to a 
    card's types). Examples: "B", "G", "R", "U", "W" """

    colors: List[str] = Field(json_schema_extra={"since": "v4.0.0"}, alias="colors")
    """A list of all the colors in manaCost and colorIndicator. Some cards may not 
    have values, such as cards with "Devoid" in its text. Examples: "B", "G", "R", 
    "U", "W" """

    converted_mana_cost: float = Field(
        json_schema_extra={"since": "v4.0.0"},
        alias="convertedManaCost",
        deprecated=True,
    )
    """The converted mana cost of the card. Use the manaValue property."""

    defense: Optional[str] = Field(
        json_schema_extra={"since": "v5.2.1"}, alias="defense", default=None
    )
    """The defense of the card. Used on battle cards."""

    edhrec_rank: Optional[int] = Field(
        json_schema_extra={"since": "v4.5.0"}, alias="edhrecRank", default=None
    )
    """The card rank on EDHRec."""

    edhrec_saltiness: Optional[float] = Field(
        json_schema_extra={"since": "v5.2.1"}, alias="edhrecSaltiness", default=None
    )
    """The card saltiness score on EDHRec."""

    face_converted_mana_cost: Optional[float] = Field(
        json_schema_extra={"since": "v4.1.1"},
        alias="faceConvertedManaCost",
        deprecated=True,
        default=None,
    )
    """The converted mana cost or mana value for the face for either half or part of 
    the card. Use the faceManaValue property. """

    face_mana_value: Optional[float] = Field(
        json_schema_extra={"since": "v5.2.0"}, alias="faceManaValue", default=None
    )
    """The mana value of the face for either half or part of the card. Formally known 
    as "converted mana cost". """

    face_name: Optional[str] = Field(
        json_schema_extra={"since": "v5.0.0"}, alias="faceName", default=None
    )
    """The name on the face of the card."""

    first_printing: Optional[str] = Field(
        json_schema_extra={"since": "v5.2.1"}, alias="firstPrinting", default=None
    )
    """The set code the card was first printed in."""

    foreign_data: List[ForeignData] = Field(
        json_schema_extra={"since": "v5.2.1"}, alias="foreignData"
    )
    """A list of data properties in other languages. See the Foreign Data Data Model."""

    hand: Optional[str] = Field(
        json_schema_extra={"since": "v4.2.1"}, alias="hand", default=None
    )
    """The starting maximum hand size total modifier. A + or - character precedes an 
    integer. """

    has_alternative_deck_limit: Optional[bool] = Field(
        json_schema_extra={"since": "v5.0.0"},
        alias="hasAlternativeDeckLimit",
        default=None,
    )
    """If the card allows a value other than 4 copies in a deck."""

    identifiers: Identifiers = Field(
        json_schema_extra={"since": "v5.0.0"}, alias="identifiers"
    )
    """A list of identifiers associated to a card. See the Identifiers Data Model."""

    is_funny: Optional[bool] = Field(
        json_schema_extra={"since": "v5.2.1"}, alias="isFunny", default=None
    )
    """If the card is part of a funny set."""

    is_reserved: Optional[bool] = Field(
        json_schema_extra={"since": "v4.0.1"}, alias="isReserved", default=None
    )
    """If the card is on the Magic: The Gathering Reserved List."""

    keywords: Optional[List[str]] = Field(
        json_schema_extra={"since": "v5.1.0"}, alias="keywords", default=None
    )
    """A list of keywords found on the card."""

    layout: str = Field(json_schema_extra={"since": "v4.0.0"}, alias="layout")
    """The type of card layout. For a token card, this will be "token".
    Examples: "adventure", "aftermath", "art_series", "augment", "class" """

    leadership_skills: Optional[LeadershipSkills] = Field(
        json_schema_extra={"since": "v4.5.1"}, alias="leadershipSkills", default=None
    )
    """A list of formats the card is legal to be a commander in. See the Leadership 
    Skills Data Model. """

    legalities: Legalities = Field(
        json_schema_extra={"since": "v4.0.0"}, alias="legalities"
    )
    """A list of play formats the card the card is legal in. See the Legalities Data 
    Model. """

    life: Optional[str] = Field(
        json_schema_extra={"since": "v4.2.1"}, alias="life", default=None
    )
    """The starting life total modifier. A plus or minus character precedes an 
    integer. Used only on cards with "Vanguard" in its types. """

    loyalty: Optional[str] = Field(
        json_schema_extra={"since": "v4.0.0"}, alias="loyalty", default=None
    )
    """The starting loyalty value of the card. Used only on cards with "Planeswalker" 
    in its types. """

    mana_cost: Optional[str] = Field(
        json_schema_extra={"since": "v4.0.0"}, alias="manaCost", default=None
    )
    """The mana cost of the card wrapped in brackets for each value.
    Example: "{1}{B}" """

    mana_value: float = Field(json_schema_extra={"since": "v5.2.0"}, alias="manaValue")
    """The mana value of the card. Formally known as "converted mana cost"."""

    name: str = Field(json_schema_extra={"since": "v4.0.0"}, alias="name")
    """The name of the card. Cards with multiple faces, like "Split" and "Meld" cards 
    are given a delimiter. Example: "Wear // Tear" """

    power: Optional[str] = Field(
        json_schema_extra={"since": "v4.0.0"}, alias="power", default=None
    )
    """The power of the card."""

    printings: Optional[List[str]] = Field(
        json_schema_extra={"since": "v4.0.0"}, alias="printings", default=None
    )
    """A list of set printing codes the card was printed in, formatted in uppercase."""

    purchase_urls: PurchaseUrls = Field(
        json_schema_extra={"since": "v4.4.0"}, alias="purchaseUrls"
    )
    """Links that navigate to websites where the card can be purchased. See the 
    Purchase Urls Data Model. """

    related_cards: Optional[RelatedCards] = Field(
        json_schema_extra={"since": "v5.2.1"}, alias="RelatedCards", default=None
    )

    rulings: Optional[List[Rulings]] = Field(
        json_schema_extra={"since": "v4.0.0"}, alias="rulings", default=None
    )
    """The official rulings of the card. See the Rulings Data Model."""

    side: Optional[str] = Field(
        json_schema_extra={"since": "v4.1.0"}, alias="side", default=None
    )
    """The identifier of the card side. Used on cards with multiple faces on the same 
    card. Examples: "a", "b", "c", "d", "e" """

    subsets: Optional[List[str]] = Field(
        json_schema_extra={"since": "v4.0.0"}, alias="subsets", default=None
    )
    """The names of the subset printings a card is in. Used primarily on "Secret Lair 
    Drop" cards."""

    subtypes: List[str] = Field(json_schema_extra={"since": "v4.0.0"}, alias="subtypes")
    """A list of card subtypes found after em-dash.
    Examples: "Abian", "Adventure", "Advisor", "Aetherborn", "Ajani" """

    supertypes: List[str] = Field(
        json_schema_extra={"since": "v4.0.0"}, alias="supertypes"
    )
    """A list of card supertypes found before em-dash.
    Examples: "Basic", "Host", "Legendary", "Ongoing", "Snow" """

    text: Optional[str] = Field(
        json_schema_extra={"since": "v4.0.0"}, alias="text", default=None
    )
    """The rules text of the card."""

    toughness: Optional[str] = Field(
        json_schema_extra={"since": "v4.0.0"}, alias="toughness", default=None
    )
    """The toughness of the card."""

    type: str = Field(json_schema_extra={"since": "v4.0.0"}, alias="type")
    """The type of the card as visible, including any supertypes and subtypes."""

    types: List[str] = Field(json_schema_extra={"since": "v4.0.0"}, alias="types")
    """A list of all card types of the card, including Un‑sets and gameplay variants.
    Examples: "Artifact", "Card", "Conspiracy", "Creature", "Dragon" """


class CardDeck(MightstoneModel):
    artist: Optional[str] = Field(
        json_schema_extra={"since": "v4.0.0"}, alias="artist", default=None
    )
    """The name of the artist that illustrated the card art."""

    ascii_name: Optional[str] = Field(
        json_schema_extra={"since": "v5.0.0"}, alias="asciiName", default=None
    )
    """The ASCII (Basic/128) code formatted card name with no special unicode 
    characters. """

    attraction_lights: Optional[List[str]] = Field(
        json_schema_extra={"since": "v5.2.1"}, alias="attractionLights", default=None
    )
    """A list of attraction lights found on a card, available only to cards printed in 
    certain Un-sets."""

    availability: List[str] = Field(
        json_schema_extra={"since": "v5.0.0"}, alias="availability"
    )
    """A list of the card's available printing types.
    Examples: "arena", "dreamcast", "mtgo", "paper", "shandalar" """

    booster_types: Optional[List[str]] = Field(
        json_schema_extra={"since": "v5.2.1"}, alias="boosterTypes", default=None
    )
    """A list of types this card is in a booster pack.
    Examples: "deck", "draft" """

    border_color: str = Field(
        json_schema_extra={"since": "v4.0.0"}, alias="borderColor"
    )
    """The color of the card border.
    Examples: "black", "borderless", "gold", "silver", "white" """

    card_parts: Optional[List[str]] = Field(
        json_schema_extra={"since": "v5.2.0"}, alias="cardParts", default=None
    )
    """A list of card names associated to this card, such as "Meld" card face names."""

    color_identity: Optional[List[str]] = Field(
        json_schema_extra={"since": "v4.0.0"}, alias="colorIdentity", default=None
    )
    """A list of all the colors found in manaCost, colorIndicator, and text.
    Examples: "B", "G", "R", "U", "W" """

    color_indicator: Optional[List[str]] = Field(
        json_schema_extra={"since": "v4.0.2"}, alias="colorIndicator", default=None
    )
    """A list of all the colors in the color indicator (The symbol prefixed to a 
    card's types). Examples: "B", "G", "R", "U", "W" """

    colors: List[str] = Field(json_schema_extra={"since": "v4.0.0"}, alias="colors")
    """A list of all the colors in manaCost and colorIndicator. Some cards may not 
    have values, such as cards with "Devoid" in its text. Examples: "B", "G", "R", 
    "U", "W" """

    converted_mana_cost: float = Field(
        json_schema_extra={"since": "v4.0.0"},
        alias="convertedManaCost",
        deprecated=True,
    )
    """The converted mana cost of the card. Use the manaValue property."""

    quantity: int = Field(json_schema_extra={"since": "v4.4.1"}, alias="count")
    """The count of how many of this card exists in a relevant deck."""

    defense: Optional[str] = Field(
        json_schema_extra={"since": "v5.2.1"}, alias="defense", default=None
    )
    """The defense of the card. Used on battle cards."""

    duel_deck: Optional[str] = Field(
        json_schema_extra={"since": "v4.2.0"}, alias="duelDeck", default=None
    )
    """The indicator for which duel deck the card is in.
    Examples: "a", "b" """

    edhrec_rank: Optional[int] = Field(
        json_schema_extra={"since": "v4.5.0"}, alias="edhrecRank", default=None
    )
    """The card rank on EDHRec."""

    edhrec_saltiness: Optional[float] = Field(
        json_schema_extra={"since": "v5.2.1"}, alias="edhrecSaltiness", default=None
    )
    """The card saltiness score on EDHRec."""

    face_converted_mana_cost: Optional[float] = Field(
        json_schema_extra={"since": "v4.1.1"},
        alias="faceConvertedManaCost",
        deprecated=True,
        default=None,
    )
    """The converted mana cost or mana value for the face for either half or part of 
    the card. Use the faceManaValue property. """

    face_flavor_name: Optional[str] = Field(
        json_schema_extra={"since": "v5.2.0"}, alias="faceFlavorName", default=None
    )
    """The flavor name on the face of the card."""

    face_mana_value: Optional[float] = Field(
        json_schema_extra={"since": "v5.2.0"}, alias="faceManaValue", default=None
    )
    """The mana value of the face for either half or part of the card. Formally known 
    as "converted mana cost". """

    face_name: Optional[str] = Field(
        json_schema_extra={"since": "v5.0.0"}, alias="faceName", default=None
    )
    """The name on the face of the card."""

    finishes: List[str] = Field(json_schema_extra={"since": "v5.2.0"}, alias="finishes")
    """The finishes of the card.
    Examples: "etched", "foil", "nonfoil", "signed" """

    flavor_name: Optional[str] = Field(
        json_schema_extra={"since": "v5.0.0"}, alias="flavorName", default=None
    )
    """The promotional card name printed above the true card name on special cards 
    that has no game function. See this card for an example. """

    flavor_text: Optional[str] = Field(
        json_schema_extra={"since": "v4.0.0"}, alias="flavorText", default=None
    )
    """The italicized text found below the rules text that has no game function."""

    foreign_data: List[ForeignData] = Field(
        json_schema_extra={"since": "v4.0.0"}, alias="foreignData"
    )
    """A list of data properties in other languages. See the Foreign Data Data Model."""

    frame_effects: Optional[List[str]] = Field(
        json_schema_extra={"since": "v4.6.0"}, alias="frameEffects", default=None
    )
    """The visual frame effects.
    Examples: "colorshifted", "companion", "compasslanddfc", "convertdfc", "devoid"
    """
    frame_version: str = Field(
        json_schema_extra={"since": "v4.0.0"}, alias="frameVersion"
    )
    """The version of the card frame style.
    Examples: "1993", "1997", "2003", "2015", "future" """

    hand: Optional[str] = Field(
        json_schema_extra={"since": "v4.2.1"}, alias="hand", default=None
    )
    """The starting maximum hand size total modifier. A + or - character precedes an 
    integer. """

    has_alternative_deck_limit: Optional[bool] = Field(
        json_schema_extra={"since": "v5.0.0"},
        alias="hasAlternativeDeckLimit",
        default=None,
    )
    """If the card allows a value other than 4 copies in a deck."""

    has_content_warning: Optional[bool] = Field(
        json_schema_extra={"since": "v5.0.0"}, alias="hasContentWarning", default=None
    )
    """If the card marked by Wizards of the Coast for having sensitive content. Cards 
    with this property may have missing or degraded properties and values. See this 
    official article for more information. """

    has_foil: bool = Field(
        json_schema_extra={"since": "v4.0.0"}, alias="hasFoil", deprecated=True
    )
    """If the card can be found in foil. Use the finishes property."""

    has_non_foil: bool = Field(
        json_schema_extra={"since": "v4.0.0"}, alias="hasNonFoil", deprecated=True
    )
    """If the card can be found in non-foil. Use the finishes property."""

    identifiers: Identifiers = Field(
        json_schema_extra={"since": "v5.0.0"}, alias="identifiers"
    )
    """A list of identifiers associated to a card. See the Identifiers Data Model."""

    is_alternative: Optional[bool] = Field(
        json_schema_extra={"since": "v4.2.0"}, alias="isAlternative", default=None
    )
    """If the card is an alternate variation to an original printing."""

    is_foil: bool = Field(json_schema_extra={"since": "v5.0.0"}, alias="isFoil")
    """If the card is in foil."""

    is_full_art: Optional[bool] = Field(
        json_schema_extra={"since": "v4.4.2"}, alias="isFullArt", default=None
    )
    """If the card has full artwork."""

    is_funny: Optional[bool] = Field(
        json_schema_extra={"since": "v5.2.0"}, alias="isFunny", default=None
    )
    """If the card is part of a funny set."""

    is_online_only: Optional[bool] = Field(
        json_schema_extra={"since": "v4.0.1"}, alias="isOnlineOnly", default=None
    )
    """If the card is only available in online game variations."""

    is_oversized: Optional[bool] = Field(
        json_schema_extra={"since": "v4.0.0"}, alias="isOversized", default=None
    )
    """If the card is oversized."""

    is_promo: Optional[bool] = Field(
        json_schema_extra={"since": "v4.4.2"}, alias="isPromo", default=None
    )
    """If the card is a promotional printing."""

    is_rebalanced: Optional[bool] = Field(
        json_schema_extra={"since": "v5.2.0"}, alias="isRebalanced", default=None
    )
    """If the card is rebalanced for the Alchemy play format."""

    is_reprint: Optional[bool] = Field(
        json_schema_extra={"since": "v4.4.2"}, alias="isReprint", default=None
    )
    """If the card has been reprinted."""

    is_reserved: Optional[bool] = Field(
        json_schema_extra={"since": "v4.0.1"}, alias="isReserved", default=None
    )
    """If the card is on the Magic: The Gathering Reserved List."""

    is_starter: Optional[bool] = Field(
        json_schema_extra={"since": "v4.0.0"},
        alias="isStarter",
        deprecated=True,
        default=None,
    )
    """If the card is found in a starter deck such as Planeswalker/Brawl decks."""

    is_story_spotlight: Optional[bool] = Field(
        json_schema_extra={"since": "v4.4.2"}, alias="isStorySpotlight", default=None
    )
    """If the card is a Story Spotlight card."""

    is_textless: Optional[bool] = Field(
        json_schema_extra={"since": "v4.4.2"}, alias="isTextless", default=None
    )
    """If the card does not have a text box."""

    is_timeshifted: Optional[bool] = Field(
        json_schema_extra={"since": "v4.4.1"}, alias="isTimeshifted", default=None
    )
    """If the card is "timeshifted", a feature of certain sets where a card will have 
    a different frameVersion. """

    keywords: Optional[List[str]] = Field(
        json_schema_extra={"since": "v5.0.0"}, alias="keywords", default=None
    )
    """A list of keywords found on the card."""

    language: str = Field(json_schema_extra={"since": "v5.2.1"}, alias="language")
    """The language the card is printed in. Examples: "Ancient Greek", "Arabic", 
    "Chinese Simplified", "Chinese Traditional", "English" """

    layout: str = Field(json_schema_extra={"since": "v4.0.0"}, alias="layout")
    """The type of card layout. For a token card, this will be "token".
    Examples: "adventure", "aftermath", "art_series", "augment", "class"
    """

    leadership_skills: Optional[LeadershipSkills] = Field(
        json_schema_extra={"since": "v4.5.1"}, alias="leadershipSkills", default=None
    )
    """A list of formats the card is legal to be a commander in. See the Leadership 
    Skills Data Model. """

    legalities: Legalities = Field(
        json_schema_extra={"since": "v4.0.0"}, alias="legalities"
    )
    """A list of play formats the card the card is legal in. See the Legalities Data 
    Model. """

    life: Optional[str] = Field(
        json_schema_extra={"since": "v4.2.1"}, alias="life", default=None
    )
    """The starting life total modifier. A plus or minus character precedes an 
    integer. Used only on cards with "Vanguard" in its types. """

    loyalty: Optional[str] = Field(
        json_schema_extra={"since": "v4.0.0"}, alias="loyalty", default=None
    )
    """The starting loyalty value of the card. Used only on cards with "Planeswalker" 
    in its types. """

    mana_cost: Optional[str] = Field(
        json_schema_extra={"since": "v4.0.0"}, alias="manaCost", default=None
    )
    """The mana cost of the card wrapped in brackets for each value.
    Example: "{1}{B}" """

    mana_value: float = Field(json_schema_extra={"since": "v5.2.0"}, alias="manaValue")
    """The mana value of the card. Formally known as "converted mana cost"."""

    name: str = Field(json_schema_extra={"since": "v4.0.0"}, alias="name")
    """The name of the card. Cards with multiple faces, like "Split" and "Meld" cards 
    are given a delimiter. Example: "Wear // Tear" """

    number: str = Field(json_schema_extra={"since": "v4.0.0"}, alias="number")
    """The number of the card. Can be prefixed or suffixed with a * or other 
    characters for promotional sets. """

    original_printings: Optional[List[str]] = Field(
        json_schema_extra={"since": "v5.2.0"}, alias="originalPrintings", default=None
    )
    """A list of card UUID's to original printings of the card if this card is 
    somehow different from its original, such as rebalanced cards. """

    original_release_date: Optional[str] = Field(
        json_schema_extra={"since": "v5.1.0"}, alias="originalReleaseDate", default=None
    )
    """The original release date in ISO 8601 format for a 
    promotional card printed outside of a cycle window, such as Secret Lair Drop 
    promotions. """

    original_text: Optional[str] = Field(
        json_schema_extra={"since": "v4.0.0"}, alias="originalText", default=None
    )
    """The text on the card as originally printed."""

    original_type: Optional[str] = Field(
        json_schema_extra={"since": "v4.0.0"}, alias="originalType", default=None
    )
    """The type of the card as originally printed. Includes any supertypes and 
    subtypes. """

    other_face_ids: Optional[List[str]] = Field(
        json_schema_extra={"since": "v4.6.1"}, alias="otherFaceIds", default=None
    )
    """A list of card UUID's to this card's counterparts, such as transformed or 
    melded faces. """

    power: Optional[str] = Field(
        json_schema_extra={"since": "v4.0.0"}, alias="power", default=None
    )
    """The power of the card. """

    printings: Optional[List[str]] = Field(
        json_schema_extra={"since": "v4.0.0"}, alias="printings", default=None
    )
    """A list of set printing codes the card was printed in, formatted in uppercase."""

    promo_types: Optional[List[str]] = Field(
        json_schema_extra={"since": "v5.0.0"}, alias="promoTypes", default=None
    )
    """A list of promotional types for a card.
    Examples: "alchemy", "arenaleague", "boosterfun", "boxtopper", "brawldeck" """

    purchaseUrls: PurchaseUrls = Field(
        json_schema_extra={"since": "v4.4.0"}, alias="purchaseUrls"
    )
    """Links that navigate to websites where the card can be purchased. See the 
    Purchase Urls Data Model. """

    rarity: str = Field(json_schema_extra={"since": "v4.0.0"}, alias="rarity")
    """The card printing rarity. Rarity bonus relates to cards that have an alternate 
    availability in booster packs, while special relates to "Timeshifted" cards. 
    Examples: "bonus", "common", "mythic", "rare", "special" """

    related_cards: Optional[RelatedCards] = Field(
        json_schema_extra={"since": "5.2.1"}, alias="RelatedCards", default=None
    )
    """The related cards for this card. See the Related Cards Data Model."""

    rebalanced_printings: Optional[List[str]] = Field(
        json_schema_extra={"since": "v5.2.0"}, alias="rebalancedPrintings", default=None
    )
    """A list of card UUID's to printings that are rebalanced 
    versions of this card. """

    rulings: Optional[List[Rulings]] = Field(
        json_schema_extra={"since": "v4.0.0"}, alias="rulings", default=None
    )
    """The official rulings of the card. See the Rulings Data Model."""

    security_stamp: Optional[str] = Field(
        json_schema_extra={"since": "v5.2.0"}, alias="securityStamp", default=None
    )
    """The security stamp printed on the card.
    Examples: "acorn", "arena", "circle", "heart", "oval" """

    set_code: str = Field(json_schema_extra={"since": "v5.0.1"}, alias="setCode")
    """The set printing code that the card is from."""

    side: Optional[str] = Field(
        json_schema_extra={"since": "v4.1.0"}, alias="side", default=None
    )
    """The identifier of the card side. Used on cards with multiple faces on the same 
    card. Examples: "a", "b", "c", "d", "e" """

    signature: Optional[str] = Field(
        json_schema_extra={"since": "v5.2.0"}, alias="signature", default=None
    )
    """The name of the signature on the card."""

    subsets: Optional[List[str]] = Field(
        json_schema_extra={"since": "v5.2.1"}, alias="subsets", default=None
    )
    """The names of the subset printings a card is in. Used primarily on "Secret Lair 
    Drop" cards."""

    subtypes: List[str] = Field(json_schema_extra={"since": "v4.0.0"}, alias="subtypes")
    """A list of card subtypes found after em-dash.
    Examples:
    "Abian", "Adventure", "Advisor", "Aetherborn", "Ajani" """

    supertypes: List[str] = Field(
        json_schema_extra={"since": "v4.0.0"}, alias="supertypes"
    )
    """A list of card supertypes found before em-dash.
    Examples: "Basic", "Host", "Legendary", "Ongoing", "Snow" """

    text: Optional[str] = Field(
        json_schema_extra={"since": "v4.0.0"}, alias="text", default=None
    )
    """The rules text of the card."""

    toughness: Optional[str] = Field(
        json_schema_extra={"since": "v4.0.0"}, alias="toughness", default=None
    )
    """The toughness of the card."""

    type: str = Field(json_schema_extra={"since": "v4.0.0"}, alias="type")
    """The type of the card as visible, including any supertypes and subtypes."""

    types: List[str] = Field(json_schema_extra={"since": "v4.0.0"}, alias="types")
    """A list of all card types of the card, including Un‑sets and gameplay variants.
    Examples: "Artifact", "Card", "Conspiracy", "Creature", "Dragon" """

    uuid: UUID = Field(json_schema_extra={"since": "v4.0.0"}, alias="uuid")
    """The universal unique identifier (v5) generated by MTGJSON. Each entry is 
    unique. """

    variations: Optional[List[UUID]] = Field(
        json_schema_extra={"since": "v4.1.2"}, alias="variations", default=None
    )
    """A list of card UUID's of this card with alternate printings in the same set. 
    Excludes Un‑sets. """

    watermark: Optional[str] = Field(
        json_schema_extra={"since": "v4.0.0"}, alias="watermark", default=None
    )
    """The name of the watermark on the card.
    Examples: "abzan", "agentsofsneak", "arena", "atarka", "azorius" """


class CardSet(MtgJsonDocument):
    """
    The Card (Set) Data Model describes the properties of a single card in a ``Set``
    Data Model.
    """

    artist: Optional[str] = Field(
        json_schema_extra={"since": "v4.0.0"}, alias="artist", default=None
    )
    """The name of the artist that illustrated the card art."""

    ascii_name: Optional[str] = Field(
        json_schema_extra={"since": "v5.0.0"}, alias="asciiName", default=None
    )
    """The ASCII (Basic/128) code formatted card name with no 
    special unicode characters. """

    attraction_lights: Optional[List[str]] = Field(
        json_schema_extra={"since": "v5.2.1"}, alias="attractionLights", default=None
    )
    """A list of attraction lights found on a card, available only to cards printed in 
    certain Un-sets."""

    availability: List[str] = Field(
        json_schema_extra={"since": "v5.0.0"}, alias="availability"
    )
    """A list of the card's available printing types.
    Examples: "arena", "dreamcast", "mtgo", "paper", "shandalar"
    """

    booster_types: Optional[List[str]] = Field(
        json_schema_extra={"since": "v5.2.1"}, alias="boosterTypes", default=None
    )
    """A list of types this card is in a booster pack.
    Examples: "deck", "draft" """

    border_color: str = Field(
        json_schema_extra={"since": "v4.0.0"}, alias="borderColor"
    )
    """The color of the card border.
    Examples: "black", "borderless", "gold", "silver", "white" """

    card_parts: Optional[List[str]] = Field(
        json_schema_extra={"since": "v5.2.0"}, alias="cardParts", default=None
    )
    """A list of card names associated to this card, such as "Meld" card face names."""

    color_identity: List[str] = Field(
        json_schema_extra={"since": "v4.0.0"}, alias="colorIdentity"
    )
    """A list of all the colors found in manaCost, colorIndicator, and text.
    Examples: "B", "G", "R", "U", "W" """

    color_indicator: Optional[List[str]] = Field(
        json_schema_extra={"since": "v4.0.2"}, alias="colorIndicator", default=None
    )
    """A list of all the colors in the color indicator (The symbol prefixed to a 
    card's types). Examples: "B", "G", "R", "U", "W" """

    colors: List[str] = Field(json_schema_extra={"since": "v4.0.0"}, alias="colors")
    """A list of all the colors in manaCost and colorIndicator. Some cards may not 
    have values, such as cards with "Devoid" in its text. Examples: "B", "G", "R", 
    "U", "W" """

    converted_mana_cost: float = Field(
        json_schema_extra={"since": "v4.0.0"},
        alias="convertedManaCost",
        deprecated=True,
    )
    """The converted mana cost of the card. Use the manaValue property."""

    defense: Optional[str] = Field(
        json_schema_extra={"since": "v5.2.1"}, alias="defense", default=None
    )
    """The defense of the card. Used on battle cards."""

    edhrec_rank: Optional[int] = Field(
        json_schema_extra={"since": "v4.5.0"}, alias="edhrecRank", default=None
    )
    """The card rank on EDHRec."""

    edhrec_saltiness: Optional[float] = Field(
        json_schema_extra={"since": "v4.5.0"}, alias="edhrecSaltiness", default=None
    )
    """The card saltiness score on EDHRec."""

    face_converted_mana_cost: Optional[float] = Field(
        json_schema_extra={"since": "v4.1.1"},
        alias="faceConvertedManaCost",
        deprecated=True,
        default=None,
    )
    """The converted mana cost or mana value for the face for either half or part of 
    the card. Use the faceManaValue property. """

    face_flavor_name: Optional[str] = Field(
        json_schema_extra={"since": "v5.2.0"}, alias="faceFlavorName", default=None
    )
    """The flavor name on the face of the card."""

    face_mana_value: Optional[float] = Field(
        json_schema_extra={"since": "v5.2.0"}, alias="faceManaValue", default=None
    )
    """The mana value of the face for either half or part of the card. Formally known 
    as "converted mana cost". """

    face_name: Optional[str] = Field(
        json_schema_extra={"since": "v5.0.0"}, alias="faceName", default=None
    )
    """The name on the face of the card."""

    finishes: List[str] = Field(json_schema_extra={"since": "v5.2.0"}, alias="finishes")
    """The finishes of the card.
    Examples: "etched", "foil", "nonfoil", "signed" """

    flavor_name: Optional[str] = Field(
        json_schema_extra={"since": "v5.0.0"}, alias="flavorName", default=None
    )
    """The promotional card name printed above the true card name on special cards 
    that has no game function. See this card for an example. """

    flavor_text: Optional[str] = Field(
        json_schema_extra={"since": "v4.0.0"}, alias="flavorText", default=None
    )
    """The italicized text found below the rules text that has no game function."""

    foreign_data: List[ForeignData] = Field(
        json_schema_extra={"since": "v4.0.0"}, alias="foreignData"
    )
    """A list of data properties in other languages. See the Foreign Data Data Model."""

    frame_effects: Optional[List[str]] = Field(
        json_schema_extra={"since": "v4.6.0"}, alias="frameEffects", default=None
    )
    """The visual frame effects.
    Examples: "colorshifted", "companion", "compasslanddfc", "convertdfc", "devoid" """

    frame_version: str = Field(
        json_schema_extra={"since": "v4.0.0"}, alias="frameVersion"
    )
    """The version of the card frame style.
    Examples: "1993", "1997", "2003", "2015", "future" """

    hand: Optional[str] = Field(
        json_schema_extra={"since": "v4.2.1"}, alias="hand", default=None
    )
    """The starting maximum hand size total modifier. A + or - character precedes an 
    integer. """

    has_alternative_deck_limit: Optional[bool] = Field(
        json_schema_extra={"since": "v5.0.0"},
        alias="hasAlternativeDeckLimit",
        default=None,
    )
    """If the card allows a value other than 4 copies in a deck."""

    has_content_warning: Optional[bool] = Field(
        json_schema_extra={"since": "v5.0.0"}, alias="hasContentWarning", default=None
    )
    """If the card marked by Wiz""ards of the Coast for having 
    sensitive content. Cards with this property may have missing or degraded 
    properties and values. See this official article for more 
    information."" """

    has_foil: bool = Field(
        json_schema_extra={"since": "v4.0.0"}, alias="hasFoil", deprecated=True
    )
    """If the card can be found in foil. Use the finishes property."""

    has_non_foil: bool = Field(
        json_schema_extra={"since": "v4.0.0"}, alias="hasNonFoil", deprecated=True
    )
    """If the card can be found in non-foil. Use the finishes property."""

    identifiers: Identifiers = Field(
        json_schema_extra={"since": "v5.0.0"}, alias="identifiers"
    )
    """A list of identifiers associated to a card. See the Identifiers Data Model."""

    is_alternative: Optional[bool] = Field(
        json_schema_extra={"since": "v4.2.0"}, alias="isAlternative", default=None
    )
    """If the card is an alternate variation to an original printing."""

    is_full_art: Optional[bool] = Field(
        json_schema_extra={"since": "v4.4.2"}, alias="isFullArt", default=None
    )
    """If the card has full artwork."""

    is_funny: Optional[bool] = Field(
        json_schema_extra={"since": "v5.2.0"}, alias="isFunny", default=None
    )
    """If the card is part of a funny set."""

    is_online_only: Optional[bool] = Field(
        json_schema_extra={"since": "v4.0.1"}, alias="isOnlineOnly", default=None
    )
    """If the card is only available in online game variations."""

    is_oversized: Optional[bool] = Field(
        json_schema_extra={"since": "v4.0.0"}, alias="isOversized", default=None
    )
    """If the card is oversized."""

    is_promo: Optional[bool] = Field(
        json_schema_extra={"since": "v4.4.2"}, alias="isPromo", default=None
    )
    """If the card is a promotional printing."""

    is_rebalanced: Optional[bool] = Field(
        json_schema_extra={"since": "v5.2.0"}, alias="isRebalanced", default=None
    )
    """If the card is rebalanced for the Alchemy 
    play format. """

    is_reprint: Optional[bool] = Field(
        json_schema_extra={"since": "v4.4.2"}, alias="isReprint", default=None
    )
    """If the card has been reprinted."""

    is_reserved: Optional[bool] = Field(
        json_schema_extra={"since": "v4.0.1"}, alias="isReserved", default=None
    )
    """If the card is on the Magic: The Gathering Reserved List."""

    is_starter: Optional[bool] = Field(
        json_schema_extra={"since": "v4.0.0"}, alias="isStarter", default=None
    )
    """If the card is found in a starter deck such as Planeswalker/Brawl decks."""

    is_story_spotlight: Optional[bool] = Field(
        json_schema_extra={"since": "v4.4.2"}, alias="isStorySpotlight", default=None
    )
    """If the card is a Story Spotlight card."""

    is_textless: Optional[bool] = Field(
        json_schema_extra={"since": "v4.4.2"}, alias="isTextless", default=None
    )
    """If the card does not have a text box."""

    is_timeshifted: Optional[bool] = Field(
        json_schema_extra={"since": "v4.4.1"}, alias="isTimeshifted", default=None
    )
    """If the card is "timeshifted", a feature of certain sets where a card will have 
    a different frameVersion. """

    keywords: Optional[List[str]] = Field(
        json_schema_extra={"since": "v5.0.0"}, alias="keywords", default=None
    )
    """A list of keywords found on the card"""

    language: str = Field(json_schema_extra={"since": "v5.2.1"}, alias="language")
    """The language the card is printed in. Examples: "Ancient Greek", "Arabic", 
    "Chinese Simplified", "Chinese Traditional", "English" """

    layout: str = Field(json_schema_extra={"since": "v4.0.0"}, alias="layout")
    """The type of card layout. For a token card, this will be "token".
    Examples: "adventure", "aftermath", "art_series", "augment", "class" """

    leadershipSkills: Optional[LeadershipSkills] = Field(
        json_schema_extra={"since": "v4.5.1"}, alias="leadershipSkills", default=None
    )
    """A list of formats the card is legal to be a commander in. See the Leadership 
    Skills Data Model. """

    legalities: Legalities = Field(
        json_schema_extra={"since": "v4.0.0"}, alias="legalities"
    )
    """A list of play formats the card the card is legal in. See the Legalities Data 
    Model. """

    life: Optional[str] = Field(
        json_schema_extra={"since": "v4.2.1"}, alias="life", default=None
    )
    """The starting life total modifier. A plus or minus character precedes an 
    integer. Used only on cards with "Vanguard" in its types. """

    loyalty: Optional[str] = Field(
        json_schema_extra={"since": "v4.0.0"}, alias="loyalty", default=None
    )
    """The starting loyalty value of the card. Used only on cards with "Planeswalker" 
    in its types. """

    mana_cost: Optional[str] = Field(
        json_schema_extra={"since": "v4.0.0"}, alias="manaCost", default=None
    )
    """The mana cost of the card wrapped in brackets for each value.
    Example: "{1}{B}" """

    mana_value: float = Field(json_schema_extra={"since": "v5.2.0"}, alias="manaValue")
    """The mana value of the card. Formally known as "converted mana cost"."""

    name: str = Field(json_schema_extra={"since": "v4.0.0"}, alias="name")
    """The name of the card. Cards with multiple faces, like "Split" and "Meld" cards 
    are given a delimiter of //. Example: "Wear // Tear" """

    number: str = Field(json_schema_extra={"since": "v4.0.0"}, alias="number")
    """The number of the card. Can be prefixed or suffixed with a * or other 
    characters for promotional sets. """

    original_printings: Optional[List[str]] = Field(
        json_schema_extra={"since": "v5.2.0"}, alias="originalPrintings", default=None
    )
    """A list of card UUID's to original printings of the card if this card is 
    somehow different from its original, such as rebalanced cards. """

    original_release_date: Optional[str] = Field(
        json_schema_extra={"since": "v5.1.0"}, alias="originalReleaseDate", default=None
    )
    """The original release date in ISO 8601 format for a promotional card printed 
    outside of a cycle window, such as Secret Lair Drop promotions. """

    original_text: Optional[str] = Field(
        json_schema_extra={"since": "v4.0.0"}, alias="originalText", default=None
    )
    """The text on the card as originally printed."""

    original_type: Optional[str] = Field(
        json_schema_extra={"since": "v4.0.0"}, alias="originalType", default=None
    )
    """The type of the card as originally printed. Includes any supertypes and 
    subtypes. """

    other_face_ids: Optional[List[str]] = Field(
        json_schema_extra={"since": "v4.6.1"}, alias="otherFaceIds", default=None
    )
    """A list of card UUID's to this card's counterparts, such as transformed or 
    melded faces. """

    power: Optional[str] = Field(
        json_schema_extra={"since": "v4.0.0"}, alias="power", default=None
    )
    """The power of the card."""

    printings: Optional[List[str]] = Field(
        json_schema_extra={"since": "v4.0.0"}, alias="printings", default=None
    )
    """A list of set printing codes the card was printed in, formatted in uppercase."""

    promo_types: Optional[List[str]] = Field(
        json_schema_extra={"since": "v5.0.0"}, alias="promoTypes", default=None
    )
    """A list of promotional types for a card.
    Examples: "alchemy", "arenaleague", "boosterfun", "boxtopper", "brawldeck"
    """

    purchase_urls: PurchaseUrls = Field(
        json_schema_extra={"since": "v4.4.0"}, alias="purchaseUrls"
    )
    """Links that navigate to websites where the card can be purchased. See the 
    Purchase Urls Data Model. """

    rarity: str = Field(json_schema_extra={"since": "v4.0.0"}, alias="rarity")
    """The card printing rarity. Rarity bonus relates to cards that have an alternate 
    availability in booster packs, while special relates to "Timeshifted" cards. 
    Examples: "bonus", "common", "mythic", "rare", "special" """

    rebalanced_printings: Optional[List[UUID]] = Field(
        json_schema_extra={"since": "v5.2.0"}, alias="rebalancedPrintings", default=None
    )
    """A list of card UUID's to printings that are rebalanced versions of this card."""

    related_cards: Optional[RelatedCards] = Field(
        json_schema_extra={"since": "v5.2.1"}, alias="relatedCards", default=None
    )
    """The related cards for this card. See the Related Cards Data Model."""

    rulings: Optional[List[Rulings]] = Field(
        json_schema_extra={"since": "v4.0.0"}, alias="rulings", default=None
    )
    """The official rulings of the card. See the Rulings Data Model."""

    security_stamp: Optional[str] = Field(
        json_schema_extra={"since": "v5.2.0"}, alias="securityStamp", default=None
    )
    """The security stamp printed on the card.
    Examples: "acorn", "arena", "circle", "heart", "oval" """

    set_code: str = Field(json_schema_extra={"since": "v5.0.1"}, alias="setCode")
    """The set printing code that the card is from."""

    side: Optional[str] = Field(
        json_schema_extra={"since": "v4.1.0"}, alias="side", default=None
    )
    """The identifier of the card side. Used on cards with multiple faces on the same 
    card. Examples: "a", "b", "c", "d", "e" """

    signature: Optional[str] = Field(
        json_schema_extra={"since": "v5.2.0"}, alias="signature", default=None
    )
    """The name of the signature on the card."""

    subsets: Optional[List[str]] = Field(
        json_schema_extra={"since": "v5.2.1"}, alias="subsets", default=None
    )
    """The names of the subset printings a card is in. Used primarily on "Secret Lair 
    Drop" cards."""

    subtypes: List[str] = Field(json_schema_extra={"since": "v4.0.0"}, alias="subtypes")
    """A list of card subtypes found after em-dash.
    Examples: "Abian", "Adventure", "Advisor", "Aetherborn", "Ajani" """

    supertypes: List[str] = Field(
        json_schema_extra={"since": "v4.0.0"}, alias="supertypes"
    )
    """A list of card supertypes found before em-dash.
    Examples: "Basic", "Host", "Legendary", "Ongoing", "Snow" """

    text: Optional[str] = Field(
        json_schema_extra={"since": "v4.0.0"}, alias="text", default=None
    )
    """The rules text of the card."""

    toughness: Optional[str] = Field(
        json_schema_extra={"since": "v4.0.0"}, alias="toughness", default=None
    )
    """The toughness of the card."""

    type: str = Field(json_schema_extra={"since": "v4.0.0"}, alias="type")
    """Type of the card as visible, including any supertypes and subtypes."""

    types: List[str] = Field(json_schema_extra={"since": "v4.0.0"}, alias="types")
    """A list of all card types of the card, including Un‑sets and gameplay variants.
    Examples: "Artifact", "Card", "Conspiracy", "Creature", "Dragon" """

    uuid: UUID = Field(json_schema_extra={"since": "v4.0.0"}, alias="uuid")
    """The universal unique identifier (v5) generated by MTGJSON. Each entry is 
    unique. """

    variations: Optional[List[UUID]] = Field(
        json_schema_extra={"since": "v4.1.2"}, alias="variations", default=None
    )
    """A list of card UUID's of this card with alternate printings in the same set. 
    Excludes Un‑sets. """

    watermark: Optional[str] = Field(
        json_schema_extra={"since": "v4.0.0"}, alias="watermark", default=None
    )
    """The name of the watermark on the card.
    Examples: "abzan", "agentsofsneak", "arena", "atarka", "azorius" """


class CardToken(MtgJsonDocument):
    artist: Optional[str] = Field(
        json_schema_extra={"since": "v4.0.0"}, alias="artist", default=None
    )
    """The name of the artist that illustrated the card art."""

    ascii_name: Optional[str] = Field(
        json_schema_extra={"since": "v5.0.0"}, alias="asciiName", default=None
    )
    """The ASCII (Basic/128) code formatted card name with no special unicode 
    characters. """

    availability: List[str] = Field(
        json_schema_extra={"since": "v5.0.0"}, alias="availability"
    )
    """A list of the card's available printing types.
    Examples: "arena", "dreamcast", "mtgo", "paper", "shandalar" """

    booster_types: Optional[List[str]] = Field(
        json_schema_extra={"since": "v5.2.1"}, alias="boosterTypes", default=None
    )
    """A list of types this card is in a booster pack.
    Examples: "deck", "draft" """

    border_color: str = Field(
        json_schema_extra={"since": "v4.0.0"}, alias="borderColor"
    )
    """The color of the card border.
    Examples: "black", "borderless", "gold", "silver", "white" """

    card_parts: Optional[List[str]] = Field(
        json_schema_extra={"since": "v5.2.0"}, alias="cardParts", default=None
    )
    """A list of card names associated to this card, such as "Meld" card face names."""

    color_identity: List[str] = Field(
        json_schema_extra={"since": "v4.0.0"}, alias="colorIdentity"
    )
    """A list of all the colors found in manaCost, colorIndicator, and text.
    Examples: "B", "G", "R", "U", "W" """

    color_indicator: Optional[List[str]] = Field(
        json_schema_extra={"since": "v4.0.2"}, alias="colorIndicator", default=None
    )
    """A list of all the colors in the color indicator (The symbol prefixed to a 
    card's types). Examples: "B", "G", "R", "U", "W" """

    colors: List[str] = Field(json_schema_extra={"since": "v4.0.0"}, alias="colors")
    """A list of all the colors in manaCost and colorIndicator. Some cards may not 
    have values, such as cards with "Devoid" in its text. Examples: "B", "G", "R", 
    "U", "W" """

    face_name: Optional[str] = Field(
        json_schema_extra={"since": "v5.0.0"}, alias="faceName", default=None
    )
    """The name on the face of the card."""

    face_flavor_name: Optional[str] = Field(
        json_schema_extra={"since": "v5.2.0"}, alias="faceFlavorName", default=None
    )
    """The flavor name on the face of the card."""

    finishes: List[str] = Field(json_schema_extra={"since": "v5.2.0"}, alias="finishes")
    """The finishes of the card.
    Examples: "etched", "foil", "nonfoil", "signed" """

    flavor_text: Optional[str] = Field(
        json_schema_extra={"since": "v4.0.0"}, alias="flavorText", default=None
    )
    """The italicized text found below the rules text that has no game function."""

    frame_effects: Optional[List[str]] = Field(
        json_schema_extra={"since": "v4.6.0"}, alias="frameEffects", default=None
    )
    """The visual frame effects.
    Examples: "colorshifted", "companion", "compasslanddfc", "convertdfc", "devoid" """

    frame_version: str = Field(
        json_schema_extra={"since": "v4.0.0"}, alias="frameVersion"
    )
    """The version of the card frame style.
    Examples: "1993", "1997", "2003", "2015", "future" """

    has_foil: bool = Field(
        json_schema_extra={"since": "v4.0.0"}, alias="hasFoil", deprecated=True
    )
    """If the card can be found in foil. Use the finishes property."""

    has_non_foil: bool = Field(
        json_schema_extra={"since": "v4.0.0"}, alias="hasNonFoil", deprecated=True
    )
    """If the card can be found in non-foil. Use the finishes property."""

    identifiers: Identifiers = Field(
        json_schema_extra={"since": "v5.0.0"}, alias="identifiers"
    )
    """A list of identifiers associated to a card. See the Identifiers Data Model."""

    is_full_art: Optional[bool] = Field(
        json_schema_extra={"since": "v4.4.2"}, alias="isFullArt", default=None
    )
    """If the card has full artwork."""

    is_funny: Optional[bool] = Field(
        json_schema_extra={"since": "v5.2.0"}, alias="isFunny", default=None
    )
    """If the card is part of a funny set."""

    is_online_only: Optional[bool] = Field(
        json_schema_extra={"since": "v4.0.1"}, alias="isOnlineOnly", default=None
    )
    """If the card is only available in online game variations."""

    is_promo: Optional[bool] = Field(
        json_schema_extra={"since": "v4.4.2"}, alias="isPromo", default=None
    )
    """If the card is a promotional printing."""

    is_reprint: Optional[bool] = Field(
        json_schema_extra={"since": "v4.4.2"}, alias="isReprint", default=None
    )
    """If the card has been reprinted."""

    keywords: Optional[List[str]] = Field(
        json_schema_extra={"since": "v5.0.0"}, alias="keywords", default=None
    )
    """A list of keywords found on the card."""

    language: str = Field(json_schema_extra={"since": "v5.2.1"}, alias="language")
    """The language the card is printed in. Examples: "Ancient Greek", "Arabic", 
    "Chinese Simplified", "Chinese Traditional", "English" """

    layout: str = Field(json_schema_extra={"since": "v4.0.0"}, alias="layout")
    """The type of card layout. For a token card, this will be "token".
    Examples: "adventure", "aftermath", "art_series", "augment", "class" """

    loyalty: Optional[str] = Field(
        json_schema_extra={"since": "v4.0.0"}, alias="loyalty", default=None
    )
    """The starting loyalty value of the card. Used only on cards with "Planeswalker" 
    in its types. """

    name: str = Field(json_schema_extra={"since": "v4.0.0"}, alias="name")
    """The name of the card. Cards with multiple faces, like "Split" and "Meld" cards 
    are given a delimiter. Example: "Wear // Tear" """

    number: str = Field(json_schema_extra={"since": "v4.0.0"}, alias="number")
    """The number of the card. Can be prefixed or suffixed with a * or other 
    characters for promotional sets. """

    orientation: Optional[str] = Field(
        json_schema_extra={"since": "v5.2.1"}, alias="orientation", default=None
    )
    """The orientation of the card."""

    other_face_ids: Optional[List[str]] = Field(
        json_schema_extra={"since": "v4.6.1"}, alias="otherFaceIds", default=None
    )
    """A list of card UUID's to this card's counterparts, such as transformed or 
    melded faces. """

    power: Optional[str] = Field(
        json_schema_extra={"since": "v4.0.0"}, alias="power", default=None
    )
    """The power of the card."""

    promo_types: Optional[List[str]] = Field(
        json_schema_extra={"since": "v5.0.0"}, alias="promoTypes", default=None
    )
    """A list of promotional types for a card.
    Examples: "alchemy", "arenaleague", "boosterfun", "boxtopper", "brawldeck" """

    related_cards: RelatedCards = Field(
        json_schema_extra={"since": "v5.2.1"}, alias="relatedCards"
    )
    """The related cards for this card. See the Related Cards Data Model."""

    reverse_related: List[str] = Field(
        json_schema_extra={"since": "v4.0.0"}, alias="reverseRelated", deprecated="True"
    )
    """The names of the cards that produce this card."""

    security_stamp: Optional[str] = Field(
        json_schema_extra={"since": "v5.2.0"}, alias="securityStamp", default=None
    )
    """The security stamp printed on the card.
    Examples: "acorn", "arena", "circle", "heart", "oval" """

    set_code: str = Field(json_schema_extra={"since": "v5.0.1"}, alias="setCode")
    """The set printing code that the card is from."""

    side: Optional[str] = Field(
        json_schema_extra={"since": "v4.1.0"}, alias="side", default=None
    )
    """The identifier of the card side. Used on cards with multiple faces on the same 
    card. Examples: "a", "b", "c", "d", "e" """

    signature: Optional[str] = Field(
        json_schema_extra={"since": "v5.2.0"}, alias="signature", default=None
    )
    """The name of the signature on the card."""

    subsets: Optional[List[str]] = Field(
        json_schema_extra={"since": "v4.0.0"}, alias="subsets", default=None
    )
    """The names of the subset printings a card is in. Used primarily on "Secret Lair 
    Drop" cards."""

    subtypes: List[str] = Field(json_schema_extra={"since": "v4.0.0"}, alias="subtypes")
    """A list of card subtypes found after em-dash.
    Examples: "Abian", "Adventure", "Advisor", "Aetherborn", "Ajani" """

    supertypes: List[str] = Field(
        json_schema_extra={"since": "v4.0.0"}, alias="supertypes"
    )
    """A list of card supertypes found before em-dash.
    Examples: "Basic", "Host", "Legendary", "Ongoing", "Snow" """

    text: Optional[str] = Field(
        json_schema_extra={"since": "v4.0.0"}, alias="text", default=None
    )
    """The rules text of the card."""

    toughness: Optional[str] = Field(
        json_schema_extra={"since": "v4.0.0"}, alias="toughness", default=None
    )
    """The toughness of the card."""

    type: str = Field(json_schema_extra={"since": "v4.0.0"}, alias="type")
    """The type of the card as visible, including any supertypes and subtypes."""

    types: List[str] = Field(json_schema_extra={"since": "v4.0.0"}, alias="types")
    """A list of all card types of the card, including Un‑sets and gameplay variants.
    Examples: "Artifact", "Card", "Conspiracy", "Creature", "Dragon" """

    uuid: UUID = Field(json_schema_extra={"since": "v4.0.0"}, alias="uuid")
    """The universal unique identifier (v5) generated by MTGJSON. Each entry is 
    unique. """

    watermark: Optional[str] = Field(
        json_schema_extra={"since": "v4.0.0"}, alias="watermark", default=None
    )
    """The name of the watermark on the card.
    Examples: "abzan", "agentsofsneak", "arena", "atarka", "azorius" """


class Deck(MtgJsonDocument):
    """
    The Deck Data Model describes a complete deck reference.
    """

    code: str = Field(json_schema_extra={"since": "v4.3.0"}, alias="code")
    """The set code for the deck."""

    file_name: Optional[str] = Field(
        json_schema_extra={"since": "v4.3.0"}, alias="fileName", default=None
    )
    """The file name for the deck. Combines the name and code fields to avoid 
    namespace collisions and are given a delimiter of _. Examples: 
    "SpiritSquadron_VOC" """

    name: str = Field(json_schema_extra={"since": "v4.3.0"}, alias="name")
    """The name of the deck."""

    release_date: Optional[datetime.date] = Field(
        json_schema_extra={"since": "v4.3.0"}, alias="releaseDate", default=None
    )
    """The release date in ISO 8601 format for the set. Returns 
    null if the set was not formally released as a product. """

    type: str = Field(json_schema_extra={"since": "v4.3.0"}, alias="type")
    """The type of deck. Examples: "Advanced Deck", "Advanced Pack", "Archenemy 
    Deck", "Basic Deck", "Brawl Deck" """

    commander: Optional[List[CardDeck]] = Field(
        json_schema_extra={"since": "v5.1.0"}, alias="commander", default=None
    )
    """The card that is the Commander in this deck. See the Card (Deck) Data Model."""

    main_board: List[CardDeck] = Field(
        json_schema_extra={"since": "v4.3.0"}, alias="mainBoard"
    )
    """The cards in the main-board. See the Card (Deck) Data Model."""

    side_board: List[CardDeck] = Field(
        json_schema_extra={"since": "v4.3.0"}, alias="sideBoard"
    )
    """The cards in the side-board. See the Card (Deck) Data Model."""


class Set(MtgJsonDocument):
    base_set_size: int = Field(
        json_schema_extra={"since": "v4.1.0"}, alias="baseSetSize"
    )
    """The number of cards in the set. This will default to totalSetSize if not 
    available. Wizards of the Coast sometimes prints extra cards 
    beyond the set size into promos or supplemental products. """

    block: Optional[str] = Field(
        json_schema_extra={"since": "v4.0.0"}, alias="block", default=None
    )
    """The block name the set was in."""

    booster: Optional[dict] = Field(
        json_schema_extra={"since": "v5.0.0"}, alias="booster", default=None
    )
    """A breakdown of possibilities and weights of cards in a booster pack. See the 
    Booster abstract model. """

    cards: List[CardSet] = Field(json_schema_extra={"since": "v4.0.0"}, alias="cards")
    """The list of cards in the set. See the Card (Set) Data Model."""

    cardsphere_set_id: Optional[int] = Field(
        json_schema_extra={"since": "v5.2.1"}, alias="cardsphereSetId", default=None
    )
    """The Cardsphere set identifier."""

    code: str = Field(json_schema_extra={"since": "v4.0.0"}, alias="code")
    """The set code for the set."""

    code_v3: Optional[str] = Field(
        json_schema_extra={"since": "v4.2.1"}, alias="codeV3", default=None
    )
    """The alternate set code Wizards of the Coast uses for a select few duel deck 
    sets. """

    is_foreign_only: Optional[bool] = Field(
        json_schema_extra={"since": "v4.4.1"}, alias="isForeignOnly", default=None
    )
    """If the set is available only outside the United States of America."""

    is_foil_only: bool = Field(
        json_schema_extra={"since": "v4.0.0"}, alias="isFoilOnly"
    )
    """If the set is only available in foil."""

    is_non_foil_only: Optional[bool] = Field(
        json_schema_extra={"since": "v5.0.0"}, alias="isNonFoilOnly", default=None
    )
    """If the set is only available in non-foil."""

    is_online_only: bool = Field(
        json_schema_extra={"since": "v4.0.0"}, alias="isOnlineOnly"
    )
    """If the set is only available in online game variations."""

    is_paper_only: Optional[bool] = Field(
        json_schema_extra={"since": "v4.6.2"}, alias="isPaperOnly", default=None
    )
    """If the set is available only in paper."""

    is_partial_preview: Optional[bool] = Field(
        json_schema_extra={"since": "v4.4.2"}, alias="isPartialPreview", default=None
    )
    """If the set is still in preview (spoiled). Preview sets do not have complete 
    data. """

    keyrune_code: str = Field(
        json_schema_extra={"since": "v4.3.2"}, alias="keyruneCode"
    )
    """The matching Keyrune code for set image icons."""

    languages: List[str] = Field(
        json_schema_extra={"since": "v5.2.1"}, alias="languages"
    )
    """The languages the set was printed in."""

    mcm_id: Optional[int] = Field(
        json_schema_extra={"since": "v4.4.0"}, alias="mcmId", default=None
    )
    """The Magic Card Market set identifier."""

    mcm_id_extras: Optional[int] = Field(
        json_schema_extra={"since": "v5.1.0"}, alias="mcmIdExtras", default=None
    )
    """The split Magic Card Market set identifier if a set is printed in two sets. 
    This identifier represents the second set's identifier. """

    mcm_name: Optional[str] = Field(
        json_schema_extra={"since": "v4.4.0"}, alias="mcmName", default=None
    )
    """The Magic Card Market set name."""

    mtgo_code: Optional[str] = Field(
        json_schema_extra={"since": "v4.0.0"}, alias="mtgoCode", default=None
    )
    """The set code for the set as it appears on Magic: The Gathering Online."""

    name: str = Field(json_schema_extra={"since": "v4.0.0"}, alias="name")
    """The name of the set."""

    parent_code: Optional[str] = Field(
        json_schema_extra={"since": "v4.3.0"}, alias="parentCode", default=None
    )
    """The parent set code for set variations like promotions, guild kits, etc."""

    release_date: datetime.date = Field(
        json_schema_extra={"since": "v4.0.0"}, alias="releaseDate"
    )
    """The release date in ISO 8601 format for the set."""

    sealed_product: Optional[List[SealedProduct]] = Field(
        json_schema_extra={"since": "v5.2.0"}, alias="sealedProduct"
    )
    """The sealed product information for the set. See the Sealed Product Data Model."""

    tcgplayer_group_id: Optional[int] = Field(
        json_schema_extra={"since": "v4.2.1"}, alias="tcgplayerGroupId", default=None
    )
    """The group identifier of the set on TCGplayer."""

    tokens: List[CardToken] = Field(
        json_schema_extra={"since": "v4.0.0"}, alias="tokens"
    )
    """The tokens available to the set. See the Card (Token) Data Model."""

    token_set_code: Optional[str] = Field(
        json_schema_extra={"since": "v5.2.1"}, alias="tokenSetcode", default=None
    )
    """The tokens set code, formatted in uppercase."""

    total_set_size: int = Field(
        json_schema_extra={"since": "v4.1.0"}, alias="totalSetSize"
    )
    """The total number of cards in the set, including promotional and related 
    supplemental products but excluding Alchemy modifications - however those cards 
    are included in the set itself. """

    translations: Translations = Field(
        json_schema_extra={"since": "v4.3.2"}, alias="translations"
    )
    """The translated set name by language. See the Translations Data Model."""

    type: str = Field(json_schema_extra={"since": "v4.0.0"}, alias="type")
    """The expansion type of the set.
    Examples: "alchemy", "archenemy", "arsenal", "box", "commander" """


class SetList(MtgJsonDocument):
    """
    The Set List Data Model describes a metadata-like properties and values for an
    individual Set.
    """

    baseSetSize: int = Field(json_schema_extra={"since": "v4.1.0"}, alias="baseSetSize")
    """The number of cards in the set. This will default to totalSetSize if not 
    available. Wizards of the Coast sometimes prints extra cards beyond the set size 
    into promos or supplemental products. """

    block: Optional[str] = Field(
        json_schema_extra={"since": "v4.0.0"}, alias="block", default=None
    )
    """The block name the set was in."""

    code: str = Field(json_schema_extra={"since": "v4.0.0"}, alias="code")
    """The set code for the set."""

    code_v3: Optional[str] = Field(
        json_schema_extra={"since": "v4.2.1"}, alias="codeV3", default=None
    )
    """The alternate set code Wizards of the Coast uses for a select few duel deck 
    sets. """

    is_foreign_only: Optional[bool] = Field(
        json_schema_extra={"since": "v4.4.1"}, alias="isForeignOnly", default=None
    )
    """If the set is available only outside the United States of America."""

    is_foil_only: bool = Field(
        json_schema_extra={"since": "v4.0.0"}, alias="isFoilOnly"
    )
    """If the set is only available in foil."""

    is_non_foil_only: Optional[bool] = Field(
        json_schema_extra={"since": "v5.0.0"}, alias="isNonFoilOnly", default=None
    )
    """If the set is only available in non-foil."""

    is_online_only: bool = Field(
        json_schema_extra={"since": "v4.0.0"}, alias="isOnlineOnly"
    )
    """If the set is only available in online game variations."""

    is_paper_only: Optional[bool] = Field(
        json_schema_extra={"since": "v4.6.2"}, alias="isPaperOnly", default=None
    )
    """If the set is only available in paper."""

    is_partial_preview: Optional[bool] = Field(
        json_schema_extra={"since": "v4.4.2"}, alias="isPartialPreview", default=None
    )
    """If the set is still in preview (spoiled). Preview sets do not have complete
    data. """

    keyrune_code: str = Field(
        json_schema_extra={"since": "v4.3.2"}, alias="keyruneCode"
    )
    """The matching Keyrune code for set image icons."""

    mcm_id: Optional[int] = Field(
        json_schema_extra={"since": "v4.4.0"}, alias="mcmId", default=None
    )
    """The Magic Card Market set identifier."""

    mcm_id_extras: Optional[int] = Field(
        json_schema_extra={"since": "v5.1.0"}, alias="mcmIdExtras", default=None
    )
    """The split Magic Card Market set identifier if a set is printed in two sets.
    This identifier represents the second set's identifier. """

    mcm_name: Optional[str] = Field(
        json_schema_extra={"since": "v4.4.0"}, alias="mcmName", default=None
    )
    """The Magic Card Market set name."""

    mtgo_code: Optional[str] = Field(
        json_schema_extra={"since": "v4.0.0"}, alias="mtgoCode", default=None
    )
    """The set code for the set as it appears on Magic: The Gathering Online."""

    name: str = Field(json_schema_extra={"since": "v4.0.0"}, alias="name")
    """The name of the set."""

    parent_code: Optional[str] = Field(
        json_schema_extra={"since": "v4.3.0"}, alias="parentCode", default=None
    )
    """The parent set code for set variations like promotions, guild kits, etc."""

    release_date: datetime.date = Field(
        json_schema_extra={"since": "v4.0.0"}, alias="releaseDate"
    )
    """The release date in ISO 8601 format for the set."""

    sealed_product: Optional[List[SealedProduct]] = Field(
        json_schema_extra={"since": "v5.1.0"}, alias="sealedProduct", default=None
    )
    """The sealed product information for the set. See the Sealed Product Data Model."""

    tcgplayer_group_id: Optional[int] = Field(
        json_schema_extra={"since": "v4.2.1"}, alias="tcgplayerGroupId", default=None
    )
    """The group identifier of the set on TCGplayer."""

    total_set_size: int = Field(
        json_schema_extra={"since": "v4.1.0"}, alias="totalSetSize"
    )
    """The total number of cards in the set, including promos and related
    supplemental products. """

    translations: Translations = Field(
        json_schema_extra={"since": "v4.3.2"}, alias="translations"
    )
    """The translated set name by language. See the Translations Data Model."""

    type: str = Field(json_schema_extra={"since": "v4.0.0"}, alias="type")
    """The expansion type of the set.
    Examples: "alchemy", "archenemy", "arsenal", "box", "commander" """


class Card(RootModel):
    """
    A card either a Card from a set, or a token
    """


class RetailPrices(MightstoneModel):
    buylist: Optional[Dict[str, Dict[str, float]]] = None
    currency: str
    retail: Optional[Dict[str, Dict[str, float]]] = None


class CardPrices(MtgJsonDocument):
    """
    A representation of the abstract model for card prices in MTGJSON
    """

    uuid: UUID
    mtgo: Optional[Dict[str, RetailPrices]] = None
    paper: Optional[Dict[str, RetailPrices]] = None


class CardAtomic(MtgJsonDocument):
    """
    A representation of a group of Atomic Card such as returned by every _atomic
    methods of MtgJson client
    """

    ascii_name: str = Field(alias="asciiName")
    """The ASCII (Basic/128) code formatted card name with no 
    special unicode characters. """

    faces: List[CardFace]


class TcgPlayerSKUs(MtgJsonDocument):
    """
    A representation of a TcgPlayerSKU list associated to a card unique ID
    """

    uuid: UUID = Field(alias="uuid")  # type: ignore
    skus: List[TcgPlayerSKU]

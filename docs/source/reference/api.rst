.. _reference-index:

API Reference
=============

EDHREC
------

**EDHREC** is a reference database for EDH and cEDH. It provides a small REST-like, and a lot of static json files that were reverse engineered in order to provide a pydantic model.

Static API
~~~~~~~~~~

There are two distinct API:
 * ``EdhRecStatic`` direct static access from https://json.edhrec.com/page, faster but incomplete support
 * ``EdhRecProxiedStatic`` proxified static access from https://edhrec.com/_next/data, slower but similar to frontend users

.. list-table::
   :header-rows: 1

   * - Feature
     - Support
   * - Top Cards (by color, by salt, by type)
     - ✅
   * - Combos
     - ✅
   * - Card in set
     - ✅
   * - Themes
     - ✅
   * - Typals (tribes)
     - ✅
   * - Card Migrations
     - ✅
   * - Decks (average, listing)
     - ✅
   * - Invidivual decks
     - 🔸(only in proxified mode)

.. autoclass:: mightstone.services.edhrec.EdhRecStatic
   :members:

.. autoclass:: mightstone.services.edhrec.EdhRecProxiedStatic
   :members:
   :inherited-members: BaseModel


Dynamic API
~~~~~~~~~~~

.. list-table::
   :header-rows: 1
   * - Feature
     - Support
   * - Recommendation
     - ✅
   * - Dynamic filters for commander
     - ✅

.. autoclass:: mightstone.services.edhrec.EdhRecApi
   :members:


Models
~~~~~~

.. currentmodule:: mightstone.services.edhrec.models

.. autosummary::
   :toctree: _autosummary

    PageAverageDeck
    PageBackground
    PageBackgrounds
    PageCard
    PageCombo
    PageCombos
    PageCommander
    PageCommanders
    PageCompanions
    PageDeck
    PageDecks
    PageManaStaples
    PagePartner
    PagePartners
    PageSalts
    PageSet
    PageSets
    PageStaples
    PageTheme
    PageThemes
    PageTopCards
    PageTypal
    PageTypals

Scryfall
--------

**Scryfall** is a search engine for magic cards. It provides a REST-like API for ingesting our card data programatically. The API exposes information available on the regular site in easy-to-consume formats.


.. list-table::
   :header-rows: 1

   * - Feature
     - Support
   * - Cards
     - ✅
   * - Sets
     - ✅
   * - Rulings
     - ✅
   * - Card Symbols
     - ✅
   * - Bulk Data
     - ✅ (fully async)
   * - Card Migrations
     - ✅
   * - Application
     - ❌

Scryfall Client
~~~~~~~~~~~~~~~

.. autoclass:: mightstone.services.scryfall.Scryfall
   :members:


Models
~~~~~~

.. currentmodule:: mightstone.services.scryfall.models

.. autosummary::
   :toctree: _autosummary

    BulkTagType
    Card
    CardFace
    Catalog
    ManaCost
    Migration
    Preview
    Ruling
    Set
    Symbol
    Tag



MTGJSON
-------

**MTGJSON** is an open-source project that catalogs all Magic: The Gathering data in portable formats. Using an aggregation process we fetch information between multiple resources and approved partners, and combine all that data in to various downloadable formats.

.. list-table::
   :header-rows: 1

   * - Feature
     - Support
   * - JSON data
     - ✅
   * - Compressed JSON data
     - ✅ (except zip)
   * - SQLite data
     - ❌
   * - CSV data
     - ❌
   * - GraphQL API
     - ❌

MtgJson Client
~~~~~~~~~~~~~~

.. autoclass:: mightstone.services.mtgjson.MtgJson
   :members:

Models
~~~~~~

.. currentmodule:: mightstone.services.mtgjson.models

.. autosummary::
   :toctree: _autosummary

   Card
   Set
   SetList
   Meta
   Keywords
   Deck
   DeckList
   CardTypes


Card Conjurer
-------------

`Card Conjurer <https://cardconjurer.com>`_ is a card editor service that provides a unique file format to describe a card image. Each card is described in a JSON file that extends a template. Template may vary from MTG copycat to brand new card frame.

.. list-table::
   :header-rows: 1

   * - Feature
     - Support
   * - Template
     - ✅ (read-only)
   * - Card
     - ✅ (read-only)
   * - Card Generation
     - 🟠 Working for the most part, but inline symbols are not supported

.. list-table::

    * - .. figure:: ./cardconjurer.sample.png

           Fig 1. Card Conjurer generated image

      - .. figure:: ./cardconjurer.mightstone.png

           Fig 2. Mightstone generated image


CardConjurer Client
~~~~~~~~~~~~~~~~~~~

.. autoclass:: mightstone.services.cardconjurer.CardConjurer
   :members:

Models
~~~~~~

.. currentmodule:: mightstone.services.cardconjurer.models

.. autosummary::
   :toctree: _autosummary
   :recursive:

   Card
   Template
   Image
   Text
   Group

Wizards Of The Coast
--------------------

RuleExplorer Client
~~~~~~~~~~~~~~~~~~~

.. autoclass:: mightstone.services.wotc.RuleExplorer
   :members:

Models
~~~~~~

.. currentmodule:: mightstone.services.wotc.models

.. autosummary::
   :toctree: _autosummary
   :recursive:

   ComprehensiveRules
   Ruleset
   Glossary

Fandom Wiki
-----------

`**MTG Wiki** at fandom <https://mtg.fandom.com>`_ is a great source of information with great details and references.


.. list-table::
   :header-rows: 1

   * - Feature
     - Support
   * - Export page
     - ✅
   * - Export category
     - ✅
   * - Explore pages (based on `Special:AllPages <https://mtg.fandom.com/wiki/Special:AllPages>`_)
     - ✅
   * - Wiki parser (bold, italic, links, lists, titles, paragraphs, templates, html tags...)
     - ✅

Wiki Client
~~~~~~~~~~~~~~~

.. autoclass:: mightstone.services.wiki.Wiki
   :members:

.. autoclass:: mightstone.services.wiki.WikiExportParser
   :members:


Wiki Parser
~~~~~~~~~~~~~~~

.. autoclass:: mightstone.services.wiki.WikiParser
   :members:

.. autoclass:: mightstone.services.wiki.MtgWikiParser
   :members:

Models
~~~~~~

.. currentmodule:: mightstone.services.wiki.models

.. autosummary::
   :toctree: _autosummary

    WikiElement
    WikiPage
    SerializableWikiPage
    WikiTextStyle
    WikiListStyle
    WikiListItemStyle
    WikiString
    WikiStyledText
    WikiLink
    WikiRevision
    WikiTemplate
    WikiFlow
    WikiParagraph
    WikiTitle
    WikiListBullet
    WikiListItem
    WikiList
    WikiHtml

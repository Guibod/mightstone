.. _reference-index:

API Reference
=============

EDHREC
------

Scryfall
--------

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
   CardAtomicGroup
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


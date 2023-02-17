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

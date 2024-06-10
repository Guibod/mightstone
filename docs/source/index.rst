mightstone -  A toolbox for anything Magic The Gathering related
================================================================

**mightstone** is a package and a command line tool to interact with Magic The Gathering™️ resources online.

Installation
=============

You can install mightstone from PyPI using pip:

.. code::

   pip install mightstone

or through Poetry:

.. code::

  poetry add mightstone


Features
========

* Mightstone use ``Pydantic``, ``Beanie`` and ``Asyncio`` as core feature.
* Integrated persistence support through ``Beanie`` of many data classes. Download once, and use data offline.
* HTTP cache integration
* Supported services:

  * `Scryfall <https://scryfall.com>`_
  * `EDHREC <https://edhrec.com/>`_
  * `MTGJSON <https://mtgjson.com/>`_
  * `CardConjurer <https://cardconjurer.com/>`_
  * `Magic The Gathering <https://magic.wizards.com/en/rules>`_ (rules)

* A ColorPie generator
* A robust Color identity Map
* A comprehensive rules API

Plans
=====

 * Support:
    * magicthegathering.io
    * 17lands
    * draftsim
    * MTGGoldfish
    * MtgTo8

 * An API to handle core concepts such as Abilities, ManaCost, Colors and Color Identity.
 * I also hope to provide tools for pandas integration

.. toctree::
   :maxdepth: 1
   :caption: Users

   users/installation
   users/cli
   users/configuration
   users/persistence
   users/cardconjurer
   users/asyncio

.. toctree::
   :maxdepth: 1
   :caption: Reference

   reference/api
   reference/changelog


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

Acknowledgments
---------------

Mightstone is inspired by `mtgtools <https://github.com/EskoSalaka/mtgtools/>`_, by Esko-Kalervo Salaka

Mightstone logo is derived from `Peter Venters original art edited by WOTC <https://scryfall.com/card/atq/55/mightstone>`_ in Antiquities extension.

Some static data are extracted from third part tools or websites:
 - `MTG WIKI <https://mtg.fandom.com/wiki/>`_ provides abilities
 - `Wizards of the coast <https://wizards.com>`_ provides rule sets

All the graphical and literal information and data related to Magic: The Gathering which can be handled with this software, such as card information and card images, is copyright © of Wizards of the Coast LLC, a Hasbro inc. subsidiary.
This software is in no way endorsed or promoted by Scryfall, magicthegathering.io or Wizards of the Coast.
This software is free and is created for the purpose of creating new Magic: The Gathering content and software, and just for fun.

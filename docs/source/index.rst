mightstone -  A toolbox for anything Magic The Gathering related
================================================================

**Mightstone** is a package and a command line tool to interact with Magic The Gathering™️ resources online.

Installation
=============

You can install mightstone from PyPI using pip:

.. code::

   pip install mightstone


Features
========

 * Mightstone use ``Pydantic`` and ``Asyncio`` as core feature.
 * Scryfall API
 * EDHREC (most features, the datamodel needs to be enhanced)
 * Magic The Gathering
    * A ColorPie generator
    * A robust Color identity Map
    * A comprehensive rules API

Plans
=====

 * Support:
    * magicthegathering.io
    * 17lands
    * draftsim
    * Card Conjurer (https://cardconjurer.com/home)
    * MTGGoldfish
    * MtgTo8

 * An API to handle core concepts such as Abilities, ManaCost, Colors and Color Identity.
 * This API should be able to parse and understand w
 * a persistence tool (most probably using Beanie and Mongodb) to allow an offline usage of scryfall or mtgio datas
 * a better documentation
 * a finalized asyncio interface (I need to pick either aiostream or asyncstdlib)
 * I also hope to provide tools for pandas integration

Getting started
===============

For more information, check the :ref:`api-reference`.

.. toctree::
   :maxdepth: 2
   :hidden:

   cli
   rule
   api_reference


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

Acknowledgments
---------------

Mightstone is inspired by `mtgtools <https://github.com/EskoSalaka/mtgtools/>`_, by Esko-Kalervo Salaka

All the graphical and literal information and data related to Magic: The Gathering which can be handled with this software, such as card information and card images, is copyright © of Wizards of the Coast LLC, a Hasbro inc. subsidiary.
This software is in no way endorsed or promoted by Scryfall, magicthegathering.io or Wizards of the Coast.
This software is free and is created for the purpose of creating new Magic: The Gathering content and software, and just for fun.

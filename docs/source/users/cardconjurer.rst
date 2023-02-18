===============
Card Generation
===============

**mightstone** provides a CardConjurer file format renderer (and parser). As for everything in mightstone, data is parsed into Pydantic objects, and accessed asynchronously.

mightstone don’t support card alteration from an existing json file for the moment.

.. literalinclude:: ../../../examples/card_conjurer.py
   :language: python

It is possible to generate your image from our CLI interface:

.. code-block:: bash

   python -m src.mightstone.cli cardconjurer render ./tests/mightstone/services/cardconjurer/Dimirova\ Smiley.json ./out.png --base-url="https://card-conjurer-assets.s3.us-east-1.amazonaws.com"

Assets and template availability
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

By design CardConjurer tries to decentralize template from their core tool. As is, Card Conjurer does not provide any mean to generate Magic The Gathering alike cards. Instead, you need to build your own template (or get your hands on) that reproduces MTG design. Mightstone won’t provide you any template.

The file format allow a card JSON data to point its parent template, and assets location. Every asset paths are relative to the parent template location. Most of the time, you’ll lose the path to the assets, that’s why you need to provide ``asset_root_url`` explicitly.

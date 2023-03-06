=================
Async vs Sync API
=================

**mightstone** is primarily an async library, that provides synchronous tools as a byproduct. We attempt to maintain a synchronous version of our API for non async programming context.

Mightstone uses Django’s ``asgiref.sync.AsyncToSync`` routines that seems to be a more advanced and robust implementation of the ``asyncio.run``. This allow async code to run in a safe sync context.

Asynchronous generators
~~~~~~~~~~~~~~~~~~~~~~~

Mightstone may stream items through an asynchronous generator, which requires ``async for`` loop.
We provide the ``aiterator_to_list`` utility to help you starting with async iterators. You should take a look at ``aiostream`` or ``asyncstdlib`` library to help you handle them.

.. code-block:: python

   from mightstone.ass import aiterator_to_list

    scryfall = Scryfall()
    found = aiterator_to_list(scryfall.search_async("boseiju"))

    print(f"I found {len(found)} ")




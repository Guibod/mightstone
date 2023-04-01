Persistence
***********

Mightstone uses `Beanie <https://beanie-odm.dev/>`_ as storage backend. This implies that you need to setup beanie backend before any instance of ``MightstoneDocument`` is created.

``beanie.exceptions.CollectionWasNotInitialized`` exception are raised as soon as a ``MightstoneDocument`` class is instanced before ``init_beanie`` is called. Please check `Beanie Documentation <https://beanie-odm.dev/tutorial/initialization/>`_ to learn more.

Automatic setup (recommended)
=============================

If you access to Mightstone content through the a ``Mightstone()`` this is done automatically.

.. literalinclude:: ../../../examples/persistence.py
   :language: python

This approach is recommended since our beanie implementation may evolved drastically.

Manual setup
============

If you wish to use base object, you’ll need to initialize beanie.

.. literalinclude:: ../../../examples/persistence_minimal.py
   :language: python


.. _cli:

Command Line Interface
======================

**mightstone** provide a command line interface built with :code:`Click`.

.. code-block:: bash

   python -m mightstone.cli --help


Examples
~~~~~~~~

.. code-block:: bash

   python -m mightstone.cli scryfall migration dd306737-d34c-4a0c-9e87-cd67bfa0d356


.. code-block:: bash

   python -m mightstone.cli scryfall collection id:683a5707-cddb-494d-9b41-51b4584ded69 "name:Ancient tomb" "set:dmu,collector_number:150"

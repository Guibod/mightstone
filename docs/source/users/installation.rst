============
Installation
============

**mightstone** is a standalone python project that uses
:code:`asyncio` and requires :code:`python >= 3.9.0`.

Install
=======

**mightstone** needs to be installed just like any other python package
into your documentation building environment:

.. code-block:: bash

   pip install mightstone

or alternatively:

.. code-block:: bash

   poetry add mightstone


Optional extensions
===================

Once installed, you'll need to enable it within sphinx' :code:`conf.py`:
Mightstone use :code:`conf.py` https://github.com/ICRAR/ijson that relies on :code:`YAJL` https://lloyd.github.io/yajl/.
IJson will use its python backend on the run if YAJL is not installed, but you cold benefit from installing YAJL locally.

.. code-block:: bash

   brew install yajl


Configuration
=============

**mightstone** does not support configuration yet.

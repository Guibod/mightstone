Configuration
*************

Mightstone behavior is defined by configuration. You can configure your mightstone by three means:

* Programmatically with a ``MightstoneSettings`` instance passed to your ``Mightstone`` application instance
* Through environment variables, for instance ``MIGHTSTONE_APPNAME`` to alter ``appname`` key
* Through a configuration file, with 3 means of defining

  * In CLI by passing a ``--config`` parameter to the command line client
  * Via ``MIGHTSTONE_CONFIG_FILE`` environment variable
  * Passively, by storing your configuration file in an standard location.

Configuration
=============

=========================== ======================================  ====== ======================== ===========
Path                        Environment Variable                    Type   default                  description
=========================== ======================================  ====== ======================== ===========
``appname``                 ``MIGHTSTONE_APPNAME``                  string ``mightstone``           Your application name, it will be used to build your storage and cache paths on the filesystem.
=========================== ======================================  ====== ======================== ===========



Storage
-------

=========================== ======================================  ====== ====================================== ===========
Path                        Environment Variable                    Type   default                                description
=========================== ======================================  ====== ====================================== ===========
``storage.implementation``  ``MIGHTSTONE_STORAGE_IMPLEMENTATION``   string ``local``                              Either ``local`` for a locally hosted mongod, ``motor`` for a remote mongodb connection.
``storage.uri``             ``MIGHTSTONE_STORAGE_URI``              string                                        Mongodb dsn (``mongodb://login:password@host/db``...), only used if ``motor`` implementation
``storage.directory``       ``MIGHTSTONE_STORAGE_DIRECTORY``        string ``<user_data>/Mightstone/data/mongo``  Data storage directory, only used if ``local`` implementation
``storage.database``        ``MIGHTSTONE_STORAGE_DATABASE``         string ``mightstone``                         The mongo database
=========================== ======================================  ====== ====================================== ===========

By default, Mighstone will use a jerry-rigged storage mechanism based on ``pymongo_inmemory``. This will not work with multiple concurrent instances of Mightstone tough.
There was an aborted attempt to use ``beanita`` / ``mongita`` backend, but we are still in dire need of features not implemented yet, and some bugfixes.

Http
----

=========================== ======================================  ============= ========================= ===========
Path                        Environment Variable                    Type          default                   description
=========================== ======================================  ============= ========================= ===========
``http.cache.persist``      ``MIGHTSTONE_CACHE_PERSIST``            bool          ``True``                  Use memory (transient) or filesystem (persistent) cache
``http.cache.directory``    ``MIGHTSTONE_CACHE_DIRECTORY``          string        ``<user_cache>/http``     The directory to store HTTP cache, only used of ``persist`` is ``true``
``http.cache.methods``      ``MIGHTSTONE_CACHE_METHODS``            list[string]  ``[GET]``                 HTTP verbs to cache
``http.cache.status``       ``MIGHTSTONE_CACHE_STATUS``             list[int]     ``[200,203,300,301,308]`` HTTP status code to cache
=========================== ======================================  ============= ========================= ===========


Where to store your configuration ?
===================================

Mightstone will search configuration file in this order:

* ``<current_directory>/mightstone.yaml``
* ``<current_directory>/mightstone.yml``
* ``<current_directory>/mightstone.json``
* ``<current_directory>/mightstone.toml``
* ``<user_config_directory>/mightstone.yaml``
* ``<user_config_directory>/mightstone.yml``
* ``<user_config_directory>/mightstone.json``
* ``<user_config_directory>/mightstone.toml``

Mighstone relies on `AppDirs <https://github.com/ActiveState/appdirs>`_ package to resolve user config directory:

::

    Mac OS X:               ~/Library/Application Support/Mightstone
    Unix:                   ~/.config/Mightstone     # or in $XDG_CONFIG_HOME, if defined
    Win XP (not roaming):   C:\Documents and Settings\<username>\Application Data\Mightstone\Mightstone
    Win XP (roaming):       C:\Documents and Settings\<username>\Local Settings\Application Data\Mightstone\Mightstone
    Win 7  (not roaming):   C:\Users\<username>\AppData\Local\Mightstone\Mightstone
    Win 7  (roaming):       C:\Users\<username>\AppData\Roaming\Mightstone\Mightstone

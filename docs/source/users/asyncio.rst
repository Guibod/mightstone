==================
Async and Sync API
==================

**mightstone** is primarily an async library, that provides synchronous tools as a byproduct. We attempt to maintain a synchronous version of our API for non async programming context.

Mightstone uses ``universalasync`` to universally provide both synchronous and asynchronous api.

As such you’ll find many method suffixed by ``_async``, and universally wrapped version without the suffix.

Example
-------

Given the ``Scryfall`` api as defined in ``mightstone.services.scryfall.api``

* ``Scryfall.random()`` is both accessible in async and sync context (thanks to `universalasync`)
* ``Scryfall.random_async()`` is the non wrapped version of the method, that can only be used in an async context

Limitation
----------

Mypy and other static type checking (pyright, pyre...) are not able to infer type from the calling context, as such it is not able to exclude async call context type from sync context (and conversely).

You’ll need to explicitly ignore the returned type.

For instance:

```python
cr: ComprehensiveRules = mightstone.rule_explorer.open(latest_url)  # type: ignore
```

from typing import Any, Type, TypeVar, Union

from injector import Injector, Provider, Scope, ScopeDecorator, SingletonScope

"""
This file implements a variant of resource cleanup provided in this MR
https://github.com/python-injector/injector/pull/252/files
"""

T = TypeVar("T")


class CleanupScope(SingletonScope):
    def __init__(self, injector: Injector) -> None:
        super().__init__(injector)
        # We have singletons here, so never cache them twice, since otherwise
        # the cleanup method might be invoked twice.
        self.cachedProviders: set[Provider[Any]] = set()

    def get(self, key: Type[T], provider_: Provider[T]) -> Provider[T]:
        obj = super().get(key, provider_)
        self.cachedProviders.add(obj)
        return obj


class CleanupInjector(Injector):
    def cleanup(self):
        cleanup_scope = self.get(CleanupScope)
        for cached_provider in cleanup_scope.cachedProviders:
            obj = cached_provider.get(self)
            if hasattr(obj, "cleanup") and callable(obj.cleanup):
                obj.cleanup()


cleaned = ScopeDecorator(CleanupScope)
ScopeType = Union[ScopeDecorator, Type[Scope], None]

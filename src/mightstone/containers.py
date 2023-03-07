import httpx_cache
from appdirs import user_cache_dir
from dependency_injector import containers, providers
from dependency_injector.providers import Factory

from .services.cardconjurer import CardConjurer
from .services.edhrec import EdhRecApi, EdhRecStatic
from .services.mtgjson import MtgJson
from .services.scryfall import Scryfall


class Container(containers.DeclarativeContainer):
    # Gateways
    httpx_cache_transport: httpx_cache.AsyncCacheControlTransport = providers.Factory(
        httpx_cache.AsyncCacheControlTransport,
        cache=httpx_cache.FileCache(cache_dir=user_cache_dir("mightstone")),
    )

    # Services
    scryfall: Factory[Scryfall] = providers.Factory(
        Scryfall,
        transport=httpx_cache_transport,
    )

    edhrec_static: Factory[EdhRecStatic] = providers.Factory(
        EdhRecStatic,
        transport=httpx_cache_transport,
    )

    edhrec_api: Factory[EdhRecApi] = providers.Factory(
        EdhRecApi,
        transport=httpx_cache_transport,
    )

    card_conjurer: Factory[CardConjurer] = providers.Factory(
        CardConjurer,
        transport=httpx_cache_transport,
    )

    mtg_json: Factory[MtgJson] = providers.Factory(
        MtgJson,
        transport=httpx_cache_transport,
    )

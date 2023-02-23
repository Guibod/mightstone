import httpx_cache
import logging.config
from dependency_injector import containers, providers

from .config import Settings
from .services.scryfall import Scryfall


class Container(containers.DeclarativeContainer):
    config = providers.Configuration(pydantic_settings=[Settings()])
    logging = providers.Resource(
        logging.config.dictConfig,
        fname="logging.ini",
    )

    # Gateways
    httpx_client = providers.Singleton(
        httpx_cache.AsyncClient,
        config.database.dsn,
    )

    # s3_client = providers.Singleton(
    #     boto3.client,
    #     service_name="s3",
    #     aws_access_key_id=config.aws.access_key_id,
    #     aws_secret_access_key=config.aws.secret_access_key,
    # )

    # Services
    scryfall = providers.Factory(
        Scryfall,
        client=httpx_client,
    )

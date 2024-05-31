import logging
from typing import Optional

from pydantic import ValidationError

from mightstone.config import MainSettings
from mightstone.containers import Application
from mightstone.core import MightstoneError
from mightstone.services.cardconjurer import CardConjurer
from mightstone.services.edhrec import EdhRecApi, EdhRecStatic
from mightstone.services.mtgjson import MtgJson
from mightstone.services.scryfall import Scryfall
from mightstone.services.wotc import RuleExplorer

logger = logging.getLogger("mightstone")


class Mightstone:
    """
    A Mighstone instance

    Using python dependency injector, this class provides the services in an
    orderly fashion after setting up dependencies such as Beanie.
    """

    def __init__(
        self,
        application: Optional[Application] = None,
        config: Optional[MainSettings] = None,
    ):
        if not application:
            application = Application()

        self.app = application
        try:
            if not config:
                config = MainSettings()

            d = config.model_dump(mode="python")
            application.config.from_dict(d)
            application.check_dependencies()
            application.init_resources()
            application.wire(modules=["mightstone"])
        except ValidationError as e:
            logger.fatal("Failed to initialize Mightstone, invalid configuration")
            logger.fatal(e)
            raise MightstoneError("Invalid configuration") from e
        except Exception as e:
            logger.fatal("Failed to initialize Mightstone, %s", e)
            raise MightstoneError("Runtime error") from e

    def __del__(self):
        self.app.shutdown_resources()

    @property
    def scryfall(self) -> Scryfall:
        return self.app.services().scryfall()

    @property
    def mtg_json(self) -> MtgJson:
        return self.app.services().mtg_json()

    @property
    def card_conjurer(self) -> CardConjurer:
        return self.app.services().card_conjurer()

    @property
    def edhrec_api(self) -> EdhRecApi:
        return self.app.services().edhrec_api()

    @property
    def edhrec_static(self) -> EdhRecStatic:
        return self.app.services().edhrec_static()

    @property
    def rule_explorer(self) -> RuleExplorer:
        return self.app.services().rule_explorer()

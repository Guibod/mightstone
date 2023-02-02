import logging

logger = logging.getLogger("mightstone")


class App:
    def __init__(self, settings):
        self.settings = settings

    def start(self):
        logger.info("mightstone Starting")

    def stop(self):
        logger.info("mightstone Stopping")

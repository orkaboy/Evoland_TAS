# Libraries and Core Files
import logging

import evo2.control

logger = logging.getLogger(__name__)
ctrl = evo2.control.handle()


def perform_TAS(config_data):
    logger.info("Game mode: Evoland2")

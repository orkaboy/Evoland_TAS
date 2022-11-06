# Libraries and Core Files
import logging

import evo1.control

logger = logging.getLogger(__name__)
ctrl = evo1.control.handle()


def perform_TAS(config_data):
    logger.info("Game mode: Evoland1")

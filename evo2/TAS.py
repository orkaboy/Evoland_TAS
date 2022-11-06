# Libraries and Core Files
import logging

import evo1.memory as memory
import evo2.control as control

logger = logging.getLogger(__name__)
ctrl = control.handle()


def perform_TAS(config_data: dict):
    logger.info("Game mode: Evoland2")
    logger.error("Not implemented yet!")
    memory.wait_seconds(3)

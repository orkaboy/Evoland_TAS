# Libraries and Core Files
import logging

import evo2.control as control
from engine.seq import wait_seconds
from term.window import WindowLayout

logger = logging.getLogger(__name__)
ctrl = control.handle()


def perform_TAS(window: WindowLayout):
    logger.info("Game mode: Evoland2")
    logger.error("Not implemented yet!")
    wait_seconds(3)

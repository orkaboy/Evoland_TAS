# Libraries and Core Files
import logging

import evo2.control as control
import evo2.memory as memory
import memory.core as core
from term.curses import WindowLayout

logger = logging.getLogger(__name__)
ctrl = control.handle()


def perform_TAS(window: WindowLayout):
    logger.info("Game mode: Evoland2")
    logger.error("Not implemented yet!")
    core.wait_seconds(3)

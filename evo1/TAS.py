# Libraries and Core Files
import logging

import evo1.control as control
import evo1.memory as memory

logger = logging.getLogger(__name__)
ctrl = control.handle()


def perform_TAS(config_data: dict):
    logger.info("Game mode: Evoland1")
    # memory.wait_frames(60)
    logger.info("Press confirm")
    ctrl.confirm()
    memory.wait_frames(30)
    ctrl.dpad.tap_down()
    ctrl.dpad.tap_down()
    ctrl.confirm()

    ctrl.set_neutral()
    memory.wait_frames(120)

    # logger.info("Pressed confirm")
    # ctrl.attack()
    logger.info("We did something!")

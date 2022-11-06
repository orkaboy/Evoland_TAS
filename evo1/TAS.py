# Libraries and Core Files
import logging

import evo1.control as control
import evo1.memory as memory
from log_init import reset_logging_time_reference
from menu_control import MenuController

logger = logging.getLogger(__name__)
ctrl = control.handle()


def evoland1_start_game():
    menu_ctrl = MenuController()
    logger.info("Starting Evoland1 from main menu...")
    logger.debug("Press confirm to activate main menu.")
    menu_ctrl.confirm()
    memory.wait_seconds(1)
    logger.debug("Press confirm to select new game.")
    menu_ctrl.confirm()
    memory.wait_seconds(1)
    logger.debug("Press confirm to select Evoland1.")
    logger.info("Starting timer!")
    reset_logging_time_reference()
    menu_ctrl.confirm()
    memory.wait_seconds(3)
    logger.info("In game!")


def perform_TAS(config_data: dict):
    logger.info("Game mode: Evoland1")
    evoland1_start_game()
    experimental_move(config_data)
    logger.info("Evoland1 TAS Done!")
    memory.wait_seconds(3)


def experimental_move(config_data: dict):
    logger.info("Experimental function")
    ctrl.dpad.right()
    memory.wait_seconds(1)
    ctrl.dpad.none()
    ctrl.dpad.left()
    memory.wait_seconds(1.5)
    ctrl.dpad.none()
    ctrl.dpad.tap_right()
    ctrl.dpad.tap_up()

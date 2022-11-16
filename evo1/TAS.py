# Libraries and Core Files
import logging

import evo1.control as control
import evo1.memory as memory
import memory.core as core
from menu_control import MenuController
from term.log_init import reset_logging_time_reference

logger = logging.getLogger(__name__)
ctrl = control.handle()


def evoland1_start_game():
    menu_ctrl = MenuController()
    logger.info("Starting Evoland1 from main menu...")
    logger.debug("Press confirm to activate main menu.")
    menu_ctrl.confirm()
    core.wait_seconds(1)
    logger.debug("Press confirm to select new game.")
    menu_ctrl.confirm()
    core.wait_seconds(1)
    logger.debug("Press confirm to select Evoland1.")
    logger.info("Starting timer!")
    reset_logging_time_reference()
    menu_ctrl.confirm()
    core.wait_seconds(3)
    logger.info("In game!")


def perform_TAS(config_data: dict):
    logger.info("Game mode: Evoland1")
    evoland1_start_game()
    experimental_move(config_data)
    logger.info("Evoland1 TAS Done!")
    core.wait_seconds(3)


def experimental_move(config_data: dict):
    mem = memory.Evoland1Memory()

    logger.info("Experimental function")
    core.wait_seconds(2)
    for _ in range(1000):
        logger.debug(f"Player pos: {mem.get_player_pos()}")
        logger.debug(f"Player facing: {mem.get_player_facing()}")
        logger.debug(f"Player is moving: {mem.get_player_is_moving()}")
        logger.debug(f"Inv_open: {mem.get_inv_open()}")
        core.wait_seconds(0.1)

    logger.info("Experimental function")
    ctrl.dpad.right()
    core.wait_seconds(1)
    ctrl.dpad.none()
    ctrl.dpad.left()
    core.wait_seconds(1.5)
    ctrl.dpad.none()
    ctrl.dpad.tap_right()
    ctrl.dpad.tap_up()

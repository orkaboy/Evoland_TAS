# Libraries and Core Files
import logging
from typing import List

import evo1.control as control
import evo1.memory as memory
import memory.core as core
from engine.seq import (
    SeqBase,
    SeqDebug,
    SeqDelay,
    SeqFunc,
    SeqList,
    SeqLog,
    SequencerEngine,
)
from evo1.stats import stats_2d
from menu_control import MenuController
from term.log_init import reset_logging_time_reference

logger = logging.getLogger(__name__)
ctrl = control.handle()


class SeqMenuConfirm(SeqBase):
    def __init__(self, name: str = "Confirm"):
        self.menu_ctrl = MenuController()
        super().__init__(name)

    def execute(self, delta: float, blackboard: dict) -> bool:
        self.menu_ctrl.confirm()
        return True


class Evoland1StartGame(SeqList):
    def __init__(self):
        super().__init__(
            name="Start game",
            children=[
                SeqLog(name="SYSTEM", text="Starting Evoland1 from main menu..."),
                SeqDebug(name="SYSTEM", text="Press confirm to activate main menu."),
                SeqMenuConfirm(),
                SeqDelay(name="Menu", time_in_s=1.0),
                SeqDebug(name="SYSTEM", text="Press confirm to select new game."),
                SeqDelay(name="Menu", time_in_s=1.0),
                SeqDebug(name="SYSTEM", text="Press confirm to select Evoland1."),
                SeqLog(name="SYSTEM", text="Starting timer!"),
                SeqFunc(reset_logging_time_reference),
                SeqMenuConfirm(),
                SeqDelay(name="Starting game", time_in_s=3.0),
                SeqLog(name="SYSTEM", text="In game!"),
            ],
        )


# def evoland1_start_game(main_win, stats_win):
#    menu_ctrl = MenuController()
#    logger.info("Starting Evoland1 from main menu...")
#    logger.debug("Press confirm to activate main menu.")
#    menu_ctrl.confirm()
#    core.wait_seconds(1)
#    logger.debug("Press confirm to select new game.")
#    menu_ctrl.confirm()
#    core.wait_seconds(1)
#    logger.debug("Press confirm to select Evoland1.")
#    logger.info("Starting timer!")
#    reset_logging_time_reference()
#    menu_ctrl.confirm()
#    core.wait_seconds(3)
#    logger.info("In game!")


def perform_TAS(main_win, stats_win, config_data: dict):
    engine = SequencerEngine(
        main_win=main_win,
        stats_win=stats_win,
        config_data=config_data,
        root=SeqList(
            name="Evoland1",
            children=[
                Evoland1StartGame(),
                SeqLog(name="SYSTEM", text="Evoland1 TAS Done!"),
            ],
        ),
    )

    while engine.active():
        engine.run()

    # main_win.clear()
    # main_win.refresh()
    # stats_win.clear()
    # stats_win.refresh()
    #
    # logger.info("Game mode: Evoland1")
    ##evoland1_start_game(main_win, stats_win)
    # experimental_move(main_win, stats_win, config_data)
    # logger.info("Evoland1 TAS Done!")
    core.wait_seconds(3)


def experimental_move(main_win, stats_win, config_data: dict):
    mem = memory.Evoland1Memory()

    logger.info("Experimental function")
    core.wait_seconds(2)

    def update():
        logger.debug(f"Player is moving: {mem.get_player_is_moving()}")
        logger.debug(f"Inv_open: {mem.get_inv_open()}")
        core.wait_seconds(0.1)

    for _ in range(1000):
        update()
        stats_2d(stats_win)

    logger.info("Experimental function")
    ctrl.dpad.right()
    core.wait_seconds(1)
    ctrl.dpad.none()
    ctrl.dpad.left()
    core.wait_seconds(1.5)
    ctrl.dpad.none()
    ctrl.dpad.tap_right()
    ctrl.dpad.tap_up()

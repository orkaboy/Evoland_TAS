# Libraries and Core Files
import curses
import logging

import evo1.control as control
import memory.core as core
from control.menu_control import SeqMenuConfirm
from engine.seq import SeqDebug, SeqDelay, SeqFunc, SeqList, SeqLog, SequencerEngine
from evo1.memory import Facing, Vec2, load_memory
from evo1.move2d import SeqAttack, SeqGrabChest, SeqMove2D
from term.log_init import reset_logging_time_reference

logger = logging.getLogger(__name__)
ctrl = control.handle()


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
                SeqMenuConfirm(),
                SeqDelay(name="Menu", time_in_s=1.0),
                SeqDebug(name="SYSTEM", text="Press confirm to select Evoland1."),
                SeqLog(name="SYSTEM", text="Starting timer!"),
                SeqFunc(reset_logging_time_reference),
                SeqMenuConfirm(),
                SeqDelay(name="Starting game", time_in_s=3.0),
                SeqLog(name="SYSTEM", text="In game!"),
            ],
        )


def perform_TAS(main_win, stats_win, config_data: dict):
    engine = SequencerEngine(
        main_win=main_win,
        stats_win=stats_win,
        config_data=config_data,
        root=SeqList(
            name="Evoland1",
            children=[
                Evoland1StartGame(),
                SeqFunc(load_memory),  # Get all pointers
                FirstArea(),
                SeqLog(name="SYSTEM", text="Evoland1 TAS Done!"),
            ],
        ),
    )

    main_win.clear()
    stats_win.clear()
    curses.doupdate()

    while engine.active():
        engine.run()

    core.wait_seconds(3)


class FirstArea(SeqList):
    def __init__(self):
        super().__init__(
            name="First area",
            children=[
                SeqMove2D("Move to chest", coords=[Vec2(14, 52)]),
                SeqGrabChest("Move Left", direction=Facing.RIGHT),
                SeqMove2D("Move to chest", coords=[Vec2(11, 52)]),
                SeqGrabChest("Move Vertical", direction=Facing.LEFT),
                SeqMove2D("Move to chest", coords=[Vec2(12, 51)]),
                SeqGrabChest("Basic Scroll", direction=Facing.UP),
                SeqMove2D(
                    "Move to chest",
                    coords=[
                        Vec2(12, 47),
                        Vec2(21, 47),
                        Vec2(21, 52),
                        Vec2(20, 52),
                    ],
                ),
                SeqGrabChest("Smooth Scroll", direction=Facing.LEFT),
                SeqMove2D(
                    "Move to sword",
                    coords=[
                        Vec2(24, 52),
                        Vec2(24, 53),
                        Vec2(29, 53),
                        Vec2(29, 58),
                        Vec2(30, 58),
                        Vec2(30, 60),
                    ],
                ),
                SeqGrabChest("Sword", direction=Facing.DOWN),
                SeqMove2D(
                    "Move to bush",
                    coords=[
                        Vec2(30, 57),
                        Vec2(31, 57),
                        Vec2(31, 55),
                    ],
                ),
                SeqAttack("Bush"),
                SeqMove2D("Move to bush", coords=[Vec2(32, 55)]),
                SeqGrabChest("Monsters", direction=Facing.RIGHT),
            ],
        )

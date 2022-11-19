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
                # TODO: Should add annotator here that can deal with enemies (seems ok tho)
                SeqMove2D(
                    "Dodge enemies",
                    coords=[
                        Vec2(35, 55),
                        Vec2(35, 54),
                        Vec2(36, 54),
                        Vec2(36, 53),
                        Vec2(37, 53),
                        Vec2(37, 52),
                        Vec2(39, 52),
                    ],
                ),
                # Here's music chest to the right, TODO: optionally grab?
                SeqAttack("Bush"),
                SeqMove2D(
                    "Move to chest",
                    coords=[
                        Vec2(39, 47),
                        # Optional, chest to the north, save (move to Vec2(39, 45), then open chest N)
                        Vec2(41, 47),
                        Vec2(41, 48),
                        Vec2(44, 48),
                        Vec2(44, 49),
                    ],
                ),
                SeqGrabChest("16-bit", direction=Facing.DOWN),
                # TODO: Some enemies here, will probably fail
                SeqMove2D(
                    "Dodge enemies",
                    coords=[
                        Vec2(44, 52),
                        Vec2(50, 52),
                        Vec2(50, 53),
                        Vec2(55, 53),
                        Vec2(55, 54),
                        Vec2(58, 54),
                    ],
                ),
                # TODO: WR attacks bush here, needed or just swag?
                SeqMove2D(
                    "Dodge enemies",
                    coords=[
                        Vec2(60, 54),
                        Vec2(60, 44),
                        Vec2(51, 44),
                        Vec2(51, 45),
                        Vec2(48, 45),
                        Vec2(48, 36),
                        Vec2(36, 36),
                        Vec2(36, 33),
                        Vec2(34, 33),
                    ],
                ),
                SeqGrabChest("Free move", direction=Facing.LEFT),
            ],
        )

from engine.seq import SeqList
from engine.mathlib import Facing, Vec2
from evo1.move2d import SeqGrabChest, SeqMove2D, SeqZoneTransition


class PapurikaVillage(SeqList):
    def __init__(self):
        super().__init__(
            name="Papurika Village",
            children=[
                SeqMove2D(
                    "Move to well",
                    coords=[
                        Vec2(42, 25),
                        Vec2(39, 18),
                        Vec2(39, 15),
                    ],
                ),
                # TODO: Confirm, confirm (down the well)
                SeqMove2D(
                    "Move to seed",
                    coords=[
                        Vec2(4, 6),
                    ],
                ),
                # TODO: Confirm, confirm (grab seed), wait for control
                SeqMove2D(
                    "Move to surface",
                    coords=[
                        Vec2(7.5, 2.6),
                    ],
                ),
                # TODO: Confirm (get out of well)
                SeqMove2D(
                    "Move to chest",
                    coords=[
                        Vec2(34, 25),
                        Vec2(29, 30),
                        Vec2(12, 30),
                        Vec2(8, 28),
                    ],
                ),
                # TODO: Grab chest(home invasion) @(7.5, 28)
                SeqMove2D(
                    "Move to shop",
                    coords=[
                        Vec2(20, 30),
                        Vec2(23.7, 29.5),
                        Vec2(25, 25),
                    ],
                ),
                # Transition north (into shop)
                SeqZoneTransition("Enter shop", Facing.UP, time_in_s=0.5),
                SeqMove2D(
                    "Looting",
                    coords=[
                        Vec2(37, 42),
                        Vec2(39, 40.2),
                        Vec2(40, 40.3), # TODO: Optional!
                    ],
                ),
                # TODO: Optional grab coin if we have less than 250
                # TODO: Conf x2
                SeqMove2D(
                    "Shopping",
                    coords=[
                        Vec2(38, 41),
                        Vec2(35, 41),
                        Vec2(34.5, 40.6),
                    ],
                ),
                # TODO: Conf (talk to shop keep)
                # TODO: [Menu]. conf(buy), down (to sword), conf x4 (sword, yes, talk to shop keep, buy), down (to armor), conf x2 (armor, yes)
                SeqMove2D(
                    "Leave shop",
                    coords=[
                        Vec2(30, 42),
                        Vec2(29, 42),
                    ],
                ),
                # Transition south (exit shop)
                SeqZoneTransition("Leave shop", Facing.DOWN, time_in_s=0.5),
                SeqMove2D(
                    "Leave town",
                    coords=[
                        Vec2(26, 27),
                        Vec2(44, 27),
                        Vec2(49, 23),
                        Vec2(62, 22),
                        Vec2(64, 19),
                        Vec2(65, 15),
                        Vec2(65, 8),
                    ],
                ),
                # Transition north (exit town to overworld)
                SeqZoneTransition("To overworld", Facing.UP, time_in_s=0.5),
            ],
        )

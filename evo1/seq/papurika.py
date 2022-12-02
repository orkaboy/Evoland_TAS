from engine.seq import SeqList, SeqOptional, SeqLog
from engine.mathlib import Facing, Vec2, Box2
from engine.navmap import NavMap
from evo1.move2d import SeqGrabChest, SeqMove2D, SeqZoneTransition, SeqKnight2D
from evo1.interact import SeqShopBuy, SeqInteract, SeqWaitForControl
from evo1.memory import get_memory

_meadow_map = NavMap("evo1/maps/meadow.yaml")

class MeadowFight(SeqList):
    def __init__(self):
        super().__init__(
            name="Meadow",
            children=[
                SeqMove2D(
                    name="Wake up knights",
                    precision=0.1,
                    coords=[
                        Vec2(14, 14), # Go past the chest
                        Vec2(14.1, 11.5),
                        Vec2(15, 11), # Wake up first knight
                        Vec2(16.5, 10.9),
                        Vec2(17, 10), # Wake up second knight
                        Vec2(16.9, 8.6),
                        Vec2(16, 8), # Wake up third knight
                        Vec2(14.5, 8.1),
                        Vec2(14, 9), # Wake up the fourth knight
                    ],
                    tilemap=_meadow_map
                ),
                SeqKnight2D(
                    "Killing four knights",
                    arena=Box2(pos=Vec2(12, 6), w=7, h=8), # Valid arena to fight inside (should be clear of obstacles)
                    targets=[Vec2(14, 11), Vec2(17, 11), Vec2(17, 7), Vec2(14, 7)], # Positions of enemies (known from start, but they move)
                    track_size=1.2,
                    tilemap=_meadow_map
                ),
                SeqMove2D(
                    name="Move to chest",
                    coords=[
                        Vec2(18, 11),
                        Vec2(19, 11),
                        # Chest to the right
                    ],
                    tilemap=_meadow_map
                ),
            ]
        )


def need_to_steal_cash() -> int:
    mem = get_memory()
    gli = mem.get_gli()
    return 1 if gli < 250 else 0


# TODO: _village_map = NavMap("evo1/maps/village.yaml")

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
                        Vec2(39, 16),
                    ],
                ),
                SeqInteract("Down the well"),
                SeqMove2D(
                    "Move to seed",
                    coords=[
                        Vec2(4, 6),
                    ],
                ),
                SeqInteract("Grab growth seed"),
                SeqMove2D(
                    "Move to surface",
                    coords=[
                        Vec2(7.5, 2.8),
                        Vec2(7.5, 2.6), # Align to look north
                    ],
                ),
                SeqInteract("Leave well"),
                SeqMove2D(
                    "Move to chest",
                    coords=[
                        Vec2(34, 25),
                        Vec2(29, 30),
                        Vec2(12, 30),
                        Vec2(7.8, 28),
                    ],
                ),
                # Grab chest(home invasion) @(7.5, 28)
                SeqGrabChest("Home invasion", direction=Facing.LEFT),
                SeqMove2D(
                    "Move to shop",
                    coords=[
                        Vec2(20, 30),
                        Vec2(24, 30),
                        Vec2(25, 25),
                    ],
                ),
                # Transition north (into shop)
                SeqZoneTransition("Enter shop", Facing.UP, time_in_s=0.5),
                SeqMove2D(
                    "Moving to chest",
                    coords=[
                        Vec2(37, 42),
                        Vec2(39, 40.2),
                    ],
                ),
                SeqOptional(
                    "Checking wallet",
                    cases={
                        # Check if we have enough cash
                        0: SeqLog("Wallet", "We don't need to break any laws today"),
                        1: SeqList(
                            "Pillaging",
                            children=[
                                SeqMove2D(
                                    "Moving to barrel",
                                    coords=[Vec2(40, 40.3)],
                                ),
                                SeqInteract("Grabbing 50 gli"),
                                SeqInteract("Confirming"),
                            ],
                        ),
                    },
                    selector=need_to_steal_cash,
                ),
                SeqMove2D(
                    "Shopping",
                    coords=[
                        Vec2(38, 41),
                        Vec2(34.6, 41),
                        Vec2(34.3, 40.6),
                    ],
                ),
                SeqShopBuy("Sword", slot=1),
                SeqShopBuy("Armor", slot=1),
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

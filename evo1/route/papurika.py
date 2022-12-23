from engine.mathlib import Box2, Facing, Vec2
from engine.move2d import SeqCtrlNeutral, SeqGrabChest, SeqMove2D
from engine.seq import SeqInteract, SeqList, SeqLog, SeqOptional
from evo1.combat import SeqKnight2D
from evo1.move2d import SeqZoneTransition
from evo1.shop import SeqShopBuy
from memory.evo1 import MapID, get_memory


def in_papurika() -> bool:
    mem = get_memory()
    return mem.map_id == MapID.PAPURIKA


class MeadowFight(SeqList):
    def __init__(self):
        super().__init__(
            name="Meadow",
            children=[
                SeqMove2D(
                    name="Wake up knights",
                    precision=0.1,
                    coords=[
                        Vec2(14, 14),  # Go past the chest
                        Vec2(14.1, 11.5),
                        Vec2(15, 11),  # Wake up first knight
                        Vec2(16.5, 10.9),
                        Vec2(17, 10),  # Wake up second knight
                        Vec2(16.9, 8.6),
                        Vec2(16, 8),  # Wake up third knight
                        Vec2(14.5, 8.1),
                        Vec2(14, 9),  # Wake up the fourth knight
                        # Return to a safer position, closer to the first knights
                        Vec2(15.5, 10),
                    ],
                ),
                SeqKnight2D(
                    "Killing four knights",
                    arena=Box2(pos=Vec2(0, 0), w=31, h=23),
                    num_targets=4,
                ),
                SeqMove2D(
                    name="Move to chest",
                    coords=[
                        Vec2(18, 11),
                        Vec2(19, 11),
                        # Chest to the right
                    ],
                    # Check if we accidentally already picked up the chest
                    emergency_skip=in_papurika,
                ),
            ],
        )


def need_to_steal_cash() -> int:
    try:
        mem = get_memory()
        return 1 if mem.gli < 250 else 0
    # This fallback clause is for load game past this point
    except AttributeError:
        return 0


class PapurikaVillageShopping(SeqList):
    def __init__(self):
        super().__init__(
            name="Shopping",
            children=[
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
                                SeqCtrlNeutral(),
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
                        Vec2(34.3, 41),
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
                SeqZoneTransition(
                    "Leave shop", Facing.DOWN, target_zone=MapID.PAPURIKA
                ),
            ],
        )


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
                        Vec2(7.5, 2.6),  # Align to look north
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
                SeqZoneTransition(
                    "Enter shop", Facing.UP, target_zone=MapID.PAPURIKA_INTERIOR
                ),
                PapurikaVillageShopping(),
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
                SeqZoneTransition(
                    "To overworld", Facing.UP, target_zone=MapID.OVERWORLD
                ),
            ],
        )

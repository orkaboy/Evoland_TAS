from engine.combat import SeqCombat3D, SeqMove2DClunkyCombat
from engine.mathlib import Box2, Facing, Vec2
from engine.move2d import (
    SeqGrabChest,
    SeqGrabChestKeyItem,
    SeqHoldInPlace,
    SeqManualUntilClose,
    SeqMove2D,
    SeqMove2DCancel,
)
from engine.seq import SeqAttack, SeqDelay, SeqList, SeqMenu
from evo1.move2d import SeqZoneTransition
from maps.evo1 import GetAStar
from memory.evo1 import MapID

_noria_astar = GetAStar(MapID.NORIA)
_noria_start_astar = GetAStar(MapID.NORIA_CLOSED)


# TODO: Improve on the chest grab to be more concise (don't require the approach)
class NoriaToMaze(SeqList):
    """Handle the entire first sequence of the Noria Mines, from entry to the start of the first maze."""

    def __init__(self):
        super().__init__(
            name="Navigate to maze",
            children=[
                SeqMove2D(
                    "Move to chest",
                    coords=_noria_start_astar.calculate(
                        start=Vec2(47, 67), goal=Vec2(46, 56), final_pos=Vec2(46, 55.6)
                    ),
                ),
                SeqGrabChest("Opening the mines", direction=Facing.UP),
                SeqMove2DClunkyCombat(
                    "Move to chest",
                    coords=_noria_astar.calculate(
                        start=Vec2(46, 55), goal=Vec2(51, 48), final_pos=Vec2(51, 47.6)
                    ),
                ),
                SeqGrabChest("Breakable pots", direction=Facing.UP),
                SeqMove2DClunkyCombat(
                    "Move to chest",
                    coords=_noria_astar.calculate(
                        start=Vec2(51, 47), goal=Vec2(54, 40), final_pos=Vec2(54, 39.6)
                    ),
                ),
                SeqGrabChest("Pressure plates", direction=Facing.UP),
                SeqMove2DClunkyCombat(
                    "Trigger plate(L)",
                    coords=_noria_astar.calculate(
                        start=Vec2(54, 39), goal=Vec2(50, 37)
                    ),
                ),
                SeqHoldInPlace(
                    name="Trigger plate(L)", target=Vec2(50, 37), timeout_in_s=0.5
                ),
                SeqMove2DClunkyCombat(
                    "Trigger plate(R)",
                    coords=_noria_astar.calculate(
                        start=Vec2(50, 37), goal=Vec2(58, 37)
                    ),
                ),
                # TODO: menu glitch (important)
                SeqHoldInPlace(
                    name="Trigger plate(R)", target=Vec2(58, 37), timeout_in_s=0.5
                ),
                SeqMove2DClunkyCombat(
                    "Move to chest",
                    coords=_noria_astar.calculate(
                        start=Vec2(58, 37), goal=Vec2(48, 45), final_pos=Vec2(48, 44.6)
                    ),
                ),
                SeqGrabChest("Red Mage", direction=Facing.UP),
                SeqMove2DClunkyCombat(
                    "Move to chest",
                    coords=_noria_astar.calculate(
                        start=Vec2(48, 44), goal=Vec2(35, 41), final_pos=Vec2(35, 40.6)
                    ),
                ),
                # TODO: Trigger menu glitch to get two keys
                SeqGrabChest("Trap room", direction=Facing.UP),
                SeqCombat3D(
                    "Killing bats",
                    arena=Box2(Vec2(32, 40), w=8, h=8),
                    num_targets=3,
                    retracking=True,
                ),
                SeqMove2DClunkyCombat("Move to chest", coords=[Vec2(34, 41)]),
                # Get in position for chest
                SeqMove2D("Move to chest", coords=[Vec2(33.6, 41)]),
                SeqGrabChest("Key", direction=Facing.LEFT),
                SeqMove2DClunkyCombat(
                    "Move to door",
                    coords=_noria_astar.calculate(
                        start=Vec2(37, 44), goal=Vec2(41, 42)
                    ),
                ),
                # TODO: Open door(N)
                SeqMove2DClunkyCombat(
                    "Move to chest",
                    coords=_noria_astar.calculate(
                        start=Vec2(41, 41), goal=Vec2(41, 40), final_pos=Vec2(41, 39.6)
                    ),
                ),
                SeqGrabChest("Skellies", direction=Facing.UP),
                # Skip past first skeleton
                SeqMove2DCancel(
                    "Move to trigger",
                    coords=_noria_astar.calculate(
                        start=Vec2(41, 40), goal=Vec2(30, 40)
                    ),
                ),
                # TODO: Deal with mage enemy here?
                SeqMove2DClunkyCombat(
                    "Trigger plate",
                    coords=_noria_astar.calculate(
                        start=Vec2(30, 39), goal=Vec2(27, 42)
                    ),
                ),
                SeqMenu("Menu manip"),
                SeqDelay(name="Trigger plate", timeout_in_s=0.5),
                SeqMenu("Menu manip"),
                SeqMove2D(name="Menu manip", coords=[Vec2(28.5, 43)]),
                SeqMenu("Menu manip"),
                SeqMove2DClunkyCombat(
                    "Move to chest",
                    coords=_noria_astar.calculate(
                        start=Vec2(29, 43), goal=Vec2(22, 40), final_pos=Vec2(22, 39.6)
                    ),
                ),
                SeqGrabChest("Maze", direction=Facing.UP),
            ],
        )


class NoriaPuzzles(SeqList):
    """Handle movement through the various mazes and puzzles, up until grabbing the boss key."""

    def __init__(self):
        super().__init__(
            name="Puzzles",
            children=[
                SeqMove2DClunkyCombat(
                    "Maze",
                    coords=_noria_astar.calculate(
                        start=Vec2(22, 39), goal=Vec2(27, 24), final_pos=Vec2(27, 23.6)
                    ),
                ),
                SeqGrabChestKeyItem("Key", direction=Facing.UP, manip=True),
                SeqMove2DClunkyCombat(
                    "Maze",
                    coords=_noria_astar.calculate(
                        start=Vec2(27, 24), goal=Vec2(15, 23)
                    ),
                ),
                # TODO: Open door(N)
                SeqMove2D("Door", coords=[Vec2(15, 22)]),
                SeqMove2DClunkyCombat(
                    "Juke skellies",
                    coords=_noria_astar.calculate(
                        start=Vec2(15, 21), goal=Vec2(14, 18)
                    ),
                ),
                # TODO: Better juking so we can avoid fighting the skellies
                SeqMove2DClunkyCombat(
                    "Juke skellies",
                    coords=_noria_astar.calculate(
                        start=Vec2(14, 18), goal=Vec2(9, 14), final_pos=Vec2(9, 13.6)
                    ),
                ),
                SeqGrabChest("Push blocks", direction=Facing.UP),
                SeqMove2DClunkyCombat(
                    "Move to block",
                    coords=_noria_astar.calculate(start=Vec2(9, 14), goal=Vec2(12, 15)),
                ),
                SeqMove2D("Push block", coords=[Vec2(12, 13)]),
                # TODO: Menu manip
                SeqMove2DClunkyCombat(
                    "Move to block",
                    coords=_noria_astar.calculate(start=Vec2(12, 15), goal=Vec2(4, 4)),
                ),
                SeqMove2D("Push block", coords=[Vec2(4, 3)]),
                SeqMove2DClunkyCombat(
                    "Move to block",
                    coords=_noria_astar.calculate(start=Vec2(4, 4), goal=Vec2(11, 4)),
                ),
                SeqMove2D("Push block", coords=[Vec2(11, 3), Vec2(11, 5)]),
                SeqMenu("Menu manip"),
                SeqDelay(name="Menu manip", timeout_in_s=0.5),
                SeqMenu("Menu manip"),
                SeqMove2D("Menu manip", coords=[Vec2(15, 5)]),
                SeqMenu("Menu manip"),
                SeqMove2DClunkyCombat(
                    "Move to trap",
                    coords=_noria_astar.calculate(start=Vec2(15, 5), goal=Vec2(22, 15)),
                ),
                # Skip past skeletons
                SeqMenu("Menu manip"),
                SeqMove2DClunkyCombat(
                    "Move to chest",
                    coords=_noria_astar.calculate(
                        start=Vec2(22, 15), goal=Vec2(22, 17), final_pos=Vec2(22, 17.4)
                    ),
                ),
                SeqGrabChest("GUI", direction=Facing.DOWN),
                SeqMove2DCancel(
                    "Talk",
                    coords=[
                        Vec2(24, 18.5),
                        Vec2(24.5, 18.5),
                        Vec2(25.5, 17.5),
                        Vec2(26, 18),
                    ],
                    precision=0.4,
                ),
                SeqMove2D(
                    "Move to chest",
                    coords=_noria_astar.calculate(
                        start=Vec2(26, 18), goal=Vec2(33, 17), final_pos=Vec2(33, 16.6)
                    ),
                ),
                SeqGrabChest("Pit", direction=Facing.UP),
                # TODO: Code to bump enemy into pit
                # TODO: Menu manip on fall
                SeqManualUntilClose("BUMP ENEMY INTO PIT", target=Vec2(34, 11)),
                # TODO: Remove manual
                SeqMove2D("Move to chest", coords=[Vec2(34, 4.6)]),
                SeqGrabChest("Trick plate", direction=Facing.UP),
                SeqMove2DClunkyCombat(
                    "Trigger plate(R)",
                    coords=_noria_astar.calculate(start=Vec2(34, 5), goal=Vec2(36, 4)),
                ),
                SeqHoldInPlace(
                    name="Trigger plate(R)", target=Vec2(36, 4), timeout_in_s=0.5
                ),
                SeqMove2DClunkyCombat(
                    "Trigger plate(L)",
                    coords=_noria_astar.calculate(start=Vec2(36, 4), goal=Vec2(32, 4)),
                ),
                # TODO: Menu manip
                SeqHoldInPlace(
                    name="Trigger plate(L)", target=Vec2(32, 4), timeout_in_s=0.5
                ),
                # TODO: Just move here? Ignore skellies?
                SeqMove2D(
                    "Move to chest",
                    coords=_noria_astar.calculate(
                        start=Vec2(32, 4), goal=Vec2(38, 14), final_pos=Vec2(38, 14.4)
                    ),
                ),
                SeqGrabChest("Wind trap", direction=Facing.DOWN),
                # TODO: Navigate the wind traps
                SeqManualUntilClose("NAVIGATE WIND TRAPS", target=Vec2(44, 23)),
                # TODO: Remove manual
                # Get in position for chest
                SeqMove2D("Move to chest", coords=[Vec2(44, 22.6)]),
                SeqGrabChest("Puzzle", direction=Facing.UP),
                # TODO: Solve puzzle
                SeqManualUntilClose("SOLVE PUZZLE", target=Vec2(61, 27)),
                # TODO: Remove manual
                # Get in position for chest
                # TODO: Can ignore this key if we do the skip earlier
                SeqMove2D("Move to chest", coords=[Vec2(61.4, 27)]),
                SeqGrabChest("Key", direction=Facing.RIGHT),
                SeqMove2DClunkyCombat(
                    "Move to door",
                    coords=_noria_astar.calculate(
                        start=Vec2(61, 27), goal=Vec2(51, 24)
                    ),
                ),
                # TODO: Open door(N)
                SeqMove2D("Door", coords=[Vec2(51, 23)]),
                SeqMove2DClunkyCombat(
                    "Move to chest",
                    coords=_noria_astar.calculate(
                        start=Vec2(51, 23), goal=Vec2(53, 19), final_pos=Vec2(53, 18.6)
                    ),
                ),
                SeqMove2D("Move to chest", coords=[Vec2(53, 18.6)]),
                SeqGrabChest("Lava", direction=Facing.UP),
                SeqMove2DClunkyCombat(
                    "Move to trigger",
                    coords=_noria_astar.calculate(
                        start=Vec2(53, 18), goal=Vec2(66, 20)
                    ),
                ),
                SeqMove2DCancel("Talk", coords=[Vec2(67, 22)], precision=0.4),
                SeqMove2DClunkyCombat(
                    "Lava Maze",
                    coords=_noria_astar.calculate(
                        start=Vec2(67, 22), goal=Vec2(72, 22)
                    ),
                ),
                SeqAttack("Pot"),
                SeqMove2DClunkyCombat(
                    "Lava Maze", coords=[Vec2(72.5, 22), Vec2(73, 22.5)], precision=0.1
                ),
                SeqMove2DClunkyCombat(
                    "Lava Maze",
                    coords=_noria_astar.calculate(
                        start=Vec2(73, 23),
                        goal=Vec2(70, 26),
                        final_pos=Vec2(69.5, 25.8),
                    ),
                    precision=0.1,
                ),
                SeqAttack("Pot"),
                SeqMove2DClunkyCombat(
                    "Lava Maze", coords=[Vec2(68.5, 25)], precision=0.1
                ),
                SeqMove2DClunkyCombat(
                    "Lava Maze",
                    coords=_noria_astar.calculate(
                        start=Vec2(68, 25), goal=Vec2(70, 30), final_pos=Vec2(70, 30.4)
                    ),
                ),
                SeqGrabChest("Fire maze", direction=Facing.DOWN),
                # TODO: Fire maze! Have fallback for dying here to recover (can also lower health to deathwarp later)
                SeqManualUntilClose("NAVIGATE FIRE MAZE", target=Vec2(70, 51)),
                # TODO: Remove manual
                SeqMove2DClunkyCombat(
                    "Move to chest",
                    coords=_noria_astar.calculate(
                        start=Vec2(70, 51), goal=Vec2(78, 56), final_pos=Vec2(78.4, 56)
                    ),
                ),
                SeqGrabChest("Boss key", direction=Facing.RIGHT),
                # TODO: Deathwarp or kill everything here
                SeqManualUntilClose("GO TO BOSS DOOR", target=Vec2(41, 55)),
                # TODO: Remove manual
            ],
        )


class NoriaBossFight(SeqList):
    """Handle navigating to and defeating Dark Clink, and leaving the Mines for the overworld."""

    def __init__(self):
        super().__init__(
            name="Boss segment",
            children=[
                # SeqMove2DClunkyCombat("Move to door", coords=_noria_astar.calculate(start=Vec2(47, 67), goal=Vec2(41, 55))),
                # Get in position for chest
                # TODO: Open door(N)
                SeqMove2D("Boss door", coords=[Vec2(41, 53)]),
                SeqMove2DClunkyCombat(
                    "Move to trigger",
                    coords=_noria_astar.calculate(
                        start=Vec2(41, 53), goal=Vec2(32, 51)
                    ),
                ),
                SeqMove2DCancel("Talk", coords=[Vec2(32, 54)], precision=0.4),
                SeqMove2DClunkyCombat(
                    "Move to trigger",
                    coords=_noria_astar.calculate(
                        start=Vec2(32, 54), goal=Vec2(27, 62)
                    ),
                ),
                # TODO: Defeat the Dark Clink boss
                SeqManualUntilClose("DEFEAT BOSS", target=Vec2(21, 61)),
                # TODO: Remove manual
                # SeqMove2D("Move to chest", coords=_noria_astar.calculate(start=Vec2(TODO), goal=Vec2(21, 61))),
                # Get in position for chest
                SeqMove2D("Move to chest", coords=[Vec2(21, 60.6)]),
                SeqGrabChest("Buster sword", direction=Facing.UP),
                # TODO: Skip (need to use cancel instead of confirm!)
                SeqMove2DCancel("Talk", coords=[Vec2(21, 69)], precision=0.4),
                SeqZoneTransition(
                    "To overworld", direction=Facing.DOWN, target_zone=MapID.OVERWORLD
                ),
            ],
        )


class NoriaMines(SeqList):
    def __init__(self):
        super().__init__(
            name="Noria Mines",
            children=[
                NoriaToMaze(),
                NoriaPuzzles(),
                NoriaBossFight(),
            ],
        )

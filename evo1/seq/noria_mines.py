from engine.mathlib import Box2, Facing, Vec2
from engine.seq import SeqList
from evo1.combat import SeqCombat3D
from evo1.maps import GetAStar
from evo1.memory import MapID
from evo1.move2d import (
    SeqGrabChest,
    SeqHoldInPlace,
    SeqManualUntilClose,
    SeqMove2D,
    SeqMove2DClunkyCombat,
    SeqMove2DConfirm,
    SeqZoneTransition,
)

_noria_astar = GetAStar(MapID.NORIA)
_noria_start_astar = GetAStar(MapID.NORIA_CLOSED)


# TODO: Improve on the chest grab to be more concise (don't require the approach)
class NoriaMines(SeqList):
    def __init__(self):
        super().__init__(
            name="Noria Mines",
            children=[
                SeqMove2D(
                    "Move to chest",
                    coords=_noria_start_astar.calculate(
                        start=Vec2(47, 67), goal=Vec2(46, 56)
                    ),
                ),
                # Get in position for chest
                SeqMove2D("Move to chest", coords=[Vec2(46, 55.6)]),
                SeqGrabChest("Opening the mines", direction=Facing.UP),
                # TODO: Navigate through the Mines, solving puzzles
                SeqMove2DClunkyCombat(
                    "Move to chest",
                    coords=_noria_astar.calculate(
                        start=Vec2(46, 55), goal=Vec2(51, 48)
                    ),
                ),
                # Get in position for chest
                SeqMove2D("Move to chest", coords=[Vec2(51, 47.6)]),
                SeqGrabChest("Breakable pots", direction=Facing.UP),
                SeqMove2DClunkyCombat(
                    "Move to chest",
                    coords=_noria_astar.calculate(
                        start=Vec2(51, 47), goal=Vec2(54, 40)
                    ),
                ),
                # Get in position for chest
                SeqMove2D("Move to chest", coords=[Vec2(54, 39.6)]),
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
                SeqHoldInPlace(
                    name="Trigger plate(R)", target=Vec2(58, 37), timeout_in_s=0.5
                ),
                SeqMove2DClunkyCombat(
                    "Move to chest",
                    coords=_noria_astar.calculate(
                        start=Vec2(58, 37), goal=Vec2(48, 45)
                    ),
                ),
                # Get in position for chest
                SeqMove2D("Move to chest", coords=[Vec2(48, 44.6)]),
                SeqGrabChest("Red Mage", direction=Facing.UP),
                SeqMove2DClunkyCombat(
                    "Move to chest",
                    coords=_noria_astar.calculate(
                        start=Vec2(48, 44), goal=Vec2(35, 41)
                    ),
                ),
                # Get in position for chest
                SeqMove2D("Move to chest", coords=[Vec2(35, 40.6)]),
                # TODO: Trigger menu bug
                SeqGrabChest("Trap room", direction=Facing.UP),
                # TODO: Test killing bat
                # TODO: Kill bats if needed (can reuse knight logic, simplify)
                SeqCombat3D(
                    "Killing bats", arena=Box2(Vec2(33, 41), w=5, h=6), num_targets=3
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
                        start=Vec2(41, 41), goal=Vec2(41, 40)
                    ),
                ),
                # Get in position for chest
                SeqMove2D("Move to chest", coords=[Vec2(41, 39.6)]),
                SeqGrabChest("Skellies", direction=Facing.UP),
                SeqMove2DClunkyCombat(
                    "Move to trigger",
                    coords=_noria_astar.calculate(
                        start=Vec2(41, 40), goal=Vec2(31, 38)
                    ),
                ),
                SeqMove2DConfirm("Talking", coords=[Vec2(30, 39)]),
                # TODO: Deal with mage enemy here?
                SeqMove2DClunkyCombat(
                    "Trigger plate",
                    coords=_noria_astar.calculate(
                        start=Vec2(30, 39), goal=Vec2(27, 42)
                    ),
                ),
                SeqHoldInPlace(
                    name="Trigger plate", target=Vec2(27, 42), timeout_in_s=0.5
                ),
                SeqMove2DClunkyCombat(
                    "Move to chest",
                    coords=_noria_astar.calculate(
                        start=Vec2(27, 42), goal=Vec2(22, 40)
                    ),
                ),
                # Get in position for chest
                SeqMove2D("Move to chest", coords=[Vec2(22, 39.6)]),
                SeqGrabChest("Maze", direction=Facing.UP),
                SeqMove2DClunkyCombat(
                    "Maze",
                    coords=_noria_astar.calculate(
                        start=Vec2(22, 39), goal=Vec2(27, 24)
                    ),
                ),
                # Get in position for chest
                SeqMove2D("Move to chest", coords=[Vec2(27, 23.6)]),
                SeqGrabChest("Key", direction=Facing.UP),
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
                SeqMove2DClunkyCombat(
                    "Juke skellies",
                    coords=_noria_astar.calculate(start=Vec2(14, 18), goal=Vec2(9, 14)),
                ),
                # Get in position for chest
                SeqMove2D("Move to chest", coords=[Vec2(9, 13.6)]),
                SeqGrabChest("Push blocks", direction=Facing.UP),
                SeqMove2DClunkyCombat(
                    "Move to block",
                    coords=_noria_astar.calculate(start=Vec2(9, 14), goal=Vec2(12, 15)),
                ),
                SeqMove2D("Push block", coords=[Vec2(12, 13)]),
                SeqMove2DClunkyCombat(
                    "Move to block",
                    coords=_noria_astar.calculate(start=Vec2(12, 15), goal=Vec2(4, 4)),
                ),
                SeqMove2D("Push block", coords=[Vec2(4, 3)]),
                SeqMove2DClunkyCombat(
                    "Move to block",
                    coords=_noria_astar.calculate(start=Vec2(4, 4), goal=Vec2(11, 4)),
                ),
                SeqMove2D("Push block", coords=[Vec2(11, 3)]),
                SeqMove2DClunkyCombat(
                    "Move to trap",
                    coords=_noria_astar.calculate(start=Vec2(11, 4), goal=Vec2(22, 15)),
                ),
                # TODO: Kill skellies (reuse knight combat) [19|20|21, 12]
                SeqManualUntilClose("KILL SKELLIES", target=Vec2(22, 17)),
                # TODO: Remove manual
                SeqMove2DClunkyCombat(
                    "Move to chest",
                    coords=_noria_astar.calculate(
                        start=Vec2(22, 15), goal=Vec2(22, 17)
                    ),
                ),
                # Get in position for chest
                SeqMove2D("Move to chest", coords=[Vec2(22, 17.4)]),
                SeqGrabChest("GUI", direction=Facing.DOWN),
                SeqMove2DConfirm("Talk", coords=[Vec2(26, 18)]),
                SeqMove2DClunkyCombat(
                    "Move to chest",
                    coords=_noria_astar.calculate(
                        start=Vec2(26, 18), goal=Vec2(33, 17)
                    ),
                ),
                # Get in position for chest
                SeqMove2D("Move to chest", coords=[Vec2(33, 16.6)]),
                SeqGrabChest("Pit", direction=Facing.UP),
                # TODO: Code to bump enemy into pit
                SeqManualUntilClose("BUMP ENEMY INTO PIT", target=Vec2(34, 5)),
                # TODO: Remove manual
                SeqMove2DClunkyCombat(
                    "Trigger plate(L)",
                    coords=_noria_astar.calculate(start=Vec2(34, 5), goal=Vec2(32, 4)),
                ),
                SeqHoldInPlace(
                    name="Trigger plate(L)", target=Vec2(32, 4), timeout_in_s=0.5
                ),
                SeqMove2DClunkyCombat(
                    "Trigger plate(R)",
                    coords=_noria_astar.calculate(start=Vec2(32, 4), goal=Vec2(36, 4)),
                ),
                SeqHoldInPlace(
                    name="Trigger plate(R)", target=Vec2(36, 4), timeout_in_s=0.5
                ),
                # TODO: Just move here? Ignore skellies?
                SeqMove2DClunkyCombat(
                    "Move to chest",
                    coords=_noria_astar.calculate(start=Vec2(36, 4), goal=Vec2(38, 14)),
                ),
                # Get in position for chest
                SeqMove2D("Move to chest", coords=[Vec2(38, 14.4)]),
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
                        start=Vec2(51, 23), goal=Vec2(53, 19)
                    ),
                ),
                # Get in position for chest
                SeqMove2D("Move to chest", coords=[Vec2(53, 18.6)]),
                SeqGrabChest("Lava", direction=Facing.UP),
                SeqMove2DClunkyCombat(
                    "Move to trigger",
                    coords=_noria_astar.calculate(
                        start=Vec2(53, 18), goal=Vec2(66, 20)
                    ),
                ),
                SeqMove2DConfirm("Talk", coords=[Vec2(67, 22)]),
                # TODO: Maze with pots! Have fallback for dying here to recover
                SeqManualUntilClose("NAVIGATE LAVA MAZE", target=Vec2(67, 30)),
                # TODO: Remove manual
                # Get in position for chest
                SeqMove2D("Move to chest", coords=[Vec2(67, 30.4)]),
                SeqGrabChest("Wind trap", direction=Facing.DOWN),
                # TODO: Fire maze! Have fallback for dying here to recover (can also lower health to deathwarp later)
                SeqManualUntilClose("NAVIGATE FIRE MAZE", target=Vec2(70, 51)),
                # TODO: Remove manual
                SeqMove2DClunkyCombat(
                    "Move to chest",
                    coords=_noria_astar.calculate(
                        start=Vec2(70, 51), goal=Vec2(78, 56)
                    ),
                ),
                # Get in position for chest
                SeqMove2D("Move to chest", coords=[Vec2(78.4, 56)]),
                SeqGrabChest("Boss key", direction=Facing.RIGHT),
                # TODO: Deathwarp or kill everything here
                SeqManualUntilClose("GO TO BOSS DOOR", target=Vec2(41, 55)),
                # TODO: Remove manual
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
                SeqMove2DConfirm("Talk", coords=[Vec2(32, 54)]),
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
                SeqMove2DConfirm("Talk", coords=[Vec2(21, 69)]),
                SeqZoneTransition(
                    "To overworld", direction=Facing.DOWN, target_zone=MapID.OVERWORLD
                ),
            ],
        )

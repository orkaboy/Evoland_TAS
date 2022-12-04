from engine.seq import SeqList
from engine.mathlib import Facing, Vec2
from evo1.move2d import SeqZoneTransition, SeqGrabChest, SeqGrabChestKeyItem, SeqMove2D, SeqMove2DClunkyCombat, SeqMove2DConfirm, SeqHoldInPlace
from evo1.maps import GetAStar
from evo1.memory import MapID

_noria_astar = GetAStar(MapID.NORIA)
_noria_start_astar = GetAStar(MapID.NORIA_CLOSED)

# TODO: Improve on the chest grab to be more concise (don't require the approach)
class NoriaMines(SeqList):
    def __init__(self):
        super().__init__(
            name="Noria Mines",
            children=[
                SeqMove2D("Move to chest", coords=_noria_start_astar.calculate(start=Vec2(47, 67), goal=Vec2(46, 56))),
                # Get in position for chest
                SeqMove2D("Move to chest", coords=[Vec2(46, 55.6)]),
                SeqGrabChest("Opening the mines", direction=Facing.UP),
                # TODO: Navigate through the Mines, solving puzzles
                SeqMove2DClunkyCombat("Move to chest", coords=_noria_astar.calculate(start=Vec2(46, 55), goal=Vec2(51, 48))),
                # Get in position for chest
                SeqMove2D("Move to chest", coords=[Vec2(51, 47.6)]),
                SeqGrabChest("Breakable pots", direction=Facing.UP),
                SeqMove2DClunkyCombat("Move to chest", coords=_noria_astar.calculate(start=Vec2(51, 47), goal=Vec2(54, 40))),
                # Get in position for chest
                SeqMove2D("Move to chest", coords=[Vec2(54, 39.6)]),
                SeqGrabChest("Pressure plates", direction=Facing.UP),
                SeqMove2DClunkyCombat("Trigger plate(L)", coords=_noria_astar.calculate(start=Vec2(54, 39), goal=Vec2(50, 37))),
                SeqHoldInPlace(name="Trigger plate(L)", target=Vec2(50, 37), timeout_in_s=0.5),
                SeqMove2DClunkyCombat("Trigger plate(R)", coords=_noria_astar.calculate(start=Vec2(50, 37), goal=Vec2(58, 37))),
                SeqHoldInPlace(name="Trigger plate(R)", target=Vec2(58, 37), timeout_in_s=0.5),
                SeqMove2DClunkyCombat("Move to chest", coords=_noria_astar.calculate(start=Vec2(58, 37), goal=Vec2(48, 45))),
                # Get in position for chest
                SeqMove2D("Move to chest", coords=[Vec2(48, 44.6)]),
                SeqGrabChest("Red Mage", direction=Facing.UP),
                SeqMove2DClunkyCombat("Move to chest", coords=_noria_astar.calculate(start=Vec2(48, 44), goal=Vec2(35, 41))),
                # Get in position for chest
                SeqMove2D("Move to chest", coords=[Vec2(35, 40.6)]),
                # TODO: Trigger menu bug
                SeqGrabChest("Trap room", direction=Facing.UP),
                SeqMove2DClunkyCombat("Move to chest", coords=_noria_astar.calculate(start=Vec2(35, 41), goal=Vec2(34, 41))),
                # TODO: Kill bats if needed (can reuse knight logic, simplify)
                # Get in position for chest
                SeqMove2D("Move to chest", coords=[Vec2(33.6, 41)]),
                SeqGrabChestKeyItem("Key", direction=Facing.LEFT),
                SeqMove2DClunkyCombat("Move to door", coords=_noria_astar.calculate(start=Vec2(37, 44), goal=Vec2(41, 42))),
                # TODO: Open door(N)
                SeqMove2DClunkyCombat("Move to chest", coords=_noria_astar.calculate(start=Vec2(41, 41), goal=Vec2(41, 40))),
                # Get in position for chest
                SeqMove2D("Move to chest", coords=[Vec2(41, 39.6)]),
                SeqGrabChest("Skellies", direction=Facing.UP),
                SeqMove2DClunkyCombat("Move to trigger", coords=_noria_astar.calculate(start=Vec2(41, 40), goal=Vec2(31, 38))),
                SeqMove2DConfirm("Talking", coords=[Vec2(30, 39)]),
                # TODO: Mage enemy here?
                SeqMove2DClunkyCombat("Trigger plate", coords=_noria_astar.calculate(start=Vec2(30, 39), goal=Vec2(27, 42))),
                SeqHoldInPlace(name="Trigger plate", target=Vec2(27, 42), timeout_in_s=0.5),
                SeqMove2DClunkyCombat("Move to chest", coords=_noria_astar.calculate(start=Vec2(27, 42), goal=Vec2(22, 40))),
                # Get in position for chest
                SeqMove2D("Move to chest", coords=[Vec2(22, 39.6)]),
                SeqGrabChest("Maze", direction=Facing.UP),
                # TODO: Navigate Maze/Puzzles
                SeqMove2DClunkyCombat("Maze", coords=_noria_astar.calculate(start=Vec2(22, 39), goal=Vec2(27, 24))),
                # TODO: The TAS should abuse the menu bug and potentially deathwarp here (see speedrun)
                # TODO: Fight shadow Clink boss
            ],
        )

from engine.seq import SeqList
from engine.mathlib import Facing, Vec2
from engine.navmap import NavMap, AStar
from evo1.move2d import SeqZoneTransition, SeqGrabChest3D, SeqMove2D, SeqMove2DClunkyCombat, SeqMove2DConfirm

_noria_map = NavMap("evo1/maps/noria_mines.yaml")
_noria_astar = AStar(_noria_map.map)

_noria_start_map = NavMap("evo1/maps/noria_start.yaml")
_noria_start_astar = AStar(_noria_start_map.map)


# TODO: Improve on the chest grab to be more concise (don't require the approach)
class NoriaMines(SeqList):
    def __init__(self):
        super().__init__(
            name="Noria Mines",
            children=[
                SeqMove2D("Move to chest", coords=_noria_start_astar.calculate(start=Vec2(47, 67), goal=Vec2(46, 56)), tilemap=_noria_start_map),
                # Get in position for chest
                SeqMove2D("Move to chest", coords=[Vec2(46, 55.6)]),
                SeqGrabChest3D("Opening the mines", direction=Facing.UP),
                # TODO: Navigate through the Mines, solving puzzles
                SeqMove2DClunkyCombat("Move to chest", coords=_noria_astar.calculate(start=Vec2(46, 55), goal=Vec2(51, 48)), tilemap=_noria_map),
                # Get in position for chest
                SeqMove2D("Move to chest", coords=[Vec2(51, 47.6)]),
                SeqGrabChest3D("Breakable pots", direction=Facing.UP),
                SeqMove2DClunkyCombat("Move to chest", coords=_noria_astar.calculate(start=Vec2(51, 47), goal=Vec2(54, 40)), tilemap=_noria_map),
                # Get in position for chest
                SeqMove2D("Move to chest", coords=[Vec2(54, 39.6)]),
                SeqGrabChest3D("Pressure plates", direction=Facing.UP),
                SeqMove2DClunkyCombat("Trigger plate(L)", coords=_noria_astar.calculate(start=Vec2(54, 39), goal=Vec2(50, 37)), tilemap=_noria_map),
                SeqMove2DClunkyCombat("Trigger plate(R)", coords=_noria_astar.calculate(start=Vec2(50, 37), goal=Vec2(58, 37)), tilemap=_noria_map),
                SeqMove2DClunkyCombat("Move to chest", coords=_noria_astar.calculate(start=Vec2(58, 37), goal=Vec2(48, 45)), tilemap=_noria_map),
                # Get in position for chest
                SeqMove2D("Move to chest", coords=[Vec2(48, 44.6)]),
                SeqGrabChest3D("Red Mage", direction=Facing.UP),
                SeqMove2DClunkyCombat("Move to chest", coords=_noria_astar.calculate(start=Vec2(48, 44), goal=Vec2(35, 41)), tilemap=_noria_map),
                # Get in position for chest
                SeqMove2D("Move to chest", coords=[Vec2(35, 40.6)]),
                # TODO: Trigger menu bug
                SeqGrabChest3D("Trap room", direction=Facing.UP),
                SeqMove2DClunkyCombat("Move to chest", coords=_noria_astar.calculate(start=Vec2(35, 41), goal=Vec2(34, 41)), tilemap=_noria_map),
                # TODO: Kill bats if needed (can reuse knight logic, simplify)
                # Get in position for chest
                SeqMove2D("Move to chest", coords=[Vec2(33.6, 41)]),
                SeqGrabChest3D("Key", direction=Facing.LEFT),
                SeqMove2DClunkyCombat("Move to door", coords=_noria_astar.calculate(start=Vec2(37, 44), goal=Vec2(41, 42)), tilemap=_noria_map),
                # TODO: Open door(N)
                SeqMove2DClunkyCombat("Move to chest", coords=_noria_astar.calculate(start=Vec2(41, 41), goal=Vec2(41, 40)), tilemap=_noria_map),
                # Get in position for chest
                SeqMove2D("Move to chest", coords=[Vec2(41, 39.6)]),
                SeqGrabChest3D("Skellies", direction=Facing.UP),
                SeqMove2DClunkyCombat("Move to trigger", coords=_noria_astar.calculate(start=Vec2(41, 40), goal=Vec2(31, 38)), tilemap=_noria_map),
                SeqMove2DConfirm("Talking", coords=[Vec2(30, 39)], tilemap=_noria_map),
                # TODO: Mage enemy here?
                SeqMove2DClunkyCombat("Trigger plate", coords=_noria_astar.calculate(start=Vec2(30, 39), goal=Vec2(27, 42)), tilemap=_noria_map),
                SeqMove2DClunkyCombat("Move to chest", coords=_noria_astar.calculate(start=Vec2(27, 42), goal=Vec2(22, 40)), tilemap=_noria_map),
                # Get in position for chest
                SeqMove2D("Move to chest", coords=[Vec2(22, 39.6)]),
                SeqGrabChest3D("Maze", direction=Facing.UP),
                # TODO: Navigate Maze/Puzzles
                # TODO: The TAS should abuse the menu bug and potentially deathwarp here (see speedrun)
                # TODO: Fight shadow Clink boss
            ],
        )

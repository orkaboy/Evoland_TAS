from engine.seq import SeqList
from engine.mathlib import Facing, Vec2
from engine.navmap import NavMap, AStar
from evo1.move2d import SeqZoneTransition, SeqGrabChest3D, SeqMove2D

_noria_map = NavMap("evo1/maps/noria_mines.yaml")
_noria_astar = AStar(_noria_map.map)


class NoriaMines(SeqList):
    def __init__(self):
        super().__init__(
            name="Noria Mines",
            children=[
                SeqMove2D("Move to chest", coords=_noria_astar.calculate(start=Vec2(47, 67), goal=Vec2(46, 56)), tilemap=_noria_map),
                # Get in position for chest
                SeqMove2D("Move to chest", coords=[Vec2(46, 55.6)]),
                SeqGrabChest3D("Opening the mines", direction=Facing.UP),
                # TODO: Navigate through the Mines, solving puzzles
                # TODO: The TAS should abuse the menu bug and potentially deathwarp here (see speedrun)
                # TODO: Fight shadow Clink boss
            ],
        )

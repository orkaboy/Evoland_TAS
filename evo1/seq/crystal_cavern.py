from engine.seq import SeqList, SeqDelay
from engine.mathlib import Facing, Vec2
from engine.navmap import NavMap, AStar
from evo1.move2d import SeqGrabChest, SeqMove2D, SeqZoneTransition
from evo1.atb import SeqATBmove2D
from evo1.interact import SeqInteract

_cavern_map = NavMap("evo1/maps/crystal_cavern.yaml")
_cavern_astar = AStar(map_nodes=_cavern_map.map)

class CrystalCavern(SeqList):
    def __init__(self):
        super().__init__(
            name="Crystal Cavern",
            children=[
                SeqATBmove2D(name="Move to chest", tilemap=_cavern_map, coords=_cavern_astar.calculate(Vec2(24, 77), Vec2(18, 39))),
                SeqGrabChest("Experience", Facing.UP),
                SeqATBmove2D(name="Move to trigger", tilemap=_cavern_map, coords=_cavern_astar.calculate(Vec2(18, 39), Vec2(54, 37))),
                SeqMove2D(name="Trigger plate", tilemap=_cavern_map, coords=[Vec2(54, 36.5)]),
                SeqInteract(name="Trigger plate", timeout_in_s=0.5),
                SeqATBmove2D(name="Move to boss", tilemap=_cavern_map, coords=_cavern_astar.calculate(Vec2(54, 37), Vec2(49, 9))),
                # TODO: Trigger fight against Kefka's ghost (interact with crystal)
                # TODO: Fight against Kefka's ghost (need to implement a smarter combat function to avoid the boss counter)
                # TODO: Grab the crystal and become 3D
                SeqMove2D(name="Move to portal", coords=[Vec2(7, 6)]),
                SeqZoneTransition("Enter the third dimension", Facing.UP, timeout_in_s=1.0),
            ],
        )

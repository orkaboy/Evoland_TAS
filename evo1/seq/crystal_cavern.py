from engine.seq import SeqList
from engine.mathlib import Facing, Vec2
from engine.navmap import NavMap, AStar
from evo1.move2d import SeqGrabChest, SeqMove2D, SeqZoneTransition, SeqHoldInPlace, SeqManualUntilClose
from evo1.interact import SeqInteract
from evo1.atb import SeqATBmove2D

_cavern_map = NavMap("evo1/maps/crystal_cavern.yaml")
_cavern_astar = AStar(map_nodes=_cavern_map.map)

_limbo_map = NavMap("evo1/maps/limbo.yaml")
_limbo_astar = AStar(map_nodes=_limbo_map.map)

class CrystalCavern(SeqList):
    def __init__(self):
        super().__init__(
            name="Crystal Cavern",
            children=[
                SeqATBmove2D(name="Move to chest", tilemap=_cavern_map, coords=_cavern_astar.calculate(start=Vec2(24, 77), goal=Vec2(18, 39))),
                SeqGrabChest("Experience", Facing.UP),
                SeqATBmove2D(name="Move to trigger", tilemap=_cavern_map, coords=_cavern_astar.calculate(start=Vec2(18, 38), goal=Vec2(54, 36))),
                SeqHoldInPlace(name="Trigger plate", target=Vec2(54, 36.5), timeout_in_s=0.5),
                SeqATBmove2D(name="Move to boss", tilemap=_cavern_map, coords=_cavern_astar.calculate(start=Vec2(54, 36), goal=Vec2(49, 9))),
                # TODO: Trigger fight against Kefka's ghost (interact with crystal)
                # TODO: Fight against Kefka's ghost (need to implement a smarter combat function to avoid the boss counter)
                SeqManualUntilClose(name="Kefka's Ghost", target=Vec2(7, 10)),
                # TODO: Grab the crystal and become 3D
                # Limbo realm
                #SeqInteract(name="Story stuff", timeout_in_s=0.5),
                SeqMove2D(name="Move to portal", tilemap=_limbo_map, coords=_limbo_astar.calculate(start=Vec2(7, 10), goal=Vec2(7, 6))),
                SeqZoneTransition("Enter the third dimension", Facing.UP, timeout_in_s=1.0),
            ],
        )

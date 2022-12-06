from engine.seq import SeqList
from engine.mathlib import Facing, Vec2
from evo1.maps import GetAStar
from evo1.move2d import SeqGrabChest, SeqMove2D, SeqZoneTransition, SeqHoldInPlace, SeqManualUntilClose
from evo1.atb import SeqATBmove2D, SeqATBCombatManual
from evo1.memory import MapID

_cavern_astar = GetAStar(MapID.CRYSTAL_CAVERN)
_limbo_astar = GetAStar(MapID.LIMBO)

class CrystalCavern(SeqList):
    def __init__(self):
        super().__init__(
            name="Crystal Cavern",
            children=[
                SeqATBmove2D(name="Move to chest", coords=_cavern_astar.calculate(start=Vec2(24, 77), goal=Vec2(18, 39))),
                SeqGrabChest("Experience", Facing.UP),
                SeqATBmove2D(name="Move to trigger", coords=_cavern_astar.calculate(start=Vec2(18, 38), goal=Vec2(54, 36))),
                SeqHoldInPlace(name="Trigger plate", target=Vec2(54, 36.5), timeout_in_s=0.5),
                SeqATBmove2D(name="Move to boss", coords=_cavern_astar.calculate(start=Vec2(54, 36), goal=Vec2(49, 9))),
                # Trigger fight against Kefka's ghost (interact with crystal)
                # TODO: Doesn't fully work (doesn't detect start of battle correctly)
                #SeqATBCombatManual(name="Kefka's Ghost", wait_for_battle=True),
                # TODO: Fight against Kefka's ghost (need to implement a smarter combat function to avoid the boss counter)
                SeqManualUntilClose(name="Kefka's Ghost", target=Vec2(7, 10)),
                # TODO: Grab the crystal and become 3D
                # Limbo realm
                #SeqInteract(name="Story stuff", timeout_in_s=0.5),
                SeqMove2D(name="Move to portal", coords=_limbo_astar.calculate(start=Vec2(7, 10), goal=Vec2(7, 6))),
                SeqZoneTransition("Enter the third dimension", Facing.UP, target_zone=MapID.EDEL_VALE),
            ],
        )

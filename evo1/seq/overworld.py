from engine.seq import SeqList
from engine.mathlib import Facing, Vec2
from evo1.atb import SeqATBmove2D, FarmingGoal
from evo1.move2d import SeqZoneTransition, SeqGrabChest, SeqMove2D
from evo1.memory import MapID
from evo1.maps import GetAStar

_overworld_astar = GetAStar(MapID.OVERWORLD)


class OverworldToMeadow(SeqList):
    def __init__(self):
        super().__init__(
            name="Overworld",
            children=[
                # TODO: Movement is awkward, would look better with joystick move instead of dpad?
                # Battle handler for random battles, mashing confirm is fine for now
                SeqATBmove2D(
                    "Navigating overworld",
                    coords=[
                        Vec2(79.7, 54.8),
                        # Nudge chest (encounters) at (79, 54)
                        # TODO: Adjust, a bit akward
                        Vec2(79.5, 53),
                        Vec2(85, 47),
                        Vec2(87, 43),
                    ],
                    # Need to farm gli before progressing. We need 250 to buy gear, and we can get 50 in the village
                    goal=FarmingGoal(farm_coords=[Vec2(87, 44), Vec2(87, 43)], precision=0.2, gli_goal=200)
                ),
                SeqZoneTransition("Meadow", direction=Facing.UP, target_zone=MapID.MEADOW),
            ],
        )

class OverworldToCavern(SeqList):
    def __init__(self):
        super().__init__(
            name="Overworld",
            children=[
                # Grab the forced combat chest and rescue/name Kaeris
                SeqATBmove2D(
                    "Picking up Kaeris",
                    coords=_overworld_astar.calculate(start=Vec2(87, 40), goal=Vec2(79, 35))
                ),
                # Move into the caverns
                SeqZoneTransition("Crystal Cavern", direction=Facing.UP, target_zone=MapID.CRYSTAL_CAVERN)
            ]
        )


class OverworldToNoria(SeqList):
    def __init__(self):
        super().__init__(
            name="Overworld",
            children=[
                SeqMove2D("Move to chest", coords=_overworld_astar.calculate(start=Vec2(79, 73), goal=Vec2(78, 76))),
                SeqGrabChest("Perspective", direction=Facing.LEFT),
                SeqMove2D("Move to mines", coords=_overworld_astar.calculate(start=Vec2(78, 76), goal=Vec2(75, 79))),
                SeqZoneTransition("Noria Mines", direction=Facing.LEFT, target_zone=MapID.NORIA_CLOSED),
            ]
        )

class OverworldToAogai(SeqList):
    def __init__(self):
        super().__init__(
            name="Overworld",
            children=[
                SeqMove2D("Performing skip", coords=[Vec2(75, 84.95), Vec2(78, 84.95)], precision=0.05),
                SeqMove2D("Moving to Aogai", coords=_overworld_astar.calculate(start=Vec2(78, 85), goal=Vec2(95, 93))),
                SeqZoneTransition("Aogai village", direction=Facing.UP, target_zone=MapID.AOGAI),
            ]
        )

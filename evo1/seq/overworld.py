from engine.seq import SeqList
from engine.mathlib import Facing, Vec2
from engine.navmap import NavMap, AStar
from evo1.atb import SeqATBmove2D, FarmingGoal
from evo1.move2d import SeqZoneTransition

_overworld_map = NavMap("evo1/maps/overworld.yaml")
_overworld_astar = AStar(_overworld_map.map)


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
                    goal=FarmingGoal(farm_coords=[Vec2(87, 44), Vec2(87, 43)], precision=0.2, gli_goal=200),
                    tilemap=_overworld_map
                ),
                SeqZoneTransition("Meadow", direction=Facing.UP, time_in_s=1.0),
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
                    coords=_overworld_astar.calculate(start=Vec2(87, 40), goal=Vec2(79, 35)),
                    tilemap=_overworld_map
                ),
                # Move into the caverns
                SeqZoneTransition("Crystal Cavern", direction=Facing.UP, time_in_s=1.0)
            ]
        )


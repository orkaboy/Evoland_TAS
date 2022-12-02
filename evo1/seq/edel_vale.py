from engine.seq import SeqDelay, SeqList
from engine.mathlib import Facing, Vec2, Box2
from engine.navmap import NavMap, AStar
from evo1.move2d import SeqAttack, SeqGrabChest, SeqMove2D, SeqMove2DClunkyCombat, SeqZoneTransition
from evo1.knights import SeqKnight2D


_edel_vale_map = NavMap("evo1/maps/edel_vale.yaml")
_edel_vale_astar = AStar(_edel_vale_map.map)


class Edel1(SeqList):
    def __init__(self):
        super().__init__(
            name="Edel Vale",
            children=[
                SeqMove2D("Move to chest", coords=[Vec2(14, 52)], tilemap=_edel_vale_map),
                SeqGrabChest("Move Left", direction=Facing.RIGHT),
                SeqMove2D("Move to chest", coords=[Vec2(11, 52)], tilemap=_edel_vale_map),
                SeqGrabChest("Move Vertical", direction=Facing.LEFT),
                SeqMove2D("Move to chest", coords=[Vec2(12, 52), Vec2(12, 51)], tilemap=_edel_vale_map),
                SeqGrabChest("Basic Scroll", direction=Facing.UP),
                SeqMove2D(
                    "Move to chest",
                    coords=_edel_vale_astar.calculate(start=Vec2(12, 51), goal=Vec2(20, 52)),
                    tilemap=_edel_vale_map
                ),
                SeqGrabChest("Smooth Scroll", direction=Facing.LEFT),
                SeqMove2D(
                    "Move to sword",
                    coords=_edel_vale_astar.calculate(start=Vec2(20, 52), goal=Vec2(30, 60)),
                    tilemap=_edel_vale_map
                ),
                SeqGrabChest("Sword", direction=Facing.DOWN),
                SeqMove2D(
                    "Move to bush",
                    coords=_edel_vale_astar.calculate(start=Vec2(30, 60), goal=Vec2(31, 55)),
                    tilemap=_edel_vale_map
                ),
                SeqAttack("Bush"),
                SeqMove2D("Move to chest", coords=[Vec2(32, 55)], tilemap=_edel_vale_map),
                SeqGrabChest("Monsters", direction=Facing.RIGHT),
                SeqMove2DClunkyCombat(
                    "Dodge enemies",
                    coords=_edel_vale_astar.calculate(start=Vec2(32, 55), goal=Vec2(39, 52)),
                    tilemap=_edel_vale_map
                ),
                SeqGrabChest("Music", direction=Facing.RIGHT), # TODO: optionally grab?
                SeqAttack("Bush"),
                SeqMove2D("Move past bush", coords=[Vec2(39, 50)], tilemap=_edel_vale_map),
                SeqMove2DClunkyCombat(
                    "Move to chest",
                    coords=_edel_vale_astar.calculate(start=Vec2(39, 50), goal=Vec2(44, 49)),
#                                coords=[
#                                    Vec2(39, 47),
#                                    # TODO Optional, chest to the north, save (move to Vec2(39, 45), then open chest N)
#                                    Vec2(41, 47),
#                                    Vec2(41, 48),
#                                    Vec2(44, 48),
#                                    Vec2(44, 49),
#                                ],
                    tilemap=_edel_vale_map
                ),
                SeqGrabChest("16-bit", direction=Facing.DOWN),
                # TODO: Some enemies here, will probably fail
                SeqMove2DClunkyCombat(
                    "Dodge enemies",
                    coords=_edel_vale_astar.calculate(start=Vec2(44, 49), goal=Vec2(34, 33)),
                    tilemap=_edel_vale_map
                ),
                SeqGrabChest("Free move", direction=Facing.LEFT),
                # TODO: At this point we can move more freely, could implement a better move2d (or improve current)
                SeqMove2DClunkyCombat(
                    "Navigate to rocks",
                    coords=[
                        # TODO: Implement Boid-type behavior to avoid enemies that approach?
                        # Move to rocks, dodging enemies
                        Vec2(33.5, 33),
                        Vec2(36, 35.7),
                        Vec2(48, 36),
                        Vec2(50, 36.5),
                    ],
                    tilemap=_edel_vale_map
                ),
                # Don't use attack behavior on this part
                SeqMove2D(
                    "Navigate to knights",
                    coords=[
                        # Navigating past the rocks
                        Vec2(51, 36.5),
                        Vec2(52, 36.5),
                        Vec2(53, 36),
                        Vec2(54.1, 33.5),  # Near left knight
                    ],
                    tilemap=_edel_vale_map
                ),
                # TODO: Optional save point?
                SeqMove2D(
                    "Nudging the knights",
                    precision=0.1,
                    coords=[
                        Vec2(55, 33),  # Nudge past left knight to activate
                        Vec2(55.5, 33.1),  # Approach right knight
                        Vec2(56, 34),  # Nudge past right knight to activate
                        Vec2(55, 35),  # Retreat and prepare for combat!
                    ],
                    tilemap=_edel_vale_map
                ),
                # We need to kill two knights. These enemies must be killed with 3 attacks, but cannot be harmed from the front.
                SeqKnight2D(
                    "Killing two knights", # TODO: Everything is fully tracked, but the enemies have to be killed manually for now. TAS resumes when all enemies are dead
                    arena=Box2(pos=Vec2(53, 32), w=5, h=4), # Valid arena to fight inside (should be clear of obstacles)
                    targets=[Vec2(54, 33), Vec2(56, 33)], # Positions of enemies (known from start)
                    tilemap=_edel_vale_map,
                ),
                SeqMove2D(
                    "Grabbing inv",
                    coords=[
                        Vec2(54, 31),
                        # TODO: Grab chest (Inv)
                        Vec2(54, 29),
                    ],
                    tilemap=_edel_vale_map
                ),
                SeqZoneTransition("Overworld", direction=Facing.UP, timeout_in_s=1.0),
            ],
        )






# TODO REMOVE when knight fight is implemented fully
class EdelExperimental(SeqList):
    def __init__(self):
        super().__init__(
            name="Knights",
            children=[
                # TODO: This appears to be needed on load for some reason, or the game crashes
                SeqDelay("Memory delay", timeout_in_s=1.0),
                # TODO: DUMMY SEQUENCE, DO NOT USE UNLESS LOADING FROM SAVEPOINT
                SeqMove2D(
                    "Navigate to knights",
                    coords=[
                        Vec2(52, 36.5),
                        Vec2(53, 36),
                        Vec2(54.1, 33.5),  # Near left knight
                    ],
                    tilemap=_edel_vale_map
                ),
                # TODO: Keep testing from here
                SeqMove2D(
                    "Nudging the knights",
                    precision=0.1,
                    coords=[
                        Vec2(55, 33),  # Nudge past left knight to activate
                        Vec2(55.5, 33.1),  # Approach right knight
                        Vec2(56, 34),  # Nudge past right knight to activate
                        Vec2(55, 35),  # Retreat and prepare for combat!
                    ],
                    tilemap=_edel_vale_map
                ),
                # TODO: We need to kill two knights. These enemies must be killed with 3 attacks, but cannot be harmed from the front.
                # TODO: Need to get hold of the enemies in question so we know when they are dead. Need to strategize for the best way to kill them without dying.
                SeqKnight2D(
                    "Killing two knights",
                    arena=Box2(pos=Vec2(53, 32), w=5, h=4), # Valid arena to fight inside (should be clear of obstacles)
                    targets=[Vec2(54, 33), Vec2(56, 33)], # Positions of enemies (known from start)
                    tilemap=_edel_vale_map
                ),
            ],
        )

from engine.seq import SeqAnnotator, SeqDelay, SeqFunc, SeqList
from evo1.memory import Facing, Vec2, Box2, load_zelda_memory
from evo1.move2d import SeqAttack, SeqGrabChest, SeqMove2D, SeqKnight2D, clunky_combat2d


class Edel1(SeqList):
    def __init__(self):
        super().__init__(
            name="Edel Vale",
            children=[
                SeqFunc(load_zelda_memory),
                SeqMove2D("Move to chest", coords=[Vec2(14, 52)]),
                SeqGrabChest("Move Left", direction=Facing.RIGHT),
                SeqMove2D("Move to chest", coords=[Vec2(11, 52)]),
                SeqGrabChest("Move Vertical", direction=Facing.LEFT),
                SeqMove2D("Move to chest", coords=[Vec2(12, 52), Vec2(12, 51)]),
                SeqGrabChest("Basic Scroll", direction=Facing.UP),
                SeqMove2D(
                    "Move to chest",
                    coords=[
                        Vec2(12, 47),
                        Vec2(21, 47),
                        Vec2(21, 52),
                        Vec2(20, 52),
                    ],
                ),
                SeqGrabChest("Smooth Scroll", direction=Facing.LEFT),
                SeqMove2D(
                    "Move to sword",
                    coords=[
                        Vec2(24, 52),
                        Vec2(24, 53),
                        Vec2(29, 53),
                        Vec2(29, 58),
                        Vec2(30, 58),
                        Vec2(30, 60),
                    ],
                ),
                SeqGrabChest("Sword", direction=Facing.DOWN),
                SeqMove2D(
                    "Move to bush",
                    coords=[
                        Vec2(30, 57),
                        Vec2(31, 57),
                        Vec2(31, 55),
                    ],
                ),
                SeqAttack("Bush"),
                SeqMove2D("Move to chest", coords=[Vec2(32, 55)]),
                SeqGrabChest("Monsters", direction=Facing.RIGHT),
                # TODO: The annotator here adds a function that can deal with enemies (poorly, dies a lot)
                SeqAnnotator(
                    "Simple enemy behavior",
                    annotations={"combat": clunky_combat2d},
                    func=load_zelda_memory,  # Need to reload memory to get the correct enemy location
                    wrapped=SeqList(
                        name="Enemies",
                        children=[
                            SeqMove2D(
                                "Dodge enemies",
                                coords=[
                                    Vec2(35, 55),
                                    Vec2(35, 54),
                                    Vec2(36, 54),
                                    Vec2(36, 53),
                                    Vec2(37, 53),
                                    Vec2(37, 52),
                                    Vec2(39, 52),
                                ],
                            ),
                            # Here's music chest to the right, TODO: optionally grab?
                            SeqGrabChest("16-bit", direction=Facing.RIGHT),
                            SeqAttack("Bush"),
                            SeqMove2D(
                                "Move to chest",
                                coords=[
                                    Vec2(39, 47),
                                    # Optional, chest to the north, save (move to Vec2(39, 45), then open chest N)
                                    Vec2(41, 47),
                                    Vec2(41, 48),
                                    Vec2(44, 48),
                                    Vec2(44, 49),
                                ],
                            ),
                            SeqGrabChest("16-bit", direction=Facing.DOWN),
                            # TODO: Some enemies here, will probably fail
                            SeqMove2D(
                                "Dodge enemies",
                                coords=[
                                    Vec2(44, 52),
                                    Vec2(50, 52),
                                    Vec2(50, 53),
                                    Vec2(55, 53),
                                    Vec2(55, 54),
                                    Vec2(58, 54),
                                ],
                            ),
                            SeqMove2D(
                                "Dodge enemies",
                                coords=[
                                    Vec2(60, 54),
                                    Vec2(60, 44),
                                    Vec2(51, 44),
                                    Vec2(51, 45),
                                    Vec2(48, 45),
                                    Vec2(48, 36),
                                    Vec2(36, 36),
                                    Vec2(36, 33),
                                    Vec2(34, 33),
                                ],
                            ),
                            SeqGrabChest("Free move", direction=Facing.LEFT),
                            # TODO: At this point we can move more freely, could implement a better move2d (or improve current)
                            SeqMove2D(
                                "Navigate to knights",
                                coords=[
                                    # TODO: Implement Boid-type behavior to avoid enemies that approach?
                                    # Move to rocks, dodging enemies
                                    Vec2(33.5, 33),
                                    Vec2(36, 35.7),
                                    Vec2(48, 36),
                                    # Navigating past the rocks
                                    Vec2(50, 36.5),
                                    Vec2(51, 36.5),
                                    Vec2(52, 36.5),
                                    Vec2(53, 36),
                                    Vec2(54.1, 33.5),  # Near left knight
                                ],
                            ),
                        ],
                    ),
                ),
            ],
        )


class EdelExperimental(SeqAnnotator):
    def __init__(self):
        super().__init__(
            name="Edel Vale experimental",
            annotations={},
            func=load_zelda_memory,  # Need to reload memory to get the correct enemy location
            wrapped=SeqList(
                name="Knights",
                children=[
                    # TODO: This appears to be needed on load for some reason, or the game crashes
                    SeqDelay("Memory delay", time_in_s=1.0),
                    # TODO: DUMMY SEQUENCE, DO NOT USE UNLESS LOADING FROM SAVEPOINT
                    SeqMove2D(
                        "Navigate to knights",
                        coords=[
                            Vec2(52, 36.5),
                            Vec2(53, 36),
                            Vec2(54.1, 33.5),  # Near left knight
                        ],
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
                    ),
                    # TODO: We need to kill two knights. These enemies must be killed with 3 attacks, but cannot be harmed from the front.
                    # TODO: Need to get hold of the enemies in question so we know when they are dead. Need to strategize for the best way to kill them without dying.
                    SeqKnight2D(
                        "Killing two knights",
                        arena=Box2(pos=Vec2(53, 32), w=5, h=4), # Valid arena to fight inside (should be clear of obstacles)
                        targets=[Vec2(54, 33), Vec2(56, 33)], # TODO: Better enemy identification
                    ),
                    SeqMove2D(
                        "Grabbing inv",
                        coords=[
                            Vec2(54, 31),
                            # TODO: Grab chest (Inv)
                            Vec2(54, 28),
                            # TODO: Transition here?
                        ],
                    ),
                    # TODO: Progress to the overworld map.
                ],
            ),
        )

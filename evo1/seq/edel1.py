from engine.seq import SeqFunc, SeqList
from evo1.memory import Facing, Vec2, load_zelda_memory
from evo1.move2d import SeqAttack, SeqGrabChest, SeqMove2D


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
                SeqMove2D("Move to chest", coords=[Vec2(12, 51)]),
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
                SeqMove2D("Move to bush", coords=[Vec2(32, 55)]),
                SeqGrabChest("Monsters", direction=Facing.RIGHT),
                # TODO: Should add annotator here that can deal with enemies (seems ok tho)
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
                # TODO: WR attacks bush here, needed or just swag?
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
            ],
        )

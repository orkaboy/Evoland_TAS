from engine.combat import SeqArenaCombat
from engine.mathlib import Box2, Vec2
from engine.move2d import SeqMove2D, SeqMove2DConfirm
from engine.seq import (
    SeqAttack,
    SeqDirHoldUntilLostControl,
    SeqInteract,
    SeqList,
    SeqTapDirection,
)


class MagiStart(SeqList):
    def __init__(self):
        super().__init__(
            name="G",
            children=[
                # Basic movement tutorial
                SeqInteract("Talk"),
                SeqDirHoldUntilLostControl("Right", Vec2(1, 0)),
                SeqInteract("Talk"),
                SeqDirHoldUntilLostControl("Left", Vec2(-1, 0)),
                SeqInteract("Talk"),
                SeqTapDirection("Down", direction=Vec2(0, 1)),
                SeqTapDirection("Up", direction=Vec2(0, -1)),
                SeqInteract("Talk"),
                # Move to bushes and attack
                SeqMove2D("Move to bush", coords=[Vec2(89.5, 50)]),
                SeqMove2DConfirm("Move to bush", coords=[Vec2(89.5, 46.3)]),
                SeqAttack("Bush"),
                SeqMove2DConfirm("Move to fight", coords=[Vec2(89.5, 40)]),
                # Fight the bots
                SeqArenaCombat(
                    "Bots",
                    Box2(pos=Vec2(86, 35), w=8, h=6),
                    num_targets=3,
                    retracking=True,
                ),
                # TODO: Move to correct position
                SeqDirHoldUntilLostControl("Wait", Vec2(0, 0)),
                SeqInteract("Story stuff"),
            ],
        )

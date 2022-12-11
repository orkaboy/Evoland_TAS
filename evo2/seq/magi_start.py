from engine.mathlib import Box2, Vec2
from engine.seq import (
    SeqAttack,
    SeqDirHoldUntilLostControl,
    SeqInteract,
    SeqList,
    SeqTapDirection,
)
from evo2.combat import SeqArenaCombat
from evo2.memory import get_zelda_memory
from evo2.move2d import SeqMove2D, SeqMove2DConfirm


class MagiStart(SeqList):
    def __init__(self):
        super().__init__(
            name="G",
            children=[
                # Basic movement tutorial
                SeqInteract("Talk", mem_func=get_zelda_memory),
                SeqDirHoldUntilLostControl(
                    "Right", Vec2(1, 0), mem_func=get_zelda_memory
                ),
                SeqInteract("Talk", mem_func=get_zelda_memory),
                SeqDirHoldUntilLostControl(
                    "Left", Vec2(-1, 0), mem_func=get_zelda_memory
                ),
                SeqInteract("Talk", mem_func=get_zelda_memory),
                SeqTapDirection("Down", direction=Vec2(0, 1)),
                SeqTapDirection("Up", direction=Vec2(0, -1)),
                SeqInteract("Talk", mem_func=get_zelda_memory),
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
                SeqDirHoldUntilLostControl(
                    "Wait", Vec2(0, 0), mem_func=get_zelda_memory
                ),
                SeqInteract("Story stuff", mem_func=get_zelda_memory),
            ],
        )

from engine.combat import SeqMove2DClunkyCombat
from engine.mathlib import Vec2
from engine.seq import SeqList
from memory.evo1 import get_diablo_memory


# TODO: Should maybe inherit SeqMove2D instead, since we usually don't want to attack everything that moves here (slow)
class SeqDiabloCombat(SeqMove2DClunkyCombat):
    def __init__(self, name: str, coords: list[Vec2], precision: float = 0.2):
        # TODO: Could use func here to load_diablo_memory?
        super().__init__(name, coords, precision)
        self.mem = get_diablo_memory()

    # TODO: execute, render

    # TODO: Boid behavior?


# TODO: NavMap for Sarudnahk


class Sarudnahk(SeqList):
    def __init__(self):
        super().__init__(
            name="Sarudnahk",
            children=[
                SeqDiabloCombat("Move to chest", coords=[]),  # TODO
                # TODO: switch to Kaeris
                # TODO: Navigate through the Diablo section (Boid behavior?)
                # TODO: Fight the Undead King boss (abuse gravestone hitbox)
                # TODO: Navigate past enemies in the Diablo section and grab the second part of the amulet
            ],
        )

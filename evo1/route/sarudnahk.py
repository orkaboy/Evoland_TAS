import logging

from control import evo_ctrl
from engine.combat import SeqMove2DClunkyCombat
from engine.mathlib import Facing, Vec2
from engine.move2d import SeqGrabChest
from engine.seq import SeqList
from memory.evo1 import get_diablo_memory

logger = logging.getLogger(__name__)


# TODO: Should maybe inherit SeqMove2D instead, since we usually don't want to attack everything that moves here (slow)
class SeqDiabloCombat(SeqMove2DClunkyCombat):
    def __init__(self, name: str, coords: list[Vec2], precision: float = 0.2):
        # TODO: Could use func here to load_diablo_memory?
        super().__init__(name, coords, precision)
        self.mem = get_diablo_memory()

    # TODO: execute, render
    # TODO: Boid behavior?


# TODO: NavMap for Sarudnahk


class SeqCharacterSelect(SeqGrabChest):
    def __init__(self):
        super().__init__(name="Character Select", direction=Facing.UP)
        self.timer = 0

    def reset(self) -> None:
        self.timer = 0
        super().reset()

    # Delay in s for Character Select screen to open
    _GUI_DELAY = 1.8
    _SEL_OFFSET = 10
    # Delay in s for Character Select rotation to complete
    _SEL_DELAY = 1.3

    def execute(self, delta: float) -> bool:
        ctrl = evo_ctrl()
        # Grab chest
        if not self.tapped:
            super().execute(delta)
        # Wait for GUI to appear
        elif self.timer < self._GUI_DELAY:
            self.timer += delta
        # Tap left to select character
        elif self.timer < self._SEL_OFFSET:
            logger.debug("Character select GUI open, tapping left to select Kaeris")
            ctrl.dpad.tap_left()
            self.timer = self._SEL_OFFSET
        # Wait for GUI to respond
        elif (self.timer - self._SEL_OFFSET) < self._SEL_DELAY:
            self.timer += delta
        # Confirm Kaeris character select
        else:
            logger.debug("Selecting Kaeris")
            ctrl.dpad.none()
            ctrl.confirm()
            return True
        return False


class Sarudnahk(SeqList):
    def __init__(self):
        super().__init__(
            name="Sarudnahk",
            children=[
                SeqDiabloCombat(
                    "Move to chest", coords=[Vec2(15, 119), Vec2(15, 112.5)]
                ),
                SeqCharacterSelect(),
                # TODO: Navigate through the Diablo section (Boid behavior?)
                # TODO: Pick up chests: Combo, Life meter, Ambient light (can glitch otherwise?), Boss
                # TODO: Fight the Undead King boss (abuse gravestone hitbox). Track Lich hp/position
                # TODO: Navigate past enemies in the Diablo section and grab the second part of the amulet
                # TODO: Grab the portal chest and teleport to Aogai
            ],
        )

import logging

from control import evo_ctrl
from engine.mathlib import Vec2
from engine.seq import SeqBase, SeqMashDelay
from evo2.memory import get_zelda_memory

logger = logging.getLogger(__name__)


class SeqInteract(SeqMashDelay):
    def __init__(self, name: str, timeout_in_s: float):
        super().__init__(name, timeout_in_s)
        self.timer = 0

    def execute(self, delta: float) -> bool:
        self.timer += delta
        ctrl = evo_ctrl()
        ctrl.confirm(tapping=True)
        # Wait out any cutscene/pickup animation
        mem = get_zelda_memory()
        return mem.player.in_control and self.timer >= self.timeout

    def __repr__(self) -> str:
        return f"Mashing confirm until in control ({self.name})"


class SeqDirHoldUntilLostControl(SeqBase):
    def __init__(self, name: str, direction: Vec2):
        self.direction = direction
        super().__init__(name)

    def execute(self, delta: float) -> bool:
        ctrl = evo_ctrl()
        if self.direction.x > 0:
            ctrl.dpad.right()
        elif self.direction.x < 0:
            ctrl.dpad.left()
        if self.direction.y > 0:
            ctrl.dpad.down()
        elif self.direction.y < 0:
            ctrl.dpad.up()

        mem = get_zelda_memory()
        done = mem.player.not_in_control
        if done:
            ctrl.dpad.none()
        return done

    def __repr__(self) -> str:
        return f"Moving until we lose control ({self.name})"

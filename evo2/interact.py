import logging

import evo2.control
from engine.mathlib import Vec2
from engine.seq import SeqBase
from evo2.memory import get_zelda_memory

logger = logging.getLogger(__name__)


class SeqMashDelay(SeqBase):
    def __init__(self, name: str, timeout_in_s: float = 0.0):
        self.timeout_in_s = timeout_in_s
        self.timer = 0.0
        super().__init__(name)

    def reset(self) -> None:
        self.timer = 0.0

    def execute(self, delta: float) -> bool:
        self.timer += delta
        ctrl = evo2.control.handle()
        ctrl.confirm(tapping=True)
        # Wait out any cutscene/pickup animation
        return self.timer >= self.timeout_in_s

    def __repr__(self) -> str:
        return f"Mashing confirm while waiting ({self.name})... {self.timer:.2f}/{self.timeout_in_s:.2f}"


class SeqInteract(SeqMashDelay):
    def execute(self, delta: float) -> bool:
        self.timer += delta
        ctrl = evo2.control.handle()
        ctrl.confirm(tapping=True)
        # Wait out any cutscene/pickup animation
        mem = get_zelda_memory()
        return mem.player.in_control and self.timer >= self.timeout_in_s

    def __repr__(self) -> str:
        return f"Mashing confirm until in control ({self.name})"


class SeqTapDirection(SeqBase):
    def __init__(self, name: str, direction: Vec2):
        self.direction = direction
        super().__init__(name)

    def execute(self, delta: float) -> bool:
        ctrl = evo2.control.handle()
        if self.direction.x > 0:
            ctrl.dpad.tap_right()
        elif self.direction.x < 0:
            ctrl.dpad.tap_left()
        if self.direction.y > 0:
            ctrl.dpad.tap_up()
        elif self.direction.y < 0:
            ctrl.dpad.tap_down()
        return True

    def __repr__(self) -> str:
        return f"Tap direction ({self.name})"


class SeqDirHoldUntilLostControl(SeqBase):
    def __init__(self, name: str, direction: Vec2):
        self.direction = direction
        super().__init__(name)

    def execute(self, delta: float) -> bool:
        ctrl = evo2.control.handle()
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

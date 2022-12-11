from control import evo_ctrl
from engine.mathlib import Vec2
from engine.seq import SeqBase


class SeqTapDirection(SeqBase):
    def __init__(self, name: str, direction: Vec2):
        self.direction = direction
        super().__init__(name)

    def execute(self, delta: float) -> bool:
        ctrl = evo_ctrl()
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


class SeqAttack(SeqBase):
    def __init__(self, name: str):
        super().__init__(name)

    def execute(self, delta: float) -> bool:
        ctrl = evo_ctrl()
        ctrl.attack(tapping=False)
        # TODO: Await control?
        return True

    def __repr__(self) -> str:
        return f"Attack({self.name})"

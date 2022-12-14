from control import evo_ctrl
from engine.mathlib import Vec2
from engine.seq.base import SeqBase
from engine.seq.time import SeqMashDelay


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
        evo_ctrl().attack(tapping=False)
        return True

    def __repr__(self) -> str:
        return f"Attack({self.name})"


class SeqMenu(SeqBase):
    def __init__(self, name: str):
        super().__init__(name)

    def execute(self, delta: float) -> bool:
        evo_ctrl().menu(tapping=False)
        return True

    def __repr__(self) -> str:
        return f"Menu({self.name})"


class SeqInteract(SeqMashDelay):
    def __init__(self, name: str, timeout_in_s: float = 0.0, once: bool = False):
        super().__init__(name, timeout_in_s)
        self.timer = 0
        self.once = once

    def execute(self, delta: float) -> bool:
        self.timer += delta
        if self.once:
            evo_ctrl().confirm(tapping=False)
            return True
        evo_ctrl().confirm(tapping=True)
        # Wait out any cutscene/pickup animation
        mem = self.zelda_mem()
        return mem.player.in_control and self.timer >= self.timeout

    def __repr__(self) -> str:
        return f"Mashing confirm until in control ({self.name})"


class SeqWaitForControl(SeqBase):
    def __init__(self, name: str):
        super().__init__(name)

    def execute(self, delta: float) -> bool:
        mem = self.zelda_mem()
        return mem.player.in_control

    def __repr__(self) -> str:
        return f"Wait for control ({self.name})"


class SeqDirHoldUntilLostControl(SeqWaitForControl):
    def __init__(self, name: str, direction: Vec2):
        self.direction = direction
        super().__init__(name)

    def execute(self, delta: float) -> bool:
        ctrl = evo_ctrl()
        ctrl.set_joystick(self.direction)

        mem = self.zelda_mem()
        done = not mem.player.in_control
        if done:
            ctrl.set_neutral()
        return done

    def __repr__(self) -> str:
        return f"Moving until we lose control ({self.name})"

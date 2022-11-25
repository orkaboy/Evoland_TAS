# Libraries and Core Files
import time
from enum import IntEnum

from control.controller import Buttons as VgButtons
from control.controller import VgTranslator, handle
from engine.seq import SeqBase


def wait_seconds(seconds: float):
    time.sleep(seconds)


# Game functions
class Buttons(IntEnum):
    CONFIRM = VgButtons.A
    CANCEL = VgButtons.B


class MenuController:
    def __init__(self):
        self.ctrl = handle()
        self.delay = 0.3
        self.dpad = self.DPad(ctrl=self.ctrl, delay=self.delay)

    # Wrappers
    def set_button(self, x_key: Buttons, value):
        self.ctrl.set_button(x_key, value)

    def set_neutral(self):
        self.ctrl.set_neutral()

    class DPad:
        def __init__(self, ctrl: VgTranslator, delay: float):
            self.ctrl = ctrl
            self.delay = delay

        def up(self):
            self.ctrl.set_button(x_key=VgButtons.DPAD, value=1)

        def down(self):
            self.ctrl.set_button(x_key=VgButtons.DPAD, value=2)

        def none(self):
            self.ctrl.set_button(x_key=VgButtons.DPAD, value=0)

        def tap_up(self):
            self.up()
            wait_seconds(self.delay)
            self.none()
            wait_seconds(self.delay)

        def tap_down(self):
            self.down()
            wait_seconds(self.delay)
            self.none()
            wait_seconds(self.delay)

    def confirm(self):
        self.set_button(x_key=Buttons.CONFIRM, value=1)
        wait_seconds(self.delay)
        self.set_button(x_key=Buttons.CONFIRM, value=0)

    def cancel(self):
        self.set_button(x_key=Buttons.CANCEL, value=1)
        wait_seconds(self.delay)
        self.set_button(x_key=Buttons.CANCEL, value=0)


_menu_ctrl = MenuController()


class SeqMenuConfirm(SeqBase):
    def __init__(self, name: str = "Confirm"):
        super().__init__(name)

    def execute(self, delta: float, blackboard: dict) -> bool:
        _menu_ctrl.confirm()
        return True


class SeqMenuDown(SeqBase):
    def __init__(self, name: str = "Down"):
        super().__init__(name)

    def execute(self, delta: float, blackboard: dict) -> bool:
        _menu_ctrl.dpad.tap_down()
        return True


class SeqLoadGame(SeqBase):
    def __init__(self, name: str, saveslot: int):
        self.saveslot = saveslot
        super().__init__(name)

    # Navigate to the saveslot in question by tapping down x times, then confirming
    def execute(self, delta: float, blackboard: dict) -> bool:
        for _ in range(1, self.saveslot):
            _menu_ctrl.dpad.tap_down()
        _menu_ctrl.confirm()
        return True

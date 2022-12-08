# Libraries and Core Files
import logging
import time
from enum import IntEnum

from control.controller import Buttons as VgButtons
from control.controller import VgTranslator
from control.controller import handle as ctrl_handle

logger = logging.getLogger(__name__)


_FPS = 30.0
_FRAME_TIME = 1.0 / _FPS


def wait_frames(frames: float):
    time.sleep(frames * _FRAME_TIME)


# Game functions
class Buttons(IntEnum):
    CONFIRM = VgButtons.A
    ATTACK = VgButtons.X
    CANCEL = VgButtons.B
    MENU = VgButtons.START


class Evoland1Controller:
    def __init__(self, delay: int):
        self.ctrl = ctrl_handle()
        self.delay = delay  # In frames
        self.dpad = self.DPad(ctrl=self.ctrl, delay=self.delay)

    # Wrappers
    def set_button(self, x_key: Buttons, value):
        self.ctrl.set_button(x_key, value)

    def set_joystick(self, x: float, y: float):
        self.ctrl.set_joystick(x, y)

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

        def left(self):
            self.ctrl.set_button(x_key=VgButtons.DPAD, value=4)

        def right(self):
            self.ctrl.set_button(x_key=VgButtons.DPAD, value=8)

        def none(self):
            self.ctrl.set_button(x_key=VgButtons.DPAD, value=0)

        def tap_up(self):
            self.up()
            wait_frames(self.delay)
            self.none()
            wait_frames(self.delay)

        def tap_down(self):
            self.down()
            wait_frames(self.delay)
            self.none()
            wait_frames(self.delay)

        def tap_left(self):
            self.left()
            wait_frames(self.delay)
            self.none()
            wait_frames(self.delay)

        def tap_right(self):
            self.right()
            wait_frames(self.delay)
            self.none()
            wait_frames(self.delay)

    def confirm(self, tapping=False):
        self.set_button(x_key=Buttons.CONFIRM, value=1)
        wait_frames(self.delay)
        self.set_button(x_key=Buttons.CONFIRM, value=0)
        if tapping:
            wait_frames(self.delay)

    def cancel(self, tapping=False):
        self.set_button(x_key=Buttons.CANCEL, value=1)
        wait_frames(self.delay)
        self.set_button(x_key=Buttons.CANCEL, value=0)
        if tapping:
            wait_frames(self.delay)

    def attack(self, tapping=False):
        self.set_button(x_key=Buttons.ATTACK, value=1)
        wait_frames(self.delay)
        self.set_button(x_key=Buttons.ATTACK, value=0)
        if tapping:
            wait_frames(self.delay)

    def menu(self, tapping=False):
        self.set_button(x_key=Buttons.MENU, value=1)
        wait_frames(self.delay)
        self.set_button(x_key=Buttons.MENU, value=0)
        if tapping:
            wait_frames(self.delay)


_controller = Evoland1Controller(delay=4)


def handle():
    return _controller

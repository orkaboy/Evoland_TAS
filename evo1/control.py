# Libraries and Core Files
import logging

import controller
import evo1.memory as memory

logger = logging.getLogger(__name__)


class Evoland1Controller:
    def __init__(self):
        self.ctrl = controller.handle()
        self.dpad = self.DPad(self.ctrl)
        logger.info("Setting up Evoland1 controller wrapper.")

    # Wrappers
    def set_button(self, x_key: str, value):
        self.ctrl.set_button(x_key, value)

    def set_joystick(self, x: float, y: float):
        self.ctrl.set_joystick(x, y)

    def set_neutral(self):
        self.ctrl.set_neutral()

    # Game functions
    BUTTONS = {
        "confirm": "btn_a",
        "attack": "btn_x",
        "cancel": "btn_b",
        "menu": "btn_start",
    }

    class DPad:
        BUTTON_DELAY = 10

        def __init__(self, ctrl: controller.VgTranslator):
            self.ctrl = ctrl

        def up(self):
            self.ctrl.set_button(x_key="d_pad", value=1)

        def down(self):
            self.ctrl.set_button(x_key="d_pad", value=2)

        def left(self):
            self.ctrl.set_button(x_key="d_pad", value=4)

        def right(self):
            self.ctrl.set_button(x_key="d_pad", value=8)

        def none(self):
            self.ctrl.set_button(x_key="d_pad", value=0)

        def tap_up(self):
            self.up()
            memory.wait_frames(self.BUTTON_DELAY)
            self.none()
            memory.wait_frames(self.BUTTON_DELAY)

        def tap_down(self):
            self.down()
            memory.wait_frames(self.BUTTON_DELAY)
            self.none()
            memory.wait_frames(self.BUTTON_DELAY)

        def tap_left(self):
            self.left()
            memory.wait_frames(self.BUTTON_DELAY)
            self.none()
            memory.wait_frames(self.BUTTON_DELAY)

        def tap_right(self):
            self.right()
            memory.wait_frames(self.BUTTON_DELAY)
            self.none()
            memory.wait_frames(self.BUTTON_DELAY)

    BUTTON_DELAY = 10

    def confirm(self):
        self.set_button(x_key=self.BUTTONS["confirm"], value=1)
        memory.wait_frames(self.BUTTON_DELAY)
        self.set_button(x_key=self.BUTTONS["confirm"], value=0)

    def cancel(self):
        self.set_button(x_key=self.BUTTONS["cancel"], value=1)
        memory.wait_frames(self.BUTTON_DELAY)
        self.set_button(x_key=self.BUTTONS["cancel"], value=0)

    def attack(self):
        self.set_button(x_key=self.BUTTONS["attack"], value=1)
        memory.wait_frames(self.BUTTON_DELAY)
        self.set_button(x_key=self.BUTTONS["attack"], value=0)

    def menu(self):
        self.set_button(x_key=self.BUTTONS["menu"], value=1)
        memory.wait_frames(self.BUTTON_DELAY)
        self.set_button(x_key=self.BUTTONS["menu"], value=0)


_controller = Evoland1Controller()


def handle():
    return _controller

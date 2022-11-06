# Libraries and Core Files
import time

import controller


def wait_seconds(seconds: float):
    time.sleep(seconds)


class MenuController:
    def __init__(self):
        self.ctrl = controller.handle()
        self.delay = 0.3
        self.dpad = self.DPad(ctrl=self.ctrl, delay=self.delay)

    # Wrappers
    def set_button(self, x_key: str, value):
        self.ctrl.set_button(x_key, value)

    def set_neutral(self):
        self.ctrl.set_neutral()

    # Game functions
    BUTTONS = {
        "confirm": "btn_a",
        "cancel": "btn_b",
    }

    class DPad:
        def __init__(self, ctrl: controller.VgTranslator, delay: float):
            self.ctrl = ctrl
            self.delay = delay

        def up(self):
            self.ctrl.set_button(x_key="d_pad", value=1)

        def down(self):
            self.ctrl.set_button(x_key="d_pad", value=2)

        def none(self):
            self.ctrl.set_button(x_key="d_pad", value=0)

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
        self.set_button(x_key=self.BUTTONS["confirm"], value=1)
        wait_seconds(self.delay)
        self.set_button(x_key=self.BUTTONS["confirm"], value=0)

    def cancel(self):
        self.set_button(x_key=self.BUTTONS["cancel"], value=1)
        wait_seconds(self.delay)
        self.set_button(x_key=self.BUTTONS["cancel"], value=0)

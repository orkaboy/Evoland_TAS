# Libraries and Core Files
import logging

import vgamepad as vg

logger = logging.getLogger(__name__)


class VgTranslator:
    def __init__(self):
        logger.info("Setting up emulated Xbox360 controller.")
        self.gamepad = vg.VX360Gamepad()

    def _set_dpad(self, value: int):
        if value == 1:  # d_pad up
            self.gamepad.press_button(button=0x0001)
        elif value == 2:  # d_pad down
            self.gamepad.press_button(button=0x0002)
        elif value == 4:  # d_pad left
            self.gamepad.press_button(button=0x0004)
        elif value == 8:  # d_pad right
            self.gamepad.press_button(button=0x0008)
        elif value == 0:
            self.gamepad.release_button(button=0x0001)
            self.gamepad.release_button(button=0x0002)
            self.gamepad.release_button(button=0x0004)
            self.gamepad.release_button(button=0x0008)

    def set_button(self, x_key: str, value):
        match x_key:
            # Dpad movement
            case "d_pad":
                self._set_dpad(value)
            # Trigger buttons
            case "trigger_l":
                self.gamepad.left_trigger_float(value_float=value)
            case "trigger_r":
                self.gamepad.right_trigger_float(value_float=value)
            # Buttons
            case "btn_back":
                if value != 0:
                    self.gamepad.press_button(button=0x0020)
                else:
                    self.gamepad.release_button(button=0x0020)
            case "btn_start":
                if value != 0:
                    self.gamepad.press_button(button=0x0010)
                else:
                    self.gamepad.release_button(button=0x0010)
            case "btn_a":
                if value != 0:
                    self.gamepad.press_button(button=0x2000)
                else:
                    self.gamepad.release_button(button=0x2000)
            case "btn_b":
                if value != 0:
                    self.gamepad.press_button(button=0x1000)
                else:
                    self.gamepad.release_button(button=0x1000)
            case "btn_x":
                if value != 0:
                    self.gamepad.press_button(button=0x4000)
                else:
                    self.gamepad.release_button(button=0x4000)
            case "btn_y":
                if value != 0:
                    self.gamepad.press_button(button=0x8000)
                else:
                    self.gamepad.release_button(button=0x8000)
            case "btn_shoulder_l":
                if value != 0:
                    self.gamepad.press_button(button=0x0100)
                else:
                    self.gamepad.release_button(button=0x0100)
            case "btn_shoulder_r":
                if value != 0:
                    self.gamepad.press_button(button=0x0200)
                else:
                    self.gamepad.release_button(button=0x0200)
        # Update state of gamepad
        self.gamepad.update()
        # For additional details, review this website:
        # https://pypi.org/project/vgamepad/

    def set_joystick(self, x: float, y: float):
        x = min(x, 1)
        x = max(x, -1)
        y = min(y, 1)
        y = max(y, -1)
        try:
            self.gamepad.left_joystick_float(x_value_float=x, y_value_float=y)
            self.gamepad.update()
        except Exception as E:
            logger.exception(E)

    def set_neutral(self):
        self.gamepad.reset()
        self.gamepad.update()


_controller = VgTranslator()


def handle():
    return _controller

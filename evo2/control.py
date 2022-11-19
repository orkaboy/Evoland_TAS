# Libraries and Core Files
import logging

import control.controller as controller
from evo1.memory import Vec2

logger = logging.getLogger(__name__)


class Evoland2Controller:
    def __init__(self):
        self.ctrl = controller.handle()

    # Wrappers
    def set_button(self, x_key: controller.Buttons, value):
        self.set_button(x_key, value)

    def set_joystick(self, dir: Vec2):
        self.ctrl.set_joystick(dir.x, dir.y)

    def set_neutral(self):
        self.ctrl.set_neutral()


_controller = Evoland2Controller()


def handle():
    return _controller

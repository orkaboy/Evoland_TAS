# Libraries and Core Files
import logging

import controller

logger = logging.getLogger(__name__)


class Evoland1Controller:
    def __init__(self):
        self.ctrl = controller.handle()
        logger.info("Setting up Evoland1 controller wrapper.")

    # Wrappers
    def set_button(self, x_key: str, value):
        self.set_button(x_key, value)

    def set_joystick(self, x: float, y: float):
        self.ctrl.set_joystick(x, y)

    def set_neutral(self):
        self.ctrl.set_neutral()


_controller = Evoland1Controller()


def handle():
    return _controller

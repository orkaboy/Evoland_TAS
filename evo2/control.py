# Libraries and Core Files
import logging

import controller

logger = logging.getLogger(__name__)


class Evoland2Controller:
    def __init__(self):
        self.handle = controller.handle()


_controller = Evoland2Controller()


def handle():
    return _controller

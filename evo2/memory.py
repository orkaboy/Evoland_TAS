# Libraries and Core Files
import logging
import time

logger = logging.getLogger(__name__)

_FPS = 30.0
_FRAME_TIME = 1.0 / _FPS


def wait_seconds(seconds: float):
    time.sleep(seconds)


def wait_frames(frames: float):
    time.sleep(frames * _FRAME_TIME)

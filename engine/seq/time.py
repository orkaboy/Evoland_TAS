# Libraries and Core Files
import time

from control import evo_ctrl
from engine.seq.base import SeqBase


def wait_seconds(seconds: float):
    time.sleep(seconds)


class SeqDelay(SeqBase):
    def __init__(self, name: str, timeout_in_s: float):
        self.timer = 0.0
        self.timeout = timeout_in_s
        super().__init__(name)

    def reset(self) -> None:
        self.timer = 0.0
        return super().reset()

    def execute(self, delta: float) -> bool:
        self.timer = self.timer + delta
        if self.timer >= self.timeout:
            self.timer = self.timeout
            return True
        return False

    def __repr__(self) -> str:
        return f"Waiting({self.name})... {self.timer:.2f}/{self.timeout:.2f}"


class SeqMashDelay(SeqDelay):
    def execute(self, delta: float) -> bool:
        self.timer += delta
        evo_ctrl().confirm(tapping=True)
        # Wait out any cutscene/pickup animation
        return self.timer >= self.timeout

    def __repr__(self) -> str:
        return f"Mashing confirm while waiting ({self.name})... {self.timer:.2f}/{self.timeout:.2f}"

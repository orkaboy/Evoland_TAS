import logging

from control import evo_ctrl
from engine.seq import SeqBase
from evo1.memory import get_zelda_memory

logger = logging.getLogger(__name__)


class SeqMashDelay(SeqBase):
    def __init__(self, name: str, timeout_in_s: float = 0.0):
        self.timeout_in_s = timeout_in_s
        self.timer = 0.0
        super().__init__(name)

    def reset(self) -> None:
        self.timer = 0.0

    def execute(self, delta: float) -> bool:
        self.timer += delta
        ctrl = evo_ctrl()
        ctrl.confirm(tapping=True)
        # Wait out any cutscene/pickup animation
        return self.timer >= self.timeout_in_s

    def __repr__(self) -> str:
        return f"Mashing confirm while waiting ({self.name})... {self.timer:.2f}/{self.timeout_in_s:.2f}"


class SeqInteract(SeqMashDelay):
    def execute(self, delta: float) -> bool:
        self.timer += delta
        ctrl = evo_ctrl()
        ctrl.confirm(tapping=True)
        # Wait out any cutscene/pickup animation
        mem = get_zelda_memory()
        return mem.player.in_control and self.timer >= self.timeout_in_s

    def __repr__(self) -> str:
        return f"Mashing confirm until in control ({self.name})"


class SeqWaitForControl(SeqBase):
    def execute(self, delta: float) -> bool:
        mem = get_zelda_memory()
        return mem.player.in_control

    def __repr__(self) -> str:
        return f"Wait for control ({self.name})"


class SeqShopBuy(SeqBase):
    def __init__(self, name: str, slot: int):
        self.slot = slot
        self.cur_slot = 0
        self.step = 0
        super().__init__(name)

    def reset(self) -> None:
        self.cur_slot = 0
        self.step = 0

    def execute(self, delta: float) -> bool:
        ctrl = evo_ctrl()
        ctrl.dpad.none()

        match self.step:
            case 0:
                ctrl.confirm(tapping=True)  # Approach
            case 1:
                ctrl.confirm(tapping=True)  # Buy
            case 2:  # Move to slot
                if self.cur_slot < self.slot:
                    ctrl.dpad.tap_down()
                    self.cur_slot = self.cur_slot + 1
                    return False
            case 3:
                ctrl.confirm(tapping=True)  # Select item to buy
            case 4:
                ctrl.confirm(tapping=True)  # Confirm buying item
            case 5:
                logger.info(f"Done buying {self.name}")
                return True

        self.step = self.step + 1
        return False

    def __repr__(self) -> str:
        return f"Shopping... (Buying {self.name})"

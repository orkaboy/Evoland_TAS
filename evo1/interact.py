import logging

import evo1.control
from engine.seq import SeqBase
from evo1.memory import get_zelda_memory, load_zelda_memory

logger = logging.getLogger(__name__)


class SeqInteract(SeqBase):
    def __init__(self, name: str):
        super().__init__(name)

    def execute(self, delta: float, blackboard: dict) -> bool:
        ctrl = evo1.control.handle()
        ctrl.confirm()
        return True


class SeqWaitForControl(SeqBase):
    def execute(self, delta: float, blackboard: dict) -> bool:
        load_zelda_memory()
        mem = get_zelda_memory()
        return not mem.player.get_inv_open()

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

    def execute(self, delta: float, blackboard: dict) -> bool:
        ctrl = evo1.control.handle()
        ctrl.dpad.none()

        match self.step:
            case 0: ctrl.confirm() # Approach
            case 1: ctrl.confirm() # Buy
            case 2: # Move to slot
                if self.cur_slot < self.slot:
                    ctrl.dpad.tap_down()
                    self.cur_slot = self.cur_slot + 1
                    return False
            case 3: ctrl.confirm() # Select item to buy
            case 4: ctrl.confirm() # Confirm buying item
            case 5:
                logger.info(f"Done buying {self.name}")
                return True

        self.step = self.step + 1
        return False

    def __repr__(self) -> str:
        return f"Shopping... (Buying {self.name})"

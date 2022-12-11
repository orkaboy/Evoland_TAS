import logging

from control import evo_ctrl
from engine.mathlib import Facing, facing_str
from engine.seq import SeqBase
from evo1.memory import MapID, get_memory

logger = logging.getLogger(__name__)


class SeqZoneTransition(SeqBase):
    def __init__(self, name: str, direction: Facing, target_zone: MapID):
        self.direction = direction
        self.target_zone = target_zone
        super().__init__(name)

    def execute(self, delta: float) -> bool:
        ctrl = evo_ctrl()
        ctrl.dpad.none()
        match self.direction:
            case Facing.LEFT:
                ctrl.dpad.left()
            case Facing.RIGHT:
                ctrl.dpad.right()
            case Facing.UP:
                ctrl.dpad.up()
            case Facing.DOWN:
                ctrl.dpad.down()

        mem = get_memory()
        if mem.map_id == self.target_zone:
            ctrl.dpad.none()
            logger.info(f"Transitioned to zone: {self.target_zone.name}")
            return True
        return False

    def __repr__(self) -> str:
        return f"Transition to {self.name}, walking {facing_str(self.direction)}"

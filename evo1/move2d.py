import logging

from control import evo_ctrl
from engine.mathlib import Facing, Vec2, facing_str
from engine.seq import SeqBase
from memory.evo1 import MapID, get_memory

logger = logging.getLogger(__name__)


class SeqZoneTransition(SeqBase):
    def __init__(self, name: str, direction: Facing, target_zone: MapID):
        self.direction = direction
        self.target_zone = target_zone
        super().__init__(name)

    def execute(self, delta: float) -> bool:
        ctrl = evo_ctrl()
        match self.direction:
            case Facing.LEFT:
                ctrl.set_joystick(Vec2(-1, 0))
            case Facing.RIGHT:
                ctrl.set_joystick(Vec2(1, 0))
            case Facing.UP:
                ctrl.set_joystick(Vec2(0, 1))
            case Facing.DOWN:
                ctrl.set_joystick(Vec2(0, -1))

        mem = get_memory()
        if mem.map_id == self.target_zone:
            ctrl.set_neutral()
            logger.info(f"Transitioned to zone: {self.target_zone.name}")
            return True
        return False

    def __repr__(self) -> str:
        return f"Transition to {self.name}, walking {facing_str(self.direction)}"

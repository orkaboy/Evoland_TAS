import logging

from control.evoland import evo_ctrl
from engine.mathlib import Facing, Vec2
from engine.move2d import SeqMove2D
from engine.seq import SeqBase, SeqDelay, SeqList, SeqLog
from evo1.move2d import SeqZoneTransition
from memory.evo1.map_id import MapID
from term.log_init import reset_logging_time_reference

logger = logging.getLogger(__name__)


def start_timer():
    reset_logging_time_reference()


class Evo1MoveTest(SeqList):
    _ENTRANCE = Vec2(54, 30)
    _DOWN = Vec2(54, 33)
    _DOWN_RIGHT = Vec2(57, 33)

    def __init__(self, setup_func):
        super().__init__(
            name="Evo1 Move Test",
            children=[
                # Start on overworld, outside Edel Vale map
                SeqZoneTransition(
                    "Move to Edel Vale",
                    direction=Facing.DOWN,
                    target_zone=MapID.EDEL_VALE,
                ),
                SeqMove2D("Start position", coords=[self._ENTRANCE], precision=0.1),
                SeqDelay("Countdown", timeout_in_s=1),
                SeqBase(func=start_timer),
                SeqLog("Reset", "Reset timer"),
                SeqMove2D("One-dir", coords=[self._DOWN], precision=0.1),
                SeqLog("Linear", "Done with linear move"),
                SeqDelay("Countdown", timeout_in_s=1),
                SeqMove2D("Reset position", coords=[self._ENTRANCE], precision=0.1),
                SeqDelay("Countdown", timeout_in_s=1),
                SeqBase(func=start_timer),
                SeqLog("Reset", "Reset timer"),
                SeqMove2D("Two-dir", coords=[self._DOWN_RIGHT], precision=0.1),
                SeqLog("Two-dir", "Done with two-dir move"),
                SeqDelay("Countdown", timeout_in_s=1),
                SeqMove2D("Reset position", coords=[self._ENTRANCE], precision=0.1),
                SeqDelay("Countdown", timeout_in_s=1),
                SeqBase(func=start_timer),
                SeqLog("Reset", "Reset timer"),
                _MoveDiag("D-pad", coords=[self._DOWN_RIGHT], precision=0.1),
                _MoveStop("D-pad"),
                SeqLog("D-pad", "Done with D-pad move"),
            ],
            func=setup_func,
        )


# Dummy class for testing, will move dpad to down-right
class _MoveDiag(SeqMove2D):
    def __init__(self, name: str, coords: list[Vec2], precision: float = 0.1):
        super().__init__(name, coords, precision)

    # Overload
    def move_function(self, player_pos: Vec2, target_pos: Vec2):
        ctrl = evo_ctrl()
        ctrl.dpad.down()
        ctrl.dpad.right()
        ctrl.set_neutral()


# Dummy class for testing, will move dpad to down-right
class _MoveStop(SeqBase):
    def __init__(self, name: str):
        super().__init__(name)

    # Overload
    def execute(self, delta: float) -> bool:
        ctrl = evo_ctrl()
        ctrl.dpad.none()
        return True

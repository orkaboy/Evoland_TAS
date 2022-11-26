import logging
import time

import evo1.control
from evo1.move2d import SeqMove2D, move_to
from evo1.memory import get_memory, get_zelda_memory, Vec2, is_close

from typing import List

logger = logging.getLogger(__name__)

class FarmingGoal:
    def __init__(self, farm_coords: List[Vec2], precision: float = 0.2, gli_goal: int = None, lvl_goal: int = None) -> None:
        self.farm_coords = farm_coords
        self.precision = precision
        self.gli_goal = gli_goal
        self.lvl_goal = lvl_goal
        self.step = 0

    def reset(self) -> None:
        self.step = 0

    def farm(self, blackboard: dict) -> None:
        # Move towards target
        target = self.farm_coords[self.step]
        mem = get_zelda_memory()
        cur_pos = mem.player.get_pos()

        move_to(player=cur_pos, target=target, precision=self.precision, blackboard=blackboard)

        # If arrived, go to next coordinate in the list
        if is_close(cur_pos, target, self.precision):
            self.step = self.step + 1 if self.step < len(self.farm_coords)-1 else 0

    def is_done(self) -> bool:
        # Check that farming goals are met
        mem = get_memory()
        gli_goal_met = mem.get_gli() >= self.gli_goal if self.gli_goal else True
        lvl_goal_met = mem.get_lvl() >= self.lvl_goal if self.lvl_goal else True
        # Check that we are in the last position of the farm cycle
        mem = get_zelda_memory()
        cur_pos = mem.player.get_pos()
        last_pos = self.farm_coords[-1]
        nav_done = is_close(cur_pos, last_pos, self.precision)
        return gli_goal_met and lvl_goal_met and nav_done

    def __repr__(self) -> str:
        mem = get_memory()
        gli_goal = f" {mem.get_gli()}/{self.gli_goal} gli" if self.gli_goal else ""
        lvl_goal = f" {mem.get_lvl()}/{self.lvl_goal} lvl" if self.lvl_goal else ""
        return f"Farming goal:{gli_goal}{lvl_goal}"


class SeqATBmove2D(SeqMove2D):
    def __init__(self, name: str, coords: List[Vec2], goal: FarmingGoal = None, precision: float = 0.2):
        self.goal = goal
        super().__init__(name, coords, precision)

    def reset(self) -> None:
        if self.goal:
            self.goal.reset()

    def _farm_done(self) -> bool:
        return self.goal.is_done() if self.goal else True

    # TODO: Very, very dumb combat.
    def _handle_combat(self) -> None:
        ctrl = evo1.control.handle()
        ctrl.dpad.none()
        ctrl.confirm()
        time.sleep(0.2)

    def execute(self, delta: float, blackboard: dict) -> bool:
        mem = get_zelda_memory()
        # For some reason, this flag is set when in ATB combat
        if mem.player.get_inv_open():
            self._handle_combat()
            return False
        else:
            self._navigate_to_checkpoint(blackboard=blackboard)

            nav_done = self._nav_done()
            farm_done = self._farm_done()

            if nav_done and not farm_done:
                self.goal.farm(blackboard=blackboard)

            done = nav_done and farm_done
            if done:
                logger.debug(f"Finished moved2D section: {self.name}")
            return done

    def __repr__(self) -> str:
        num_coords = len(self.coords)
        farm = f"\n    {self.goal}" if self.goal else ""
        if self.step >= num_coords:
            return f"{self.name}[{num_coords}/{num_coords}]: {farm}"
        target = self.coords[self.step]
        step = self.step + 1
        return f"{self.name}[{step}/{num_coords}]: {target}{farm}"

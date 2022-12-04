import logging
import time

from engine.mathlib import Vec2, is_close
import evo1.control
from evo1.move2d import SeqMove2D, move_to
from evo1.memory import get_memory, get_zelda_memory, MapID
from memory.rng import EvolandRNG
from enum import Enum, auto
from term.curses import WindowLayout

from typing import List

logger = logging.getLogger(__name__)


class EncounterID(Enum):
    # Overworld 2D
    SLIME = auto()
    EMUK = auto()
    SLIME_2 = auto()
    SLIME_EMUK = auto()
    SLIME_3 = auto()
    # Cavern
    SCAVEN_2 = auto()
    KOBRA = auto()
    TORK = auto()
    KOBRA_2 = auto()
    SCAVEN_2_TORK = auto()
    # Overworld 3D
    ZOOMBA_2_APIDYA = auto()
    APIDYA = auto()
    ZOOMBA_2_ATUIN = auto()
    ZOOMBA_APIDYA = auto()


def calc_next_encounter(has_3d_monsters: bool = False) -> EncounterID:
    rng = EvolandRNG().get_rng()
    map_id = get_memory().get_map_id()
    modulo = 0xA
    if map_id == MapID.CRYSTAL_CAVERN:
        lut_value = (rng.rand_int() & 0x3fffffff) % modulo
        match lut_value:
            case 0 | 1 | 2: return EncounterID.SCAVEN_2
            case 3 | 4 | 5: return EncounterID.KOBRA
            case 6 | 7: return EncounterID.TORK
            case 8: return EncounterID.KOBRA_2
            case _: return EncounterID.SCAVEN_2_TORK
    elif not has_3d_monsters: # Overworld 2D
        lut_value = (rng.rand_int() & 0x3fffffff) % modulo
        match lut_value:
            case 0 | 1 | 2: return EncounterID.SLIME
            case 3 | 4 | 5: return EncounterID.EMUK
            case 6 | 7: return EncounterID.SLIME_2
            case 8: return EncounterID.SLIME_EMUK
            case _: return EncounterID.SLIME_3
    else:
        # Overworld 3D
        modulo = 0x7
        lut_value = (rng.rand_int() & 0x3fffffff) % modulo
        match lut_value:
            case 0 | 1 | 2: return EncounterID.ZOOMBA_2_APIDYA
            case 3 | 4: return EncounterID.APIDYA
            case 5: return EncounterID.ZOOMBA_2_ATUIN
            case 6: return EncounterID.ZOOMBA_APIDYA

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
        self.next_enc: EncounterID = None
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
        ctrl.confirm(tapping=True)

    def execute(self, delta: float, blackboard: dict) -> bool:
        mem = get_zelda_memory()
        # For some reason, this flag is set when in ATB combat
        if mem.player.get_inv_open():
            self._handle_combat()
            return False
        else:
            self.next_enc = calc_next_encounter(has_3d_monsters=False)  # TODO: Check for chest
            self._navigate_to_checkpoint(blackboard=blackboard)

            nav_done = self._nav_done()
            farm_done = self._farm_done()

            if nav_done and not farm_done:
                self.goal.farm(blackboard=blackboard)

            done = nav_done and farm_done
            if done:
                logger.debug(f"Finished moved2D section: {self.name}")
            return done

    def render(self, window: WindowLayout, blackboard: dict) -> None:
        super().render(window, blackboard)

        if self.next_enc:
            mem = get_zelda_memory()
            enc_timer = mem.player.get_encounter_timer()
            window.stats.addstr(12, 1, f" Next encounter ({enc_timer:.3f}):")
            window.stats.addstr(13, 1, f"  {self.next_enc.name}")

    def __repr__(self) -> str:
        num_coords = len(self.coords)
        farm = f"\n    {self.goal}" if self.goal else ""
        if self.step >= num_coords:
            return f"{self.name}[{num_coords}/{num_coords}]: {farm}"
        target = self.coords[self.step]
        step = self.step + 1
        return f"{self.name}[{step}/{num_coords}]: {target}{farm}"

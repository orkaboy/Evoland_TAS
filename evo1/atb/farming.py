import logging

import evo1.control
from engine.mathlib import Vec2
from evo1.atb.base import Encounter, SeqATBCombat, calc_next_encounter
from evo1.memory import get_memory, get_zelda_memory
from evo1.move2d import SeqMove2D, is_close, move_to
from memory.rng import EvolandRNG
from term.window import WindowLayout

logger = logging.getLogger(__name__)


def _tap_confirm() -> None:
    ctrl = evo1.control.handle()
    ctrl.dpad.none()
    ctrl.confirm(tapping=True)


class FarmingGoal:
    def __init__(
        self,
        farm_coords: list[Vec2],
        precision: float = 0.2,
        gli_goal: int = None,
        lvl_goal: int = None,
    ) -> None:
        self.farm_coords = farm_coords
        self.precision = precision
        self.gli_goal = gli_goal
        self.lvl_goal = lvl_goal
        self.step = 0

    def reset(self) -> None:
        self.step = 0

    def farm(self) -> None:
        # Move towards target
        target = self.farm_coords[self.step]
        mem = get_zelda_memory()
        cur_pos = mem.player.pos

        move_to(player=cur_pos, target=target, precision=self.precision)

        # If arrived, go to next coordinate in the list
        if is_close(cur_pos, target, self.precision):
            self.step = self.step + 1 if self.step < len(self.farm_coords) - 1 else 0

    def is_done(self) -> bool:
        # Check that farming goals are met
        mem = get_memory()
        gli_goal_met = mem.gli >= self.gli_goal if self.gli_goal else True
        lvl_goal_met = mem.lvl >= self.lvl_goal if self.lvl_goal else True
        # Check that we are in the last position of the farm cycle
        mem = get_zelda_memory()
        cur_pos = mem.player.pos
        last_pos = self.farm_coords[-1]
        nav_done = is_close(cur_pos, last_pos, self.precision)
        return gli_goal_met and lvl_goal_met and nav_done

    def __repr__(self) -> str:
        mem = get_memory()
        gli_goal = f" {mem.gli}/{self.gli_goal} gli" if self.gli_goal else ""
        lvl_goal = f" {mem.lvl}/{self.lvl_goal} lvl" if self.lvl_goal else ""
        return f"Farming goal:{gli_goal}{lvl_goal}"


class SeqATBmove2D(SeqMove2D):
    def __init__(
        self,
        name: str,
        coords: list[Vec2],
        battle_handler: SeqATBCombat = SeqATBCombat(),
        goal: FarmingGoal = None,
        precision: float = 0.2,
    ):
        self.goal = goal
        self.next_enc: Encounter = None
        self.battle_handler = battle_handler
        super().__init__(name, coords, precision)

    def reset(self) -> None:
        if self.goal:
            self.goal.reset()
        self.battle_handler.reset()

    def _farm_done(self) -> bool:
        return self.goal.is_done() if self.goal else True

    # Override
    def do_encounter_manip(self) -> bool:
        return False

    def navigate_to_goal(self) -> bool:
        rng = EvolandRNG().get_rng()
        # TODO: Check for manips
        self.next_enc = calc_next_encounter(rng=rng, has_3d_monsters=False)
        if self.do_encounter_manip():
            return True
        self._navigate_to_checkpoint()
        return False

    def check_farming_goals(self) -> bool:
        nav_done = self._nav_done()
        farm_done = self._farm_done()

        if nav_done and not farm_done:
            self.goal.farm()

        return nav_done and farm_done

    def execute(self, delta: float) -> bool:
        mem = get_zelda_memory()
        # For some reason, this flag is set when in ATB combat
        if mem.player.not_in_control:
            # Check for active battle (returns True on completion/non-execution)
            if self.battle_handler.execute(delta=delta):
                # Handle non-battle reasons for losing control
                # TODO: Just cutscenes for now, might need logic for skips here
                _tap_confirm()
            return False

        # Else navigate the world, checking for farming goals
        if self.navigate_to_goal():
            return False

        if done := self.check_farming_goals():
            logger.info(f"Finished moved2D section: {self.name}")
        return done

    def render(self, window: WindowLayout) -> None:
        # Check for acvite battle
        if self.battle_handler.active:
            self.battle_handler.render(window=window)
            return

        super().render(window=window)

        if self.next_enc:
            mem = get_zelda_memory()
            enc_timer = mem.player.encounter_timer
            window.stats.addstr(Vec2(1, 12), f" Next enc ({enc_timer:.3f}):")
            window.stats.addstr(Vec2(1, 13), f"  {self.next_enc}")

    def __repr__(self) -> str:
        # Check for active battle
        battle = f"\n    {self.battle_handler}" if self.battle_handler.active else ""
        num_coords = len(self.coords)
        farm = f"\n    {self.goal}" if self.goal else ""
        if self.step >= num_coords:
            return f"{self.name}[{num_coords}/{num_coords}]: {farm}{battle}"
        target = self.coords[self.step]
        step = self.step + 1
        return f"{self.name}[{step}/{num_coords}]: {target}{farm}{battle}"

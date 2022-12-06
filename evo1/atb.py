import logging

from engine.seq import SeqBase
from engine.mathlib import Vec2, is_close
import evo1.control
from evo1.move2d import SeqMove2D, move_to
from evo1.memory import get_memory, get_zelda_memory, MapID, BattleMemory, BattleEntity
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


def calc_next_encounter(rng: EvolandRNG.RNGStruct, has_3d_monsters: bool = False) -> EncounterID:
    rng_value = (rng.rand_int() & 0x3fffffff)
    map_id = get_memory().map_id
    modulo = 0xA
    if map_id == MapID.CRYSTAL_CAVERN:
        lut_value = rng_value % modulo
        match lut_value:
            case 0 | 1 | 2: return EncounterID.SCAVEN_2
            case 3 | 4 | 5: return EncounterID.KOBRA
            case 6 | 7: return EncounterID.TORK
            case 8: return EncounterID.KOBRA_2
            case _: return EncounterID.SCAVEN_2_TORK
    elif not has_3d_monsters: # Overworld 2D
        lut_value = rng_value % modulo
        match lut_value:
            case 0 | 1 | 2: return EncounterID.SLIME
            case 3 | 4 | 5: return EncounterID.EMUK
            case 6 | 7: return EncounterID.SLIME_2
            case 8: return EncounterID.SLIME_EMUK
            case _: return EncounterID.SLIME_3
    else:
        # Overworld 3D
        modulo = 0x7
        lut_value = rng_value % modulo
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
        cur_pos = mem.player.pos

        move_to(player=cur_pos, target=target, precision=self.precision, blackboard=blackboard)

        # If arrived, go to next coordinate in the list
        if is_close(cur_pos, target, self.precision):
            self.step = self.step + 1 if self.step < len(self.farm_coords)-1 else 0

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


def _tap_confirm() -> None:
    ctrl = evo1.control.handle()
    ctrl.dpad.none()
    ctrl.confirm(tapping=True)


# Handling of the actual battle logic itself (base class, replace with more complex logic)
class SeqATBCombat(SeqBase):
    def __init__(self, name: str = "Generic", wait_for_battle: bool = False) -> None:
        self.mem: BattleMemory = None
        self.wait_for_battle = wait_for_battle
        # Triggered is used together with wait_for_battle to handle boss sequences
        self.triggered = False
        super().__init__(name=name)

    def reset(self) -> None:
        self.triggered = False

    def execute(self, delta: float, blackboard: dict) -> bool:
        if not self.update_mem():
            if not self.wait_for_battle or self.triggered:
                return True
            # Tap confirm until battle starts
            _tap_confirm()
            return False
        self.triggered = True

        # Tap past win screen/cutscenes
        if self.mem.ended:
            _tap_confirm()
        else:
            self.handle_combat()

        return not self.active

    def update_mem(self) -> bool:
        # Check if we need to create a new ATB battle structure, or update the old one
        if self.mem is None:
            self.mem = BattleMemory()
        else:
            self.mem.update()
        # Clear unused memory; we need to try to recreate it next frame
        if not self.active:
            self.mem = None
            return False
        return True

    # TODO: Predict hit-chance (need the formula based on acc/evade)

    # Att + (0.5 * Att * random_float) - enemy_def
    def predict_damage(self, attacker: BattleEntity, defender: BattleEntity) -> int:
        rng = EvolandRNG().get_rng()
        rand_float = rng.rand_float()
        attack = attacker.attack
        defense = defender.defense
        return int(attack + (0.5 * attack * rand_float) - defense + 0.5)

    def predict_hit(self, attacker: BattleEntity, defender: BattleEntity) -> bool:
        rng = EvolandRNG().get_rng()
        accuracy = 10 # TODO: from attacker
        evade = 10 # TODO: from defender
        miss_chance = 30 # TODO: Calc
        roll = (rng.rand_int() & 0x3fffffff) % 100
        return roll >= miss_chance

    # TODO: Actual combat logic
    # TODO: Overload with more complex
    def handle_combat(self):
        # TODO: Very, very dumb combat.
        _tap_confirm()

    # TODO: Render combat state
    def render(self, window: WindowLayout, blackboard: dict) -> None:
        if not self.active:
            return
        window.stats.erase()
        window.write_stats_centered(line=1, text="Evoland 1 TAS")
        window.write_stats_centered(line=2, text="ATB Combat")

        window.stats.addstr(4, 1, "Party:")
        self._print_group(window=window, group=self.mem.allies, y_offset=5)
        window.stats.addstr(8, 1, "Enemies:")
        self._print_group(window=window, group=self.mem.enemies, y_offset=9)

        # TODO: Hit/Damage prediction
        # TODO: Who is acting?
        if not self.mem.ended:
            # TODO: Damage prediction for Kaeris
            dmg = self.predict_damage(self.mem.allies[0], self.mem.enemies[0])
            window.stats.addstr(13, 1, "Damage prediction:")
            window.stats.addstr(14, 2, f"Clink: {dmg}")

        # TODO: map representation

    def _print_group(self, window: WindowLayout, group: List[BattleEntity], y_offset: int) -> None:
        for i, entity in enumerate(group):
            y_pos = y_offset + i
            window.stats.addstr(y_pos, 2, f"{entity.cur_hp}/{entity.max_hp} [{entity.turn_gauge:.02f}]")

    def __repr__(self) -> str:
        if self.active:
            return f"Battle ended ({self.name})" if self.mem.ended else f"In battle ({self.name})"
        return f"Waiting for battle to start ({self.name})"

    @property
    def active(self):
        return self.mem is not None and self.mem.battle_active


# Dummy class for ATB combat testing; requires manual control
class SeqATBCombatManual(SeqATBCombat):
    def __init__(self, name: str = "Generic", wait_for_battle: bool = False) -> None:
        super().__init__(name=name, wait_for_battle=wait_for_battle)

    def handle_combat(self):
        pass


class SeqATBmove2D(SeqMove2D):
    def __init__(self, name: str, coords: List[Vec2], battle_handler: SeqATBCombat = SeqATBCombat(), goal: FarmingGoal = None, precision: float = 0.2):
        self.goal = goal
        self.next_enc: EncounterID = None
        self.battle_handler = battle_handler
        super().__init__(name, coords, precision)

    def reset(self) -> None:
        if self.goal:
            self.goal.reset()
        self.battle_handler.reset()

    def _farm_done(self) -> bool:
        return self.goal.is_done() if self.goal else True

    # Override
    def do_encounter_manip(self, blackboard: dict) -> bool:
        return False

    def navigate_to_goal(self, blackboard: dict) -> bool:
        rng = EvolandRNG().get_rng()
        self.next_enc = calc_next_encounter(rng=rng, has_3d_monsters=False)  # TODO: Check for manips
        if self.do_encounter_manip(blackboard=blackboard):
            return True
        self._navigate_to_checkpoint(blackboard=blackboard)
        return False

    def check_farming_goals(self, blackboard: dict) -> bool:
        nav_done = self._nav_done()
        farm_done = self._farm_done()

        if nav_done and not farm_done:
            self.goal.farm(blackboard=blackboard)

        return nav_done and farm_done

    def execute(self, delta: float, blackboard: dict) -> bool:
        mem = get_zelda_memory()
        # For some reason, this flag is set when in ATB combat
        if mem.player.not_in_control:
            # Check for active battle (returns True on completion/non-execution)
            if self.battle_handler.execute(delta=delta, blackboard=blackboard):
                # Handle non-battle reasons for losing control
                # TODO: Just cutscenes for now, might need logic for skips here
                _tap_confirm()
            return False

        # Else navigate the world, checking for farming goals
        if self.navigate_to_goal(blackboard=blackboard):
            return False

        if done := self.check_farming_goals(blackboard=blackboard):
            logger.debug(f"Finished moved2D section: {self.name}")
        return done

    def render(self, window: WindowLayout, blackboard: dict) -> None:
        # Check for acvite battle
        if self.battle_handler.active:
            self.battle_handler.render(window=window, blackboard=blackboard)
            return

        super().render(window, blackboard)

        if self.next_enc:
            mem = get_zelda_memory()
            enc_timer = mem.player.encounter_timer
            window.stats.addstr(12, 1, f" Next enc ({enc_timer:.3f}):")
            window.stats.addstr(13, 1, f"  {self.next_enc.name}")

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

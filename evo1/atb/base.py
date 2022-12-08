import logging
from enum import Enum, auto
from typing import List

import evo1.control
from engine.mathlib import Vec2
from engine.seq import SeqBase
from evo1.memory import BattleEntity, BattleMemory, MapID, get_memory
from memory.rng import EvolandRNG
from term.window import WindowLayout

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


def calc_next_encounter(
    rng: EvolandRNG.RNGStruct, has_3d_monsters: bool = False
) -> EncounterID:
    rng_value = rng.rand_int() & 0x3FFFFFFF
    map_id = get_memory().map_id
    modulo = 0xA
    if map_id == MapID.CRYSTAL_CAVERN:
        lut_value = rng_value % modulo
        match lut_value:
            case 0 | 1 | 2:
                return EncounterID.SCAVEN_2
            case 3 | 4 | 5:
                return EncounterID.KOBRA
            case 6 | 7:
                return EncounterID.TORK
            case 8:
                return EncounterID.KOBRA_2
            case _:
                return EncounterID.SCAVEN_2_TORK
    elif not has_3d_monsters:  # Overworld 2D
        lut_value = rng_value % modulo
        match lut_value:
            case 0 | 1 | 2:
                return EncounterID.SLIME
            case 3 | 4 | 5:
                return EncounterID.EMUK
            case 6 | 7:
                return EncounterID.SLIME_2
            case 8:
                return EncounterID.SLIME_EMUK
            case _:
                return EncounterID.SLIME_3
    else:
        # Overworld 3D
        modulo = 0x7
        lut_value = rng_value % modulo
        match lut_value:
            case 0 | 1 | 2:
                return EncounterID.ZOOMBA_2_APIDYA
            case 3 | 4:
                return EncounterID.APIDYA
            case 5:
                return EncounterID.ZOOMBA_2_ATUIN
            case 6:
                return EncounterID.ZOOMBA_APIDYA


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

    def execute(self, delta: float) -> bool:
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
        # accuracy = 10  # TODO: from attacker
        # evade = 10  # TODO: from defender
        miss_chance = 30  # TODO: Calc
        roll = (rng.rand_int() & 0x3FFFFFFF) % 100
        return roll >= miss_chance

    # TODO: Actual combat logic
    # TODO: Overload with more complex
    def handle_combat(self):
        # TODO: Very, very dumb combat.
        _tap_confirm()

    # TODO: Render combat state
    def render(self, window: WindowLayout) -> None:
        if not self.active:
            return
        window.stats.erase()
        window.stats.write_centered(line=1, text="Evoland 1 TAS")
        window.stats.write_centered(line=2, text="ATB Combat")

        window.stats.addstr(Vec2(1, 4), "Party:")
        self._print_group(window=window, group=self.mem.allies, y_offset=5)
        window.stats.addstr(Vec2(1, 8), "Enemies:")
        self._print_group(window=window, group=self.mem.enemies, y_offset=9)

        # TODO: Hit/Damage prediction
        # TODO: Who is acting?
        if not self.mem.ended:
            # TODO: Damage prediction for Kaeris
            dmg = self.predict_damage(self.mem.allies[0], self.mem.enemies[0])
            window.stats.addstr(Vec2(1, 13), "Damage prediction:")
            window.stats.addstr(Vec2(2, 14), f"Clink: {dmg}")

        # TODO: map representation

    def _print_group(
        self, window: WindowLayout, group: List[BattleEntity], y_offset: int
    ) -> None:
        for i, entity in enumerate(group):
            y_pos = y_offset + i
            window.stats.addstr(
                Vec2(2, y_pos),
                f"{entity.cur_hp}/{entity.max_hp} [{entity.turn_gauge:.02f}]",
            )

    def __repr__(self) -> str:
        if self.active:
            return (
                f"Battle ended ({self.name})"
                if self.mem.ended
                else f"In battle ({self.name})"
            )
        return f"Waiting for battle to start ({self.name})"

    @property
    def active(self):
        return self.mem is not None and self.mem.battle_active

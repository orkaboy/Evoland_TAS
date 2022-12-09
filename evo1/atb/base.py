import logging
from enum import Enum, auto

import evo1.control
from engine.mathlib import Vec2
from engine.seq import SeqBase
from evo1.memory import BattleEntity, BattleMemory, MapID, get_memory
from memory.rng import EvolandRNG
from term.window import WindowLayout

logger = logging.getLogger(__name__)


class ATBEnemyID(Enum):
    CLINK = auto()
    KAERIS = auto()
    # Bosses
    KEFKAS_GHOST = auto()
    ZEPHYROS = auto()
    # Overworld 2D
    SLIME = auto()
    EMUK = auto()
    # Cavern
    SCAVEN = auto()
    KOBRA = auto()
    TORK = auto()
    # Overworld 3D
    ZOOMBA = auto()
    APIDYA = auto()
    ATUIN = auto()


class EncounterID(Enum):
    # Overworld 2D
    SLIME = auto()
    EMUK = auto()
    SLIME_2 = auto()
    SLIME_EMUK = auto()
    SLIME_3 = auto()
    # Crystal Caverns
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


class ATBEnemy:
    def __init__(self, kind: ATBEnemyID, turn_gauge: float) -> None:
        self.kind = kind
        self.turn_gauge = turn_gauge


class AttackPrediction:
    def __init__(self, dmg: int, hit: bool, max_hp: int) -> None:
        self.dmg = dmg
        self.hit = hit
        self.one_shot = dmg >= max_hp

    def __repr__(self) -> str:
        return f"{'KO' if self.one_shot else 'hit'}: {self.dmg}" if self.hit else "miss"

    def __eq__(self, other: object) -> bool:
        ko = self.one_shot == other.one_shot
        miss = self.hit is False and self.hit == other.hit
        return True if miss else True if ko else self.dmg == other.dmg


class Encounter:
    def __init__(
        self, id: EncounterID, enemies: list[ATBEnemy], first_turn: AttackPrediction
    ) -> None:
        self.id = id
        self.enemies = enemies
        self.first_turn = first_turn

    def __repr__(self) -> str:
        return f"{self.id.name}: {self.first_turn}"

    def __eq__(self, other: object) -> bool:
        return self.id == other.id and self.first_turn == other.first_turn


def _get_enc_enemies(enc: EncounterID) -> list[ATBEnemyID]:
    match enc:
        # Overworld 2D
        case EncounterID.SLIME:
            return [ATBEnemyID.SLIME]
        case EncounterID.EMUK:
            return [ATBEnemyID.EMUK]
        case EncounterID.SLIME_2:
            return [ATBEnemyID.SLIME, ATBEnemyID.SLIME]
        case EncounterID.SLIME_EMUK:
            return [ATBEnemyID.EMUK, ATBEnemyID.SLIME]
        case EncounterID.SLIME_3:
            return [ATBEnemyID.SLIME, ATBEnemyID.SLIME, ATBEnemyID.SLIME]
        # Crystal Caverns
        case EncounterID.SCAVEN_2:
            return [ATBEnemyID.SCAVEN, ATBEnemyID.SCAVEN]
        case EncounterID.KOBRA:
            return [ATBEnemyID.KOBRA]
        case EncounterID.TORK:
            return [ATBEnemyID.TORK]
        case EncounterID.KOBRA_2:
            return [ATBEnemyID.KOBRA, ATBEnemyID.KOBRA]
        case EncounterID.SCAVEN_2_TORK:
            return [ATBEnemyID.TORK, ATBEnemyID.SCAVEN, ATBEnemyID.SCAVEN]
        # Overworld 3D
        # TODO: Check order of the enemies?
        case EncounterID.ZOOMBA_2_APIDYA:
            return [ATBEnemyID.APIDYA, ATBEnemyID.ZOOMBA, ATBEnemyID.ZOOMBA]
        case EncounterID.APIDYA:
            return [ATBEnemyID.APIDYA]
        case EncounterID.ZOOMBA_2_ATUIN:
            return [ATBEnemyID.ZOOMBA, ATBEnemyID.ZOOMBA, ATBEnemyID.ATUIN]
        case EncounterID.ZOOMBA_APIDYA:
            return [ATBEnemyID.APIDYA, ATBEnemyID.ZOOMBA]


def _get_enc_kind(rng_value: int, has_3d_monsters: bool = False) -> EncounterID:
    map_id = get_memory().map_id
    modulo = 0xA
    # Crystal Caverns
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


class ATBEnemyStats:
    def __init__(self, id: ATBEnemyID, level: int = 1) -> None:
        match id:
            case ATBEnemyID.CLINK:
                self.max_hp = 100
                # TODO: Check gear
                self.attack = 8  # baby sword, lvl1
                if level >= 2:
                    self.attack = 21  # long sword, lvl2
                else:
                    self.attack = 20  # long sword, lvl1
                # TODO: Check gear
                self.defense = 0
                if level >= 3:
                    self.defense = 6  # armor, lvl3
                else:
                    self.defense = 5  # armor, lvl1
                self.magic = 12
                self.evade = 0
            case ATBEnemyID.KAERIS:
                self.max_hp = 70
                self.attack = 10
                if level >= 2:
                    self.defense = 6  # lvl2
                else:
                    self.defense = 5  # lvl1
                if level >= 3:
                    self.magic = 6  # lvl3
                else:
                    self.magic = 5  # lvl1
                self.evade = 0
            # Bosses
            case ATBEnemyID.KEFKAS_GHOST:
                self.max_hp = 250
                self.attack = 22
                self.defense = 5
                self.magic = 0
                self.evade = 0
            case ATBEnemyID.ZEPHYROS:
                self.max_hp = 250
                # TODO: Stats
                self.attack = 5
                self.defense = 0
                self.magic = 0
                self.evade = 0
            # Enemies
            case ATBEnemyID.SLIME:
                self.max_hp = 12
                self.attack = 5
                self.defense = 0
                self.magic = 0
                self.evade = 0
            case ATBEnemyID.EMUK:
                self.max_hp = 20
                self.attack = 7
                self.defense = 2
                self.magic = 0
                self.evade = 0
            case ATBEnemyID.SCAVEN:
                self.max_hp = 11
                self.attack = 7
                self.defense = 2
                self.magic = 0
                self.evade = 0
            case ATBEnemyID.KOBRA:
                self.max_hp = 15
                self.attack = 10
                self.defense = 10
                self.magic = 0
                self.evade = 30
            case ATBEnemyID.TORK:
                self.max_hp = 15
                self.attack = 18
                self.defense = 17
                self.magic = 0
                self.evade = 0
            case ATBEnemyID.ZOOMBA:
                self.max_hp = 30
                self.attack = 10
                self.defense = 5
                self.magic = 0
                self.evade = 0
            case ATBEnemyID.ATUIN:
                self.max_hp = 50
                self.attack = 15
                self.defense = 15
                self.magic = 0
                self.evade = 0
            case ATBEnemyID.APIDYA:
                self.max_hp = 19
                self.attack = 16
                self.defense = 5
                self.magic = 0
                self.evade = 25
            # TODO: More stat blocks
            case _:
                self.max_hp = 0
                self.attack = 0
                self.defense = 0
                self.magic = 0
                self.evade = 0


def _predict_attack(
    rng: EvolandRNG.RNGStruct, attacker: ATBEnemyStats, defender: ATBEnemyStats
) -> AttackPrediction:
    dmg = _predict_damage(attacker.attack, defender.defense, rng.rand_float())
    hit = _predict_hit(attacker.accuracy, defender.evade, rng.rand_int())
    max_hp = defender.max_hp
    return AttackPrediction(dmg, hit, max_hp)


def calc_next_encounter(
    rng: EvolandRNG.RNGStruct, has_3d_monsters: bool = False
) -> Encounter:
    rng_value = rng.rand_int() & 0x3FFFFFFF
    enc_kind = _get_enc_kind(rng_value, has_3d_monsters)
    enemy_ids = [ATBEnemyID(ekind) for ekind in _get_enc_enemies(enc_kind)]
    enemies = [ATBEnemy(id, rng.rand_float()) for id in enemy_ids]
    return Encounter(
        enc_kind, enemies, AttackPrediction(rng, ATBEnemyStats(enemy_ids[0]))
    )


def _tap_confirm() -> None:
    ctrl = evo1.control.handle()
    ctrl.dpad.none()
    ctrl.confirm(tapping=True)


# Att + (0.5 * Att * random_float) - enemy_def
def _predict_damage(attack: int, defense: int, rng_float: float) -> int:
    return int(attack + (0.5 * attack * rng_float) - defense + 0.5)


def _predict_hit(accuracy: int, evade: int, rng_int: int) -> bool:
    miss_chance = 30  # TODO: Calc from accuracy/evade
    roll = (rng_int & 0x3FFFFFFF) % 100
    return roll >= miss_chance


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
    def predict_damage(
        self, rng: EvolandRNG.RNGStruct, attacker: BattleEntity, defender: BattleEntity
    ) -> int:
        rand_float = rng.rand_float()
        return _predict_damage(attacker.attack, defender.defense, rand_float)

    def predict_hit(
        self, rng: EvolandRNG.RNGStruct, attacker: BattleEntity, defender: BattleEntity
    ) -> bool:
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
            rng = EvolandRNG().get_rng()
            dmg = self.predict_damage(rng, self.mem.allies[0], self.mem.enemies[0])
            window.stats.addstr(Vec2(1, 13), "Damage prediction:")
            window.stats.addstr(Vec2(2, 14), f"Clink: {dmg}")

        # TODO: map representation

    def _print_group(
        self, window: WindowLayout, group: list[BattleEntity], y_offset: int
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

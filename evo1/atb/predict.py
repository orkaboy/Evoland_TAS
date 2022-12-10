import logging

from evo1.atb.entity import ATBEntityStats
from memory.rng import EvolandRNG

logger = logging.getLogger(__name__)


class AttackPrediction:
    def __init__(self, dmg: int, hit: bool, cur_hp: int) -> None:
        self.dmg = dmg
        self.hit = hit
        self.one_shot = dmg >= cur_hp

    def __repr__(self) -> str:
        return f"{'KO' if self.one_shot else 'hit'}: {self.dmg}" if self.hit else "miss"

    def __eq__(self, other: object) -> bool:
        ko = self.one_shot == other.one_shot
        miss = self.hit is False and self.hit == other.hit
        return True if miss else True if ko else self.dmg == other.dmg


def predict_attack(
    rng: EvolandRNG.RNGStruct, attacker: ATBEntityStats, defender: ATBEntityStats
) -> AttackPrediction:
    dmg = _predict_damage(attacker.attack, defender.defense, rng.rand_float())
    hit = _predict_hit(defender.evade, rng.rand_int())
    cur_hp = defender.cur_hp
    return AttackPrediction(dmg=dmg, hit=hit, cur_hp=cur_hp)


# Att + (0.5 * Att * random_float) - enemy_def
def _predict_damage(attack: int, defense: int, rng_float: float) -> int:
    return int(attack + (0.5 * attack * rng_float) - defense + 0.5)


def _predict_hit(evade: int, rng_int: int) -> bool:
    roll = (rng_int & 0x3FFFFFFF) % 100
    return roll >= evade

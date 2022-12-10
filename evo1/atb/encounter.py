import logging
from enum import Enum, auto

from evo1.atb.entity import ATBEntity, ATBEntityID, atb_stats_from_id
from evo1.atb.predict import AttackPrediction, predict_attack
from evo1.memory import MapID, get_memory
from memory.rng import EvolandRNG

logger = logging.getLogger(__name__)


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


class Encounter:
    def __init__(
        self,
        enc_id: EncounterID,
        enemies: list[ATBEntity],
        first_turn: AttackPrediction,
    ) -> None:
        self.enc_id = enc_id
        self.enemies = enemies
        self.first_turn = first_turn

    def __repr__(self) -> str:
        return f"{self.enc_id.name}: {self.first_turn}"

    def __eq__(self, other: object) -> bool:
        return self.enc_id == other.enc_id and self.first_turn == other.first_turn


def get_enc_enemies(enc: EncounterID) -> list[ATBEntityID]:
    match enc:
        # Overworld 2D
        case EncounterID.SLIME:
            return [ATBEntityID.SLIME]
        case EncounterID.EMUK:
            return [ATBEntityID.EMUK]
        case EncounterID.SLIME_2:
            return [ATBEntityID.SLIME, ATBEntityID.SLIME]
        case EncounterID.SLIME_EMUK:
            return [ATBEntityID.EMUK, ATBEntityID.SLIME]
        case EncounterID.SLIME_3:
            return [ATBEntityID.SLIME, ATBEntityID.SLIME, ATBEntityID.SLIME]
        # Crystal Caverns
        case EncounterID.SCAVEN_2:
            return [ATBEntityID.SCAVEN, ATBEntityID.SCAVEN]
        case EncounterID.KOBRA:
            return [ATBEntityID.KOBRA]
        case EncounterID.TORK:
            return [ATBEntityID.TORK]
        case EncounterID.KOBRA_2:
            return [ATBEntityID.KOBRA, ATBEntityID.KOBRA]
        case EncounterID.SCAVEN_2_TORK:
            return [ATBEntityID.TORK, ATBEntityID.SCAVEN, ATBEntityID.SCAVEN]
        # Overworld 3D
        case EncounterID.ZOOMBA_2_APIDYA:
            return [ATBEntityID.APIDYA, ATBEntityID.ZOOMBA, ATBEntityID.ZOOMBA]
        case EncounterID.APIDYA:
            return [ATBEntityID.APIDYA]
        case EncounterID.ZOOMBA_2_ATUIN:
            return [ATBEntityID.ZOOMBA, ATBEntityID.ZOOMBA, ATBEntityID.ATUIN]
        case EncounterID.ZOOMBA_APIDYA:
            return [ATBEntityID.APIDYA, ATBEntityID.ZOOMBA]


def get_enc_kind(rng_value: int, has_3d_monsters: bool = False) -> EncounterID:
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


def calc_next_encounter(
    rng: EvolandRNG.RNGStruct, has_3d_monsters: bool = False, clink_level: int = 0
) -> Encounter:
    rng_value = rng.rand_int() & 0x3FFFFFFF
    enc_kind = get_enc_kind(rng_value, has_3d_monsters)
    enemy_ids = list(get_enc_enemies(enc_kind))
    enemies = [ATBEntity(id, rng.rand_float()) for id in enemy_ids]
    return Encounter(
        enc_kind,
        enemies,
        predict_attack(
            rng,
            atb_stats_from_id(ATBEntityID.CLINK, level=clink_level),
            atb_stats_from_id(enemy_ids[0]),
        ),
    )

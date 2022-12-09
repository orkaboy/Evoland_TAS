import logging
from enum import Enum, auto

from evo1.memory.atb import BattleEntity

logger = logging.getLogger(__name__)


class ATBEntityID(Enum):
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


class ATBEntity:
    def __init__(self, kind: ATBEntityID, turn_gauge: float) -> None:
        self.kind = kind
        self.turn_gauge = turn_gauge


class ATBEntityStats:
    def __init__(
        self,
        max_hp: int,
        cur_hp: int,
        attack: int,
        defense: int,
        magic: int,
        evade: int,
    ) -> None:
        self.cur_hp = cur_hp
        self.max_hp = max_hp
        self.attack = attack
        self.defense = defense
        self.magic = magic
        self.evade = evade


def atb_stats_from_id(entity_id: ATBEntityID, level: int = 0) -> ATBEntityStats:
    match entity_id:
        case ATBEntityID.CLINK:
            max_hp = 100
            if level >= 2:
                attack = 21  # long sword, lvl2
            elif level >= 1:
                attack = 20  # long sword, lvl1
            else:
                attack = 8  # baby sword
            if level >= 3:
                defense = 6  # armor, lvl3
            elif level >= 1:
                defense = 5  # armor, lvl1
            else:
                defense = 0  # no armor
            magic = 12
            evade = 0
        case ATBEntityID.KAERIS:
            max_hp = 70
            attack = 10
            if level >= 2:
                defense = 6  # lvl2
            else:
                defense = 5  # lvl1
            if level >= 3:
                magic = 6  # lvl3
            else:
                magic = 5  # lvl1
            evade = 0
        # Bosses
        case ATBEntityID.KEFKAS_GHOST:
            max_hp = 250
            attack = 22
            defense = 5
            magic = 0
            evade = 0
        case ATBEntityID.ZEPHYROS:
            max_hp = 250
            # TODO: Stats
            attack = 5
            defense = 0
            magic = 0
            evade = 0
        # Enemies
        case ATBEntityID.SLIME:
            max_hp = 12
            attack = 5
            defense = 0
            magic = 0
            evade = 0
        case ATBEntityID.EMUK:
            max_hp = 20
            attack = 7
            defense = 2
            magic = 0
            evade = 0
        case ATBEntityID.SCAVEN:
            max_hp = 11
            attack = 7
            defense = 2
            magic = 0
            evade = 0
        case ATBEntityID.KOBRA:
            max_hp = 15
            attack = 10
            defense = 10
            magic = 0
            evade = 30
        case ATBEntityID.TORK:
            max_hp = 15
            attack = 18
            defense = 17
            magic = 0
            evade = 0
        case ATBEntityID.ZOOMBA:
            max_hp = 30
            attack = 10
            defense = 5
            magic = 0
            evade = 0
        case ATBEntityID.ATUIN:
            max_hp = 50
            attack = 15
            defense = 15
            magic = 0
            evade = 0
        case ATBEntityID.APIDYA:
            max_hp = 19
            attack = 16
            defense = 5
            magic = 0
            evade = 25
        # TODO: More stat blocks
        case _:
            max_hp = 0
            attack = 0
            defense = 0
            magic = 0
            evade = 0

    return ATBEntityStats(
        max_hp=max_hp,
        cur_hp=max_hp,
        attack=attack,
        defense=defense,
        magic=magic,
        evade=evade,
    )


def atb_stats_from_memory(entity: BattleEntity) -> ATBEntityStats:
    return ATBEntityStats(
        max_hp=entity.max_hp,
        cur_hp=entity.cur_hp,
        attack=entity.attack,
        defense=entity.defense,
        magic=entity.magic,
        evade=entity.evade,
    )

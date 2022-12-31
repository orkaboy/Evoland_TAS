from enum import IntEnum

from memory.core import LocProcess
from memory.evo2.entity.fighter import entZFighter


class MobState(IntEnum):
    START = 0
    STAND = 1
    PATROL = 2
    AGGRO = 3
    ATTACK = 4
    JUMP = 5
    CHARGE = 6
    DODGE = 7
    FLEE = 8
    RUN = 9
    HURT = 10
    DEAD = 11
    SLEEP = 12
    SPECIAL = 13
    SWIM = 14
    TURN = 15
    FALL = 16
    STUN = 17
    TP = 18
    LAUGH = 19
    BOLT = 20
    CHANGE_MODE = 21


class MobData:
    """HVIRTUAL mob data."""

    _ATTACK_PTR = [0xC, 0x0]  # int
    _DEFENSE_PTR = [0x10, 0x0]  # int
    _DROP_KIND_PTR = [0x14, 0x0]  # ptr to HOBJ or 0
    _FLAGS_PTR = [0x18, 0x0]  # int
    _ID_PTR = [0x1C, 0x0]  # ptr to String
    _IMAGE_PTR = [0x20, 0x0]  # ptr to HVIRTUAL
    _LIFE_PTR = [0x24, 0x0]  # int
    _NAME_PTR = [0x28, 0x0]  # ptr to HOBJ
    _NPC_REF_PTR = [0x2C, 0x0]  # ptr to HOBJ
    _SPEED_PTR = [0x30, 0x0]  # double
    _XP_PTR = [0x34, 0x0]  # int

    def __init__(self, process: LocProcess, base_ptr: int = 0) -> None:
        self.process = process
        self.base_ptr = base_ptr

    @property
    def attack(self) -> int:
        ptr = self.process.get_pointer(self.base_ptr, offsets=self._ATTACK_PTR)
        return self.process.read_u32(ptr)

    @property
    def defense(self) -> int:
        ptr = self.process.get_pointer(self.base_ptr, offsets=self._DEFENSE_PTR)
        return self.process.read_u32(ptr)

    @property
    def life(self) -> int:
        ptr = self.process.get_pointer(self.base_ptr, offsets=self._LIFE_PTR)
        return self.process.read_u32(ptr)

    @property
    def xp(self) -> int:
        ptr = self.process.get_pointer(self.base_ptr, offsets=self._XP_PTR)
        return self.process.read_u32(ptr)

    # TODO: More stuff


# Only valid when instantiated, on the screen that they live
class entZMob(entZFighter):
    """ent.z.Mob hashlink class."""

    _C_PTR = [0xB4]  # ptr to HOBJ
    _MOB_STATE_PTR = [0xB8, 0x4]  # ptr to HENUM, MobState
    _PATROL_TIME_PTR = [0xC0]  # double
    _PATROL_SLEEP_PTR = [0xC8]  # double
    _HURT_LOCK_PTR = [0xD0]  # bool
    _CELL_TARGET_PTR = [0xD4]  # ptr to HOBJ
    _DATA_PTR = [0xD8]  # ptr to HOBJ. Template for mob!
    _AUTO_HERO_COLLIDE_PTR = [0xDC]  # bool
    _DIED_PLAYED_PTR = [0xDD]  # bool
    _HERO_HIT_BOUNDS_PTR = [0xE0]  # ptr to HOBJ
    _SAVE_POS_PTR = [0xE4]  # ptr to HOBJ
    _SAVE_CPT_PTR = [0xE8]  # double
    _AGGRO_DECAL_PTR = [0xF0]  # double

    def __init__(self, process: LocProcess, entity_ptr: int = 0) -> None:
        super().__init__(process, entity_ptr)
        data_ptr = self.process.get_pointer(self.entity_ptr, offsets=self._DATA_PTR)
        self.data = MobData(process, data_ptr)

    @property
    def mob_state(self) -> MobState:
        ptr = self.process.get_pointer(self.entity_ptr, offsets=self._MOB_STATE_PTR)
        mstate = self.process.read_u32(ptr)
        return MobState(mstate)

    @property
    def is_enemy(self) -> bool:
        """Used by enemy tracking/sorting."""
        # TODO: Ugly way of determining if a Mob is an enemy or not (sorting out pots/bushes etc)
        return self.data.attack != 0

    def __repr__(self) -> str:
        try:
            return f"Mob({self.pos}, hp: {self.life})"
        except ReferenceError:
            return "BADREF"

    # TODO: Implement a bunch of stuff

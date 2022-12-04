# Libraries and Core Files
import logging
from enum import Flag, auto, Enum, IntEnum
from typing import List, Optional, Tuple

from engine.mathlib import Vec2, Facing

import memory.core
from memory.core import LocProcess

logger = logging.getLogger(__name__)

# Representation of game features picked up from chests
class GameFeatures(Flag):
    MoveSmooth = auto()


_LIBHL_OFFSET = 0x0004914C



# TODO RNG Calculations
# Evoland1 specific stuff

# Clinks attack in ATB combat
# Att + (0.5 * Att * random_float) - enemy_def

# Maybe correct formulas for stats. Should be readable in memory while in combat
# Att: 8 + round(level / 3) + modifiers
# Def:  0 + floor(level / 3) + modifiers
# HP: 100 + (ceil(level / 3) * 5 - 5)



class MapID(Enum):
    EDEL_VALE = 0
    OVERWORLD = 1
    MEADOW = 2
    PAPURIKA = 3
    PAPURIKA_WELL = 4
    NORIA_CLOSED = 5
    NORIA = 6
    CRYSTAL_CAVERN = 7
    PAPURIKA_INTERIOR = 8
    HIDDEN_MEADOW = 9
    HIDDEN_MEADON_CAVE = 10
    LIMBO = 11
    AOGAI = 12
    SACRED_GROVE_2D = 13
    SACRED_GROVE_3D = 14
    SARUDNAHK = 15
    SACRED_GROVE_CAVE_1 = 16
    SACRED_GROVE_CAVE_2 = 17
    BABAMUT_SHRINE = 18
    FORBIDDEN_LAKE_2D = 19
    FORBIDDEN_LAKE_3D = 20
    END = 21


# TODO: Refactor (currently only used in very specific cases)
class Evoland1Memory:

    # Zelda player health for roaming battle (hearts)
    _PLAYER_HP_ZELDA_PTR = [0x7FC, 0x8, 0x30, 0x7C, 0x0] # each heart is 16 "health"
    _GLI_PTR = [0x7FC, 0x8, 0x30, 0x84, 0x0] # Money

    _MAP_ID_PTR = [0x7FC, 0x8, 0x30, 0xC8, 0x0, 0x4]

    # TODO: Verify these are useful/correct (got from mem searching)
    _PLAYER_MAX_HP_ZELDA_PTR = [0x7FC, 0x8, 0x30, 0x80, 0x0]
    _PLAYER_HP_OVERWORLD_PTR = [0x7FC, 0x8, 0x30, 0x3C, 0x0]
    _KAERIS_HP_OVERWORLD_PTR = [0x7FC, 0x8, 0x30, 0x48]
    _LEVEL_ARRAY_SIZE_PTR = [0x7FC, 0x8, 0x30, 0x78, 0x0, 0x4] # Should be 2
    _PLAYER_LVL_PTR = [0x7FC, 0x8, 0x30, 0x78, 0x0, 0x8, 0x10, 0x8, 0x0] # int
    _PLAYER_EXP_PTR = [0x7FC, 0x8, 0x30, 0x78, 0x0, 0x8, 0x10, 0x8, 0x4] # int
    _KAERIS_LVL_PTR = [0x7FC, 0x8, 0x30, 0x78, 0x0, 0x8, 0x14, 0x8, 0x0] # int
    _KAERIS_EXP_PTR = [0x7FC, 0x8, 0x30, 0x78, 0x0, 0x8, 0x14, 0x8, 0x4] # int

    # TODO: Split battle stuff into own memory block
    # Only valid in atb battle
    _PLAYER_ATB_CUR_HP_PTR = [0x860, 0x0, 0x244, 0x2C, 0x8, 0x10, 0xF4]

    _ENEMY_ATB_CUR_HP_PTR = [0x860, 0x0, 0x244, 0x30, 0x8, 0x10, 0xF4]
    # Only valid when menu is open
    _PLAYER_ATB_MENU_CURSOR_PTR = [0x860, 0x0, 0x244, 0x48, 0x8C]

    def __init__(self):
        mem_handle = memory.core.handle()
        self.process = mem_handle.process
        self.base_addr = mem_handle.base_addr
        self.setup_pointers()

    def setup_pointers(self):
        self.player_hp_overworld_ptr = self.process.get_pointer(
            self.base_addr + _LIBHL_OFFSET, offsets=self._PLAYER_HP_OVERWORLD_PTR
        )
        self.gli_ptr = self.process.get_pointer(
            self.base_addr + _LIBHL_OFFSET, offsets=self._GLI_PTR
        )
        self.map_id_ptr = self.process.get_pointer(
            self.base_addr + _LIBHL_OFFSET, self._MAP_ID_PTR
        )

    # Only valid in zelda map
    def get_player_hearts(self) -> float:
        player_hearts_ptr = self.process.get_pointer(
            self.base_addr + _LIBHL_OFFSET, offsets=self._PLAYER_HP_ZELDA_PTR
        )
        return self.process.read_double(player_hearts_ptr)

    def get_gli(self) -> int:
        return self.process.read_u32(self.gli_ptr)

    def get_lvl(self) -> int:
        # TODO: Implement level
        return 1

    def get_map_id(self) -> MapID:
        return MapID(self.process.read_u32(self.map_id_ptr))

    # Only valid in battle!
    def get_atb_player_hp(self) -> int:
        atb_player_hp_ptr = self.process.get_pointer(
            self.base_addr + _LIBHL_OFFSET, offsets=self._PLAYER_ATB_CUR_HP_PTR
        )
        return self.process.read_u32(atb_player_hp_ptr)

    def get_atb_menu_cursor(self) -> int:
        atb_menu_cursor_ptr = self.process.get_pointer(
            self.base_addr + _LIBHL_OFFSET,
            offsets=self._PLAYER_ATB_MENU_CURSOR_PTR,
        )
        return self.process.read_u32(atb_menu_cursor_ptr)

    def get_player_hp_overworld(self) -> int:
        return self.process.read_u32(self.player_hp_overworld_ptr)


_mem = None


def load_memory() -> None:
    global _mem
    _mem = Evoland1Memory()


def get_memory() -> Evoland1Memory:
    return _mem


# Only valid when instantiated, on the screen that they live
class GameEntity2D:
    _ENT_KIND_PTR = [0x4, 0x4]  # int
    _X_PTR = [0x8]  # double
    _Y_PTR = [0x10]  # double
    _X_TILE_PTR = [0x14]  # int
    _Y_TILE_PTR = [0x18]  # int
    _SPEED_PTR = [0x20]  # double (quite small numbers, 0.05 for player)
    _TARGET_PTR = [0x40]  # Target pointer. Only valid if != 0
    _TARGET_X_OFFSET = 0x18  # In reference to Target
    _TARGET_Y_OFFSET = 0x20  # In reference to Target
    _TIMER_PTR = [0x48]  # double (timeout in s)
    _FACING_PTR = [0x58]  # int
    _ATTACK_PTR = [0x5C]  # byte, bit 5
    _ROTATION_PTR = [0x90]  # double (left = 0.0, up = 1.57, right = 3.14, down = -1.57)
    _HP_PTR = [0x100]  # int, for enemies such as knights
    # TODO Verify these
    #_ATTACK_TIMER_PTR = [0xC8]  # double unclear purpose, resets when swinging sword
    _ENCOUNTER_TIMER_PTR = [0xD0]  # double. Steps to encounter
    # This seems to be set on picking up stuff/opening inventory/opening menu, may be misnamed. Invincibility flag?
    # This is also marked when in ATB combat. GUI open?
    _INV_OPEN_PTR = [0xA4]

    def __init__(self, process: LocProcess, entity_ptr: int):
        self.process = process
        self.entity_ptr = entity_ptr
        self.setup_pointers()

    def setup_pointers(self):
        self.ent_kind_ptr = self.process.get_pointer(self.entity_ptr, offsets=self._ENT_KIND_PTR)
        self.x_ptr = self.process.get_pointer(self.entity_ptr, offsets=self._X_PTR)
        self.y_ptr = self.process.get_pointer(self.entity_ptr, offsets=self._Y_PTR)
        self.x_tile_ptr = self.process.get_pointer(
            self.entity_ptr, offsets=self._X_TILE_PTR
        )
        self.y_tile_ptr = self.process.get_pointer(
            self.entity_ptr, offsets=self._Y_TILE_PTR
        )
        self.speed_ptr = self.process.get_pointer(
            self.entity_ptr, offsets=self._SPEED_PTR
        )
        self.target_ptr = self.process.get_pointer(
            self.entity_ptr, offsets=self._TARGET_PTR
        )
        self.timer_ptr = self.process.get_pointer(
            self.entity_ptr, offsets=self._TIMER_PTR
        )
        self.facing_ptr = self.process.get_pointer(
            self.entity_ptr, offsets=self._FACING_PTR
        )
        self.attack_ptr = self.process.get_pointer(
            self.entity_ptr, offsets=self._ATTACK_PTR
        )
        self.rotation_ptr = self.process.get_pointer(
            self.entity_ptr, offsets=self._ROTATION_PTR
        )
        self.hp_ptr = self.process.get_pointer(
            self.entity_ptr, offsets=self._HP_PTR
        )
        self.inv_open_ptr = self.process.get_pointer(
            self.entity_ptr, offsets=self._INV_OPEN_PTR
        )
        self.encounter_timer_ptr = self.process.get_pointer(
            self.entity_ptr, offsets=self._ENCOUNTER_TIMER_PTR
        )

    class EKind(IntEnum):
        PLAYER = 0
        # TODO 1=?
        ENEMY = 2
        CHEST = 3
        ITEM = 4
        NPC = 5
        PARTICLE = 6 # When breaking pots, closing bars?
        SPECIAL = 7
        UNKNOWN = 999

    # TODO: EKind Enum instead of str
    def get_kind(self) -> EKind:
        kind_val = self.process.read_u32(self.ent_kind_ptr)
        try:
            return GameEntity2D.EKind(kind_val)
        except ValueError:
            logger.error(f"Unknown GameEntity2D EKind: {kind_val}")
            return GameEntity2D.EKind.UNKNOWN

    def get_pos(self) -> Vec2:
        return Vec2(
            self.process.read_double(self.x_ptr),
            self.process.read_double(self.y_ptr),
        )

    def get_tile_pos(self) -> Tuple[int, int]:
        return [
            self.process.read_u32(self.x_tile_ptr),
            self.process.read_u32(self.y_tile_ptr),
        ]

    def get_speed(self) -> float:
        return self.process.read_double(self.speed_ptr)

    def get_target(self) -> Optional[Vec2]:
        target_ptr = self.process.read_u32(self.target_ptr)
        if target_ptr != 0:
            return Vec2(
                x=self.process.read_double(target_ptr + self._TARGET_X_OFFSET),
                y=self.process.read_double(target_ptr + self._TARGET_Y_OFFSET),
            )
        return None

    def get_timer(self) -> float:
        return self.process.read_double(self.timer_ptr)

    # 0=left,1=right,2=up,3=down. Doesn't do diagonal facings.
    def get_facing(self) -> Facing:
        return self.process.read_u32(self.facing_ptr)

    def get_attacking(self) -> bool:
        attacking = self.process.read_u8(self.attack_ptr)
        return attacking & 0x10  # Bit5 denotes attacking

    def get_rotation(self) -> float:
        return self.process.read_double(self.rotation_ptr)

    def get_hp(self) -> int:
        return self.process.read_u32(self.hp_ptr)

    def get_inv_open(self) -> bool:
        return self.process.read_u8(self.inv_open_ptr) == 1

    def get_encounter_timer(self) -> float:
        return self.process.read_double(self.encounter_timer_ptr)

    def __repr__(self) -> str:
        kind = self.get_kind()
        hp_str = f", hp: {self.get_hp()}" if kind == self.EKind.ENEMY else ""
        return f"Ent({kind.name}, {self.get_pos()}{hp_str})"


class ZeldaMemory:

    # Zelda-related things:
    _ZELDA_PTR = [0x7C8, 0x8, 0x3C]
    _PLAYER_PTR = [0x30]

    _ACTOR_ARR_PTR = [0x48, 0x8]
    _ACTOR_ARR_SIZE_PTR = [0x48, 0x4]
    _ACTOR_PTR_SIZE = 4
    _ACTOR_BASE_ADDR = 0x10

    def __init__(self):
        mem_handle = memory.core.handle()
        self.process = mem_handle.process
        self.base_addr = mem_handle.base_addr
        # logger.debug(f"Zelda base address: {hex(self.base_addr)}")
        self.base_offset = self.process.get_pointer(
            self.base_addr + _LIBHL_OFFSET, offsets=self._ZELDA_PTR
        )

        self._init_player()
        self._init_actors()

    def _init_player(self):
        player_ptr = self.process.get_pointer(self.base_offset, self._PLAYER_PTR)
        self.player = GameEntity2D(self.process, player_ptr)

    def _init_actors(self):
        self.actors: List[GameEntity2D] = []
        actor_arr_size_ptr = self.process.get_pointer(
            self.base_offset, offsets=self._ACTOR_ARR_SIZE_PTR
        )
        actor_arr_size = self.process.read_u32(actor_arr_size_ptr)
        actor_arr_offset = self.process.get_pointer(
            self.base_offset, offsets=self._ACTOR_ARR_PTR
        )
        for i in range(actor_arr_size):
            # Set enemy offsets
            actor_offset = self._ACTOR_BASE_ADDR + i * self._ACTOR_PTR_SIZE
            actor_ptr = self.process.get_pointer(actor_arr_offset, [actor_offset])
            self.actors.append(GameEntity2D(self.process, actor_ptr))


_zelda_mem = None


def load_zelda_memory() -> None:
    global _zelda_mem
    _zelda_mem = ZeldaMemory()


def get_zelda_memory() -> ZeldaMemory:
    return _zelda_mem

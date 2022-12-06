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


class BattleEntity:
    _MAX_HP_PTR = [0xF0] # int
    _CUR_HP_PTR = [0xF4] # int
    _ATK_PTR = [0xF8] # int
    _DEF_PTR = [0xFC] # int
    #_?_PTR = [0x104] # int: 12 for Clink? Acc??
    _TURN_GAUGE_PTR = [0x110] # double: [0-1.0]

    def __init__(self, process: LocProcess, entity_ptr: int):
        self.process = process
        self.entity_ptr = entity_ptr
        self.setup_pointers()

    def setup_pointers(self) -> None:
        self.max_hp_ptr = self.process.get_pointer(
            self.entity_ptr, offsets=self._MAX_HP_PTR
        )
        self.cur_hp_ptr = self.process.get_pointer(
            self.entity_ptr, offsets=self._CUR_HP_PTR
        )
        self.atk_ptr = self.process.get_pointer(
            self.entity_ptr, offsets=self._ATK_PTR
        )
        self.def_ptr = self.process.get_pointer(
            self.entity_ptr, offsets=self._DEF_PTR
        )
        self.turn_gauge_ptr = self.process.get_pointer(
            self.entity_ptr, offsets=self._TURN_GAUGE_PTR
        )

    @property
    def max_hp(self) -> int:
        return self.process.read_u32(self.max_hp_ptr)

    @property
    def cur_hp(self) -> int:
        return self.process.read_u32(self.cur_hp_ptr)

    @property
    def attack(self) -> int:
        return self.process.read_u32(self.atk_ptr)

    @property
    def defense(self) -> int:
        return self.process.read_u32(self.def_ptr)

    @property
    def turn_gauge(self) -> float:
        return self.process.read_double(self.turn_gauge_ptr)


class BattleMemory:
    # Pointer to the last/current battle
    last_battle_ptr = 0

    # All battle data is stored here
    _BATTLE_BASE_PTR = [0x860, 0x0, 0x244]
    # All allies are listed here
    _ALLIES_ARR_SIZE_PTR = [0x2C, 0x4]
    _ALLIES_ARR_BASE_PTR = [0x2C, 0x8]
    # All enemies are listed here
    _ENEMIES_ARR_SIZE_PTR = [0x30, 0x4]
    _ENEMIES_ARR_BASE_PTR = [0x30, 0x8]
    # Each list has these properties
    _FIRST_ENT_OFFSET = 0x10 # Offset from base ptr
    _ENT_PTR_SIZE = 0x4 # 0x10, 0x14...

    # Only valid when menu is open
    # TODO: Implement
    _PLAYER_ATB_MENU_CURSOR_PTR = [0x48, 0x8C]

    def __init__(self):
        # Check if we are in battle
        self.active = False
        mem = get_zelda_memory()
        in_control = mem.player.in_control
        if in_control:
            return

        # Set up memory access, get the base pointer to the battle structure
        mem_handle = memory.core.handle()
        self.process = mem_handle.process
        base_addr = mem_handle.base_addr
        self.base_offset = self.process.get_pointer(
            base_addr + _LIBHL_OFFSET, offsets=self._BATTLE_BASE_PTR
        )

        # Check if we have triggered a new battle
        if self.base_offset == BattleMemory.last_battle_ptr:
            return

        self.active = True
        self.update()

        if self.active:
            BattleMemory.last_battle_ptr = self.base_offset

    def update(self):
        try:
            self.allies = self._init_entities(array_size_ptr=self._ALLIES_ARR_SIZE_PTR, array_base_ptr=self._ALLIES_ARR_BASE_PTR)
            self.enemies = self._init_entities(array_size_ptr=self._ENEMIES_ARR_SIZE_PTR, array_base_ptr=self._ENEMIES_ARR_BASE_PTR)
            # TODO: Other battle related data? Cursors gui etc.
        except ReferenceError:
            self.active = False

    def _init_entities(self, array_size_ptr: List[int], array_base_ptr: List[int]) -> List[BattleEntity]:
        entities: List[BattleEntity] = []
        entities_arr_size_ptr = self.process.get_pointer(
            self.base_offset, offsets=array_size_ptr
        )
        entities_arr_size = self.process.read_u32(entities_arr_size_ptr)
        entities_arr_offset = self.process.get_pointer(
            self.base_offset, offsets=array_base_ptr
        )
        for i in range(entities_arr_size):
            # Set enemy offsets
            entity_offset = self._FIRST_ENT_OFFSET + i * self._ENT_PTR_SIZE
            entity_ptr = self.process.get_pointer(entities_arr_offset, [entity_offset])
            entities.append(BattleEntity(self.process, entity_ptr))
        return entities

    @property
    def ended(self) -> bool:
        # Check if every enemy is defeated, if so, battle has ended
        if len(self.enemies) == 0:
            return True
        # Check if every ally has fallen, if so, battle has ended
        return all(ally.cur_hp <= 0 for ally in self.allies)

    @property
    def battle_active(self) -> bool:
        mem = get_zelda_memory()
        in_control = mem.player.in_control
        return False if in_control else self.active


# TODO: Refactor (currently only used in very specific cases)
class Evoland1Memory:

    # TODO
    # Zelda player health for roaming battle (hearts)
    _PLAYER_HP_ZELDA_PTR = [0x7FC, 0x8, 0x30, 0x7C, 0x0] # each heart is 16 "health"
    _GLI_PTR = [0x7FC, 0x8, 0x30, 0x84, 0x0] # Money

    _MAP_ID_PTR = [0x7FC, 0x8, 0x30, 0xC8, 0x0, 0x4]

    # TODO: Verify these are useful/correct (got from mem searching)
    _PLAYER_MAX_HP_ZELDA_PTR = [0x7FC, 0x8, 0x30, 0x80, 0x0]
    _PLAYER_HP_OVERWORLD_PTR = [0x7FC, 0x8, 0x30, 0x3C, 0x0]
    #_KAERIS_HP_OVERWORLD_PTR = [0x7FC, 0x8, 0x30, 0x48] # TODO: Verify, looks wrong
    _LEVEL_ARRAY_SIZE_PTR = [0x7FC, 0x8, 0x30, 0x78, 0x0, 0x4] # Should be 2
    _PLAYER_LVL_PTR = [0x7FC, 0x8, 0x30, 0x78, 0x0, 0x8, 0x10, 0x8, 0x0] # int
    _PLAYER_EXP_PTR = [0x7FC, 0x8, 0x30, 0x78, 0x0, 0x8, 0x10, 0x8, 0x4] # int
    _KAERIS_LVL_PTR = [0x7FC, 0x8, 0x30, 0x78, 0x0, 0x8, 0x14, 0x8, 0x0] # int
    _KAERIS_EXP_PTR = [0x7FC, 0x8, 0x30, 0x78, 0x0, 0x8, 0x14, 0x8, 0x4] # int

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
    @property
    def player_hearts(self) -> float:
        player_hearts_ptr = self.process.get_pointer(
            self.base_addr + _LIBHL_OFFSET, offsets=self._PLAYER_HP_ZELDA_PTR
        )
        return self.process.read_double(player_hearts_ptr)

    @property
    def gli(self) -> int:
        return self.process.read_u32(self.gli_ptr)

    @property
    def lvl(self) -> int:
        # TODO: Implement player level
        return 1

    @property
    def map_id(self) -> MapID:
        return MapID(self.process.read_u32(self.map_id_ptr))

    @property
    def player_hp_overworld(self) -> int:
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
    #TODO: _ATTACK_TIMER_PTR = [0xC8]  # double. unclear purpose, resets when swinging sword
    _ENCOUNTER_TIMER_PTR = [0xD0]  # double. Steps to encounter
    _IN_CONTROL_PTR = [0xA4]

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
        self.in_control_ptr = self.process.get_pointer(
            self.entity_ptr, offsets=self._IN_CONTROL_PTR
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

    @property
    def kind(self) -> EKind:
        kind_val = self.process.read_u32(self.ent_kind_ptr)
        try:
            return GameEntity2D.EKind(kind_val)
        except ValueError:
            logger.error(f"Unknown GameEntity2D EKind: {kind_val}")
            return GameEntity2D.EKind.UNKNOWN

    @property
    def pos(self) -> Vec2:
        return Vec2(
            self.process.read_double(self.x_ptr),
            self.process.read_double(self.y_ptr),
        )

    @property
    def tile_pos(self) -> Tuple[int, int]:
        return [
            self.process.read_u32(self.x_tile_ptr),
            self.process.read_u32(self.y_tile_ptr),
        ]

    @property
    def speed(self) -> float:
        return self.process.read_double(self.speed_ptr)

    @property
    def target(self) -> Optional[Vec2]:
        target_ptr = self.process.read_u32(self.target_ptr)
        if target_ptr != 0:
            return Vec2(
                x=self.process.read_double(target_ptr + self._TARGET_X_OFFSET),
                y=self.process.read_double(target_ptr + self._TARGET_Y_OFFSET),
            )
        return None

    @property
    def timer(self) -> float:
        return self.process.read_double(self.timer_ptr)

    # 0=left,1=right,2=up,3=down. Doesn't do diagonal facings.
    @property
    def facing(self) -> Facing:
        return self.process.read_u32(self.facing_ptr)

    @property
    def is_attacking(self) -> bool:
        attacking = self.process.read_u8(self.attack_ptr)
        return attacking & 0x10  # Bit5 denotes attacking

    @property
    def rotation(self) -> float:
        return self.process.read_double(self.rotation_ptr)

    @property
    def hp(self) -> int:
        return self.process.read_u32(self.hp_ptr)

    @property
    def not_in_control(self) -> bool:
        return self.process.read_u8(self.in_control_ptr) == 1

    @property
    def in_control(self) -> bool:
        return self.process.read_u8(self.in_control_ptr) == 0

    @property
    def encounter_timer(self) -> float:
        return self.process.read_double(self.encounter_timer_ptr)

    def __repr__(self) -> str:
        kind = self.kind
        hp_str = f", hp: {self.hp}" if kind == self.EKind.ENEMY else ""
        return f"Ent({kind.name}, {self.pos}{hp_str})"


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

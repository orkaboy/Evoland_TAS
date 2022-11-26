# Libraries and Core Files
import logging
import math
from enum import Flag, IntEnum, auto
from typing import List, NamedTuple, Tuple

import memory.core
from memory.core import LocProcess

logger = logging.getLogger(__name__)

# TODO: Move these to a math library instead

class Vec2(NamedTuple):
    x: float
    y: float

    def __add__(self, other):
        return Vec2(self.x + other.x, self.y + other.y)
    def __sub__(self, other):
        return Vec2(self.x - other.x, self.y - other.y)

    def __repr__(self) -> str:
        return f"Vec2({self.x:0.3f}, {self.y:0.3f})"


def dist(a: Vec2, b: Vec2) -> float:
    dx = b.x - a.x
    dy = b.y - a.y
    return math.sqrt(dx * dx + dy * dy)


def is_close(a: Vec2, b: Vec2, precision: float) -> bool:
    return dist(a, b) <= precision

class Box2(NamedTuple):
    pos: Vec2
    w: float
    h: float

    def __repr__(self) -> str:
        return f"Box[{self.pos}, w: {self.w}, h: {self.h}]"

    def contains(self, pos: Vec2):
        left, top = self.pos.x, self.pos.y
        right, bottom = self.pos.x + self.w, self.pos.y + self.h
        return pos.x >= left and pos.x <= right and pos.y >= top and pos.y <= bottom

    # Top-left, Top-right, Bot-left, Bot-right
    def tl(self) -> Vec2:
        return self.pos
    def tr(self) -> Vec2:
        return Vec2(self.pos.x + self.w, self.pos.y)
    def bl(self) -> Vec2:
        return Vec2(self.pos.x, self.pos.y + self.h)
    def br(self) -> Vec2:
        return Vec2(self.pos.x + self.w, self.pos.y + self.h)

# expand the box by a set amount in all directions
def grow_box(box: Box2, amount: int = 1) -> Box2:
    return Box2(
        pos=Vec2(box.pos.x - amount, box.pos.y - amount),
        w=box.w + 2*amount,
        h=box.h + 2*amount
    )

class Facing(IntEnum):
    LEFT = 0
    RIGHT = 1
    UP = 2
    DOWN = 3

def facing_str(facing: Facing) -> str:
    match facing:
        case Facing.LEFT:
            return "left"
        case Facing.RIGHT:
            return "right"
        case Facing.UP:
            return "up"
        case Facing.DOWN:
            return "down"

def facing_ch(facing: Facing) -> str:
    match facing:
        case Facing.LEFT:
            return "<"
        case Facing.RIGHT:
            return ">"
        case Facing.UP:
            return "^"
        case Facing.DOWN:
            return "v"


# Representation of game features picked up from chests
class GameFeatures(Flag):
    MoveSmooth = auto()


_LIBHL_OFFSET = 0x0004914C


# TODO: Refactor (currently not used)
class Evoland1Memory:

    # Zelda player health for roaming battle (hearts)
    _PLAYER_HP_ZELDA_PTR = [0x7FC, 0x8, 0x30, 0x7C, 0x0]
    # TODO: Verify these are useful/correct (got from mem searching)
    _GLI_PTR = [0x7FC, 0x8, 0x30, 0x84, 0x0]  # TODO: Verify, Money
    _PLAYER_MAX_HP_ZELDA_PTR = [0x7FC, 0x8, 0x30, 0x80, 0x0] # TODO: Verify
    _PLAYER_HP_OVERWORLD_PTR = [0x7FC, 0x8, 0x30, 0x3C, 0x0]
    _KAERIS_HP_OVERWORLD_PTR = [0x7FC, 0x8, 0x30, 0x48]

    # Only valid in atb battle
    _PLAYER_ATB_CUR_HP_PTR = [0x860, 0x0, 0x244, 0x2C, 0x8, 0x10, 0xF4]
    # Only valid when menu is open
    _PLAYER_ATB_MENU_CURSOR_PTR = [0x860, 0x0, 0x244, 0x48, 0x8C]

    def __init__(self):
        mem_handle = memory.core.handle()
        self.process = mem_handle.process
        self.base_addr = mem_handle.base_addr
        logger.debug(f"Base address: {hex(self.base_addr)}")
        self.setup_pointers()

    def setup_pointers(self):
        self.player_hp_overworld_ptr = self.process.get_pointer(
            self.base_addr + _LIBHL_OFFSET, offsets=self._PLAYER_HP_OVERWORLD_PTR
        )
        self.gli_ptr = self.process.get_pointer(
            self.base_addr + _LIBHL_OFFSET, offsets=self._GLI_PTR
        )
        logger.debug(
            f"Address to player_hp_overworld: {hex(self.player_hp_overworld_ptr)}"
        )
        logger.debug(f"Address to gli: {hex(self.gli_ptr)}")

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

    def in_combat(self) -> bool:
        # TODO: This is a dumb idea, but should work?
        # TODO: It doesn't. The memory address remains in memory after the first battle ends.
        try:
            _ = self.get_atb_player_hp()
            return True
        except ReferenceError:
            return False

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
    _X_PTR = [0x8]  # double
    _Y_PTR = [0x10]  # double
    _X_TILE_PTR = [0x14]  # int
    _Y_TILE_PTR = [0x18]  # int
    _TIMER_PTR = [0x48]  # double (timeout in s)
    _FACING_PTR = [0x58]  # int
    _ATTACK_PTR = [0x5C]  # byte, bit 5
    _ROTATION_PTR = [0x90]  # double (left = 0.0, up = 1.57, right = 3.14, down = -1.57)
    _HP_PTR = [0x100]  # int, for enemies such as knights
    # This seems to be set on picking up stuff/opening inventory/opening menu, may be misnamed. Invincibility flag?
    _INV_OPEN_PTR = [0xA4]

    def __init__(self, process: LocProcess, entity_ptr: int):
        self.process = process
        self.entity_ptr = entity_ptr
        self.setup_pointers()

    def setup_pointers(self):
        self.x_ptr = self.process.get_pointer(self.entity_ptr, offsets=self._X_PTR)
        self.y_ptr = self.process.get_pointer(self.entity_ptr, offsets=self._Y_PTR)
        self.x_tile_ptr = self.process.get_pointer(
            self.entity_ptr, offsets=self._X_TILE_PTR
        )
        self.y_tile_ptr = self.process.get_pointer(
            self.entity_ptr, offsets=self._Y_TILE_PTR
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

    def __repr__(self) -> str:
        return f"Ent({self.get_pos()}, hp: {self.get_hp()})"


class ZeldaMemory:

    # Zelda-related things:
    _ZELDA_PTR = [0x7C8, 0x8, 0x3C]
    _PLAYER_PTR = [0x30]
    _ENEMY_ARR_PTR = [0x48, 0x8]

    _ENEMY_ARR_SIZE_PTR = [0x48, 0x8, 0x8]  # TODO: Need to verify this one
    _ENEMY_PTR_SIZE = 4
    _ENEMY_BASE_ADDR = 0x10  # TODO: Need to verify this one

    def __init__(self):
        mem_handle = memory.core.handle()
        self.process = mem_handle.process
        self.base_addr = mem_handle.base_addr
        # logger.debug(f"Zelda base address: {hex(self.base_addr)}")
        self.base_offset = self.process.get_pointer(
            self.base_addr + _LIBHL_OFFSET, offsets=self._ZELDA_PTR
        )

        self._init_player()
        self._init_enemies()

    def _init_player(self):
        player_ptr = self.process.get_pointer(self.base_offset, self._PLAYER_PTR)
        self.player = GameEntity2D(self.process, player_ptr)

    def _init_enemies(self):
        self.enemies: List[GameEntity2D] = []
        enemy_arr_size_ptr = self.process.get_pointer(
            self.base_offset, offsets=self._ENEMY_ARR_SIZE_PTR
        )
        enemy_arr_size = self.process.read_u32(enemy_arr_size_ptr)
        enemy_arr_offset = self.process.get_pointer(
            self.base_offset, offsets=self._ENEMY_ARR_PTR
        )
        for i in range(enemy_arr_size):
            # Set enemy offsets
            enemy_offset = self._ENEMY_BASE_ADDR + i * self._ENEMY_PTR_SIZE
            enemy_ptr = self.process.get_pointer(enemy_arr_offset, [enemy_offset])
            self.enemies.append(GameEntity2D(self.process, enemy_ptr))


_zelda_mem = None


def load_zelda_memory() -> None:
    global _zelda_mem
    _zelda_mem = ZeldaMemory()


def get_zelda_memory() -> ZeldaMemory:
    return _zelda_mem

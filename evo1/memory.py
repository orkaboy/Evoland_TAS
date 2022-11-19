# Libraries and Core Files
import logging
from enum import Flag, IntEnum, auto
from typing import NamedTuple, Tuple

import memory.core

logger = logging.getLogger(__name__)


class Vec2(NamedTuple):
    x: float
    y: float


class Facing(IntEnum):
    LEFT = 0
    RIGHT = 1
    UP = 2
    DOWN = 3


# Representation of game features picked up from chests
class GameFeatures(Flag):
    MoveSmooth = auto()


class Evoland1Memory:

    _LIBHL_OFFSET = 0x0004914C

    # Player position on map
    _PLAYER_X_PTR = [0x7C8, 0x8, 0x3C, 0x30, 0x8]
    _PLAYER_Y_PTR = [0x7C8, 0x8, 0x3C, 0x30, 0x10]

    # Same as pos, but only integer part (not needed?)
    _PLAYER_X_TILE_PTR = [0x7C8, 0x8, 0x3C, 0x30, 0x14]
    _PLAYER_Y_TILE_PTR = [0x7C8, 0x8, 0x3C, 0x30, 0x18]

    # 0=left,1=right,2=up,3=down. Doesn't do diagonal facings.
    _PLAYER_FACING_PTR = [0x7C8, 0x8, 0x3C, 0x30, 0x58]

    # This seems to be set on picking up stuff/opening inventory/opening menu, may be misnamed. Invincibility flag?
    _PLAYER_INV_OPEN_PTR = [0x7C8, 0x8, 0x3C, 0x30, 0xA4]

    # Only 1 when moving AND has sub-tile movement
    _PLAYER_IS_MOVING_PTR = [0x7C8, 0x8, 0x3C, 0x30, 0xA5]

    # Overworld player health for ATB battle. Only updates outside battle!
    _PLAYER_HP_OVERWORLD_PTR = [0xA6C, 0x0, 0x90, 0x3C, 0x0]

    # Zelda player health for roaming battle (hearts)
    _PLAYER_HP_ZELDA_PTR = [0x7FC, 0x8, 0x30, 0x7C, 0x0]

    # Only valid in atb battle
    _PLAYER_APB_CUR_HP_PTR = [0x860, 0x0, 0x244, 0x2C, 0x8, 0x10, 0xF4]
    # Only valid when menu is open
    _PLAYER_APB_MENU_CURSOR_PTR = [0x860, 0x0, 0x244, 0x48, 0x8C]

    # Money
    _GLI_PTR = [0xA6C, 0x0, 0x90, 0x18, 0x10]

    def __init__(self):
        mem_handle = memory.core.handle()
        self.process = mem_handle.process
        self.base_addr = mem_handle.base_addr
        logger.debug(f"Base address: {hex(self.base_addr)}")
        self.setup_pointers()

    def setup_pointers(self):
        self.player_x_ptr = self.process.get_pointer(
            self.base_addr + self._LIBHL_OFFSET, offsets=self._PLAYER_X_PTR
        )
        self.player_y_ptr = self.process.get_pointer(
            self.base_addr + self._LIBHL_OFFSET, offsets=self._PLAYER_Y_PTR
        )
        self.player_x_tile_ptr = self.process.get_pointer(
            self.base_addr + self._LIBHL_OFFSET, offsets=self._PLAYER_X_TILE_PTR
        )
        self.player_y_tile_ptr = self.process.get_pointer(
            self.base_addr + self._LIBHL_OFFSET, offsets=self._PLAYER_Y_TILE_PTR
        )
        self.player_facing_ptr = self.process.get_pointer(
            self.base_addr + self._LIBHL_OFFSET, offsets=self._PLAYER_FACING_PTR
        )
        self.player_inv_open_ptr = self.process.get_pointer(
            self.base_addr + self._LIBHL_OFFSET, offsets=self._PLAYER_INV_OPEN_PTR
        )
        self.player_is_moving_ptr = self.process.get_pointer(
            self.base_addr + self._LIBHL_OFFSET, offsets=self._PLAYER_IS_MOVING_PTR
        )
        self.player_hp_overworld_ptr = self.process.get_pointer(
            self.base_addr + self._LIBHL_OFFSET, offsets=self._PLAYER_HP_OVERWORLD_PTR
        )
        self.gli_ptr = self.process.get_pointer(
            self.base_addr + self._LIBHL_OFFSET, offsets=self._GLI_PTR
        )
        logger.debug(f"Address to player_x: {hex(self.player_x_ptr)}")
        logger.debug(f"Address to player_y: {hex(self.player_y_ptr)}")
        logger.debug(f"Address to player_facing: {hex(self.player_facing_ptr)}")
        logger.debug(f"Address to player_inv_open: {hex(self.player_inv_open_ptr)}")
        logger.debug(f"Address to player_is_moving: {hex(self.player_is_moving_ptr)}")
        logger.debug(
            f"Address to player_hp_overworld: {hex(self.player_hp_overworld_ptr)}"
        )
        logger.debug(f"Address to gli: {hex(self.gli_ptr)}")

    def get_player_pos(self) -> Vec2:
        return Vec2(
            self.process.read_double(self.player_x_ptr),
            self.process.read_double(self.player_y_ptr),
        )

    def get_player_tile_pos(self) -> Tuple[int, int]:
        return [
            self.process.read_double(self.player_x_tile_ptr),
            self.process.read_double(self.player_y_tile_ptr),
        ]

    # 0=left,1=right,2=up,3=down. Doesn't do diagonal facings.
    def get_player_facing(self) -> Facing:
        return self.process.read_u32(self.player_facing_ptr)

    def get_player_facing_str(self, facing: Facing) -> str:
        match facing:
            case Facing.LEFT:
                return "left"
            case Facing.RIGHT:
                return "right"
            case Facing.UP:
                return "up"
            case Facing.DOWN:
                return "down"
            case other:
                return "err"

    # Only valid in zelda map
    def get_player_hearts(self) -> float:
        player_hearts_ptr = self.process.get_pointer(
            self.base_addr + self._LIBHL_OFFSET, offsets=self._PLAYER_HP_ZELDA_PTR
        )
        return self.process.read_double(player_hearts_ptr)

    def get_gli(self) -> int:
        return self.process.read_u32(self.gli_ptr)

    # Only valid in battle!
    def get_atb_player_hp(self) -> int:
        atb_player_hp_ptr = self.process.get_pointer(
            self.base_addr + self._LIBHL_OFFSET, offsets=self._PLAYER_APB_CUR_HP_PTR
        )
        return self.process.read_u32(atb_player_hp_ptr)

    def get_atb_menu_cursor(self) -> int:
        atb_menu_cursor_ptr = self.process.get_pointer(
            self.base_addr + self._LIBHL_OFFSET,
            offsets=self._PLAYER_APB_MENU_CURSOR_PTR,
        )
        return self.process.read_u32(atb_menu_cursor_ptr)

    # TODO: Rename?
    def get_inv_open(self) -> bool:
        return self.process.read_u8(self.player_inv_open_ptr) == 1

    # TODO: Rename?
    def get_player_is_moving(self) -> bool:
        return self.process.read_u8(self.player_is_moving_ptr) == 1

    def get_player_hp_overworld(self) -> int:
        return self.process.read_u32(self.player_hp_overworld_ptr)


_mem = None


def load_memory() -> None:
    global _mem
    _mem = Evoland1Memory()


def get_memory() -> Evoland1Memory:
    return _mem

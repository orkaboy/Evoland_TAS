# Libraries and Core Files
import logging

import memory.core

logger = logging.getLogger(__name__)


class Evoland1Memory:

    _LIBHL_OFFSET = 0x0004914C

    # Player position on map
    _PLAYER_X_PTR = [0x7C8, 0x8, 0x3C, 0x30, 0x8]
    _PLAYER_Y_PTR = [0x7C8, 0x8, 0x3C, 0x30, 0x10]

    # Same as pos, but only integer part
    _PLAYER_X_TILE_PTR = [0x7C8, 0x8, 0x3C, 0x30, 0x14]
    _PLAYER_Y_TILE_PTR = [0x7C8, 0x8, 0x3C, 0x30, 0x18]

    # Drop? Doesn't seem that useful
    _PLAYER_X_FACING_PTR = [0x7C8, 0x8, 0x3C, 0x30, 0x50]
    _PLAYER_Y_FACING_PTR = [0x7C8, 0x8, 0x3C, 0x30, 0x54]

    # 0=left,1=right,2=up,3=down. Doesn't do diagonal facings.
    _PLAYER_FACING_PTR = [0x7C8, 0x8, 0x3C, 0x30, 0x58]

    # This seems to be set on picking up stuff/opening inventory/opening menu, may be misnamed. Invincibility flag?
    _PLAYER_INV_OPEN_PTR = [0x7C8, 0x8, 0x3C, 0x30, 0xA4]

    # Only 1 when moving AND has sub-tile movement
    _PLAYER_IS_MOVING_PTR = [0x7C8, 0x8, 0x3C, 0x30, 0xA5]

    # Overworld player health for ATB battle. Only updates outside battle!
    _PLAYER_HP_OVERWORLD_PTR = [0xA6C, 0x0, 0x90, 0x3C, 0x0]

    # TODO: Doesn't seem to be reliable between boots of the game (and requires THREADSTACK0)
    # The value is reallocated in every battle
    # The value is retained [somewhere] between battles, not sure how it's stored in memory
    # Might only be updated after battle
    _PLAYER_APB_CUR_HP_PTR = [0x1C, 0x1C, 0x88, 0x2C, 0x8, 0x10, 0xF4]

    def __init__(self):
        mem = memory.core.handle()
        self.process = mem.process
        self.base_addr = mem.base_addr
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
        self.player_x_facing_ptr = self.process.get_pointer(
            self.base_addr + self._LIBHL_OFFSET, offsets=self._PLAYER_X_FACING_PTR
        )
        self.player_y_facing_ptr = self.process.get_pointer(
            self.base_addr + self._LIBHL_OFFSET, offsets=self._PLAYER_Y_FACING_PTR
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
        logger.debug(f"Address to player_x: {hex(self.player_x_ptr)}")
        logger.debug(f"Address to player_y: {hex(self.player_y_ptr)}")
        logger.debug(f"Address to player_x_facing: {hex(self.player_x_facing_ptr)}")
        logger.debug(f"Address to player_y_facing: {hex(self.player_y_facing_ptr)}")
        logger.debug(f"Address to player_facing: {hex(self.player_facing_ptr)}")
        logger.debug(f"Address to player_inv_open: {hex(self.player_inv_open_ptr)}")
        logger.debug(f"Address to player_is_moving: {hex(self.player_is_moving_ptr)}")
        logger.debug(
            f"Address to player_hp_overworld: {hex(self.player_hp_overworld_ptr)}"
        )

    def get_player_pos(self) -> list[float]:
        return [
            self.process.read_double(self.player_x_ptr),
            self.process.read_double(self.player_y_ptr),
        ]

    def get_player_tile_pos(self) -> list[int]:
        return [
            self.process.read_double(self.player_x_tile_ptr),
            self.process.read_double(self.player_y_tile_ptr),
        ]

    # TODO: Remove?
    def get_player_facing2(self) -> list[int]:
        return [
            self.process.read_s32(self.player_x_facing_ptr),
            self.process.read_s32(self.player_y_facing_ptr),
        ]

    # 0=left,1=right,2=up,3=down. Doesn't do diagonal facings.
    def get_player_facing(self) -> int:
        return self.process.read_u32(self.player_facing_ptr)

    def get_player_facing_str(self, facing: int) -> str:
        match facing:
            case 0:
                return "left"
            case 1:
                return "right"
            case 2:
                return "up"
            case 3:
                return "down"
            case other:
                return "err"

    # TODO: Rename?
    def get_inv_open(self) -> bool:
        return self.process.read_u8(self.player_inv_open_ptr) == 1

    # TODO: Rename?
    def get_player_is_moving(self) -> bool:
        return self.process.read_u8(self.player_is_moving_ptr) == 1

    def get_player_hp_overworld(self) -> int:
        return self.process.read_u32(self.player_hp_overworld_ptr)

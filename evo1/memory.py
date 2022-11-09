# Libraries and Core Files
import logging

import memory.core

logger = logging.getLogger(__name__)


class Evoland1Memory:

    _LIBHL_OFFSET = 0x0004914C
    _PLAYER_X_PTR = [0x7C8, 0x8, 0x3C, 0x30, 0x8]
    _PLAYER_Y_PTR = [0x7C8, 0x8, 0x3C, 0x30, 0x10]
    _PLAYER_X_FACING_PTR = [0x7C8, 0x8, 0x3C, 0x30, 0x50]
    _PLAYER_Y_FACING_PTR = [0x7C8, 0x8, 0x3C, 0x30, 0x54]

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
        self.player_x_facing_ptr = self.process.get_pointer(
            self.base_addr + self._LIBHL_OFFSET, offsets=self._PLAYER_X_FACING_PTR
        )
        self.player_y_facing_ptr = self.process.get_pointer(
            self.base_addr + self._LIBHL_OFFSET, offsets=self._PLAYER_Y_FACING_PTR
        )
        logger.debug(f"Address to player_x: {hex(self.player_x_ptr)}")
        logger.debug(f"Address to player_y: {hex(self.player_y_ptr)}")
        logger.debug(f"Address to player_x_facing: {hex(self.player_x_facing_ptr)}")
        logger.debug(f"Address to player_y_facing: {hex(self.player_y_facing_ptr)}")

    def get_player_pos(self) -> list[float]:
        return [
            self.process.read_double(self.player_x_ptr),
            self.process.read_double(self.player_y_ptr),
        ]

    def get_player_facing(self) -> list[int]:
        return [
            self.process.read_s32(self.player_x_facing_ptr),
            self.process.read_s32(self.player_y_facing_ptr),
        ]

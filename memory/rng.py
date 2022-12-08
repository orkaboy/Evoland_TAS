# Libraries and Core Files
import logging
from typing import List

import memory.core

logger = logging.getLogger(__name__)

_LIBHL_OFFSET = 0x0004914C


class EvolandRNG:
    # Evoland (or rather; HashLink) RNG works by generating a batch of 25 random values
    # A counter (the cursor) points to the current value. When the game extracts a
    # pseudo rng value, it increments the counter by 1. When the counter overflows
    # (reaches 25), a new batch is generated.
    # Each random value is a 32 bit number, that the game then interprets.

    # Code: https://github.com/HaxeFoundation/hashlink/blob/master/src/std/random.c

    RNG_VALS = 25
    RNG_MAX = 7
    RNG_MAG01 = [0x0, 0x8EBFD028]

    _RNG_VALUE_SIZE = 4  # 4 bytes
    _RNG_BASE_PTR = [0x7F4, 0x0, 0x18, 0x0]
    _RNG_CURSOR_PTR = [0x7F4, 0x0, 0x18, 0x64]

    def __init__(self) -> None:
        mem_handle = memory.core.handle()
        self.process = mem_handle.process
        self.base_addr = mem_handle.base_addr
        self.setup_pointers()

    def setup_pointers(self):
        self.rng_cursor_ptr = self.process.get_pointer(
            self.base_addr + _LIBHL_OFFSET, offsets=self._RNG_CURSOR_PTR
        )
        self.rng_base_ptr = self.process.get_pointer(
            self.base_addr + _LIBHL_OFFSET, offsets=self._RNG_BASE_PTR
        )

    class RNGStruct:
        def __init__(self, cursor: int, values: List[int]) -> None:
            self.cursor = cursor
            self.values = values

        def advance_rng(self, steps: int = 1) -> int:
            for _ in range(steps):
                pos = self.cursor
                self.cursor += 1
                if pos >= EvolandRNG.RNG_VALS:
                    self._calc_next_rng()
                    self.cursor = 1
                    pos = 0
            return pos

        def _calc_next_rng(self):
            for kk in range(EvolandRNG.RNG_VALS - EvolandRNG.RNG_MAX):
                self.values[kk] = (
                    self.values[kk + EvolandRNG.RNG_MAX]
                    ^ (self.values[kk] >> 1)
                    ^ EvolandRNG.RNG_MAG01[self.values[kk] % 2]
                )
            for kk in range(
                EvolandRNG.RNG_VALS - EvolandRNG.RNG_MAX, EvolandRNG.RNG_VALS
            ):
                self.values[kk] = (
                    self.values[kk + (EvolandRNG.RNG_MAX - EvolandRNG.RNG_VALS)]
                    ^ (self.values[kk] >> 1)
                    ^ EvolandRNG.RNG_MAG01[self.values[kk] % 2]
                )

        # consumes one rng value and returns an int
        def rand_int(self) -> int:
            pos = self.advance_rng()
            ret = self.values[pos]
            ret ^= (ret << 7) & 0x2B5B2500
            ret ^= (ret << 15) & 0xDB8B0000
            ret ^= ret >> 16
            return ret

        # consume three rng values and returns a float
        def rand_float(self) -> float:
            big = 4294967296.0
            return (
                (self.rand_int() / big + self.rand_int()) / big + self.rand_int()
            ) / big

    # Get the current RNG values
    def get_rng(self) -> RNGStruct:
        cursor = self.process.read_u32(self.rng_cursor_ptr)
        values = [
            self.process.read_u32(self.rng_base_ptr + i * self._RNG_VALUE_SIZE)
            for i in range(self.RNG_VALS)
        ]
        return EvolandRNG.RNGStruct(cursor=cursor, values=values)

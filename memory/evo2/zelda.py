# Libraries and Core Files
import logging

from memory.core import LIBHL_OFFSET
from memory.evo2.entity import EKind, entEntity, entZHero, entZMob
from memory.zelda_base import ZeldaMemory

logger = logging.getLogger(__name__)


class Evo2ZeldaMemory(ZeldaMemory):
    # Zelda-related things:
    _ZELDA_PTR = [0x37C, 0x0, 0x58]
    _PLAYER_PTR = [0x30]

    _FIGHTERS_ARR_PTR = [0x44, 0x8]
    _FIGHTERS_ARR_SIZE_PTR = [0x44, 0x4]
    _FIGHTERS_PTR_SIZE = 4
    _FIGHTERS_BASE_ADDR = 0x10

    def __init__(self):
        super().__init__()
        self.base_offset = self.process.get_pointer(
            self.base_addr + LIBHL_OFFSET, offsets=self._ZELDA_PTR
        )

        self._init_player()
        # TODO: Maybe need to use a superclass here
        self.actors: list[entZMob] = []
        self._init_fighters()

    def _init_player(self):
        player_ptr = self.process.get_pointer(self.base_offset, self._PLAYER_PTR)
        self.player = entZHero(self.process, player_ptr)

    def _init_fighters(self):
        fighter_arr_size_ptr = self.process.get_pointer(
            self.base_offset, offsets=self._FIGHTERS_ARR_SIZE_PTR
        )
        fighter_arr_size = self.process.read_u32(fighter_arr_size_ptr)
        fighter_arr_offset = self.process.get_pointer(
            self.base_offset, offsets=self._FIGHTERS_ARR_PTR
        )
        for i in range(fighter_arr_size):
            # Set enemy offsets
            fighter_offset = self._FIGHTERS_BASE_ADDR + i * self._FIGHTERS_PTR_SIZE
            fighter_ptr = self.process.get_pointer(fighter_arr_offset, [fighter_offset])

            fighter_kind = entEntity(self.process, fighter_ptr).kind
            match fighter_kind:
                case EKind.MOB:
                    self.actors.append(entZMob(self.process, fighter_ptr))
                # TODO: Parse more kinds of entities
                case _:
                    pass


_zelda_mem = None


def load_zelda_memory() -> None:
    global _zelda_mem
    _zelda_mem = Evo2ZeldaMemory()


def get_zelda_memory() -> Evo2ZeldaMemory:
    return _zelda_mem

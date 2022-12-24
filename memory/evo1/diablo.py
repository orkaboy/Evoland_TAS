# Libraries and Core Files
import logging

from memory.core import LocProcess
from memory.evo1.zelda import Evo1GameEntity2D, Evo1ZeldaMemory

logger = logging.getLogger(__name__)


# Only valid when instantiated, on the screen that they live
class Evo1DiabloEntity(Evo1GameEntity2D):
    """Memory representation of HackMonster (Sarudnahk section)."""

    _MKIND_PTR = [0xA4, 0x4]  # MKind enum (overrides base class)
    _HP_PTR = [0x108]  # double (overrides base class)

    def __init__(self, process: LocProcess, entity_ptr: int):
        super().__init__(process, entity_ptr)
        # Overrides
        self.mkind_ptr = self.process.get_pointer(entity_ptr, offsets=self._MKIND_PTR)
        self.hp_ptr = self.process.get_pointer(entity_ptr, offsets=self._HP_PTR)

    # Override (double instead of int)
    @property
    def hp(self) -> float:
        return self.process.read_double(self.hp_ptr)


class Evo1DiabloMemory(Evo1ZeldaMemory):
    # _DIABLO_HERO_SELECT_PTR = [0x7FC, 0x8, 0x30, 0xA4, 0x0] # TODO: Verify

    # Override to get correct class
    def _alloc_monster(self, actor_ptr) -> Evo1DiabloEntity:
        return Evo1DiabloEntity(self.process, actor_ptr)


_diablo_mem = None


def load_diablo_memory() -> None:
    global _diablo_mem
    _diablo_mem = Evo1DiabloMemory()


def get_diablo_memory() -> Evo1DiabloMemory:
    return _diablo_mem

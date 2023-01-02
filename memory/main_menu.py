# Libraries and Core Files
import logging

from memory.core import LIBHL_OFFSET, mem_handle

logger = logging.getLogger(__name__)


# TODO: Refactor (currently only used in very specific cases)
class MainMenuMemory:
    # Only valid in main menu
    _CHOICE_PTR = [0x648, 0x8, 0x1C, 0xC, 0x44]
    _MENU_COUNT_PTR = [0x648, 0x8, 0x1C, 0xC, 0x4C]

    def __init__(self):
        mem = mem_handle()
        self.process = mem.process
        self.base_addr = mem.base_addr

    @property
    def choice(self) -> int:
        ptr = self.process.get_pointer(
            self.base_addr + LIBHL_OFFSET, offsets=self._CHOICE_PTR
        )
        return self.process.read_u32(ptr)

    @property
    def menu_count(self) -> int:
        """Can't quite be used as a menu ID, since some menues have the same value."""
        ptr = self.process.get_pointer(
            self.base_addr + LIBHL_OFFSET, offsets=self._MENU_COUNT_PTR
        )
        return self.process.read_u32(ptr)


_mem = None


def load_menu_memory() -> None:
    global _mem
    _mem = MainMenuMemory()


def get_menu_memory() -> MainMenuMemory:
    return _mem

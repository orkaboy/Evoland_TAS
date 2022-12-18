# Libraries and Core Files
import logging

from memory.core import LIBHL_OFFSET, mem_handle

logger = logging.getLogger(__name__)


# TODO: Refactor (currently only used in very specific cases)
class MainMenuMemory:

    _CURSOR_PTR = [0x7F8, 0x0, 0x24, 0x444]

    def __init__(self):
        mem = mem_handle()
        self.process = mem.process
        self.base_addr = mem.base_addr

        self.cursor_ptr = self.process.get_pointer(
            self.base_addr + LIBHL_OFFSET, offsets=self._CURSOR_PTR
        )

    # Only valid in main menu
    @property
    def cursor(self) -> int:
        return self.process.read_u32(self.cursor_ptr)


_mem = None


def load_menu_memory() -> None:
    global _mem
    _mem = MainMenuMemory()


def get_menu_memory() -> MainMenuMemory:
    return _mem

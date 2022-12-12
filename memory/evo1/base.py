# Libraries and Core Files
from memory.core import LIBHL_OFFSET, mem_handle
from memory.evo1.map_id import MapID


# TODO: Refactor (currently only used in very specific cases)
class Evoland1Memory:

    # TODO
    # Zelda player health for roaming battle (hearts)
    _PLAYER_HP_ZELDA_PTR = [0x7FC, 0x8, 0x30, 0x7C, 0x0]  # each heart is 16 "health"
    _GLI_PTR = [0x7FC, 0x8, 0x30, 0x84, 0x0]  # Money

    _MAP_ID_PTR = [0x7FC, 0x8, 0x30, 0xC8, 0x0, 0x4]

    # TODO: Verify these are useful/correct (got from mem searching)
    _PLAYER_MAX_HP_ZELDA_PTR = [0x7FC, 0x8, 0x30, 0x80, 0x0]
    _PLAYER_HP_OVERWORLD_PTR = [0x7FC, 0x8, 0x30, 0x3C, 0x0]
    # _KAERIS_HP_OVERWORLD_PTR = [0x7FC, 0x8, 0x30, 0x48] # TODO: Verify, looks wrong
    _LEVEL_ARRAY_SIZE_PTR = [0x7FC, 0x8, 0x30, 0x78, 0x0, 0x4]  # Should be 2
    _PLAYER_LVL_PTR = [0x7FC, 0x8, 0x30, 0x78, 0x0, 0x8, 0x10, 0x8, 0x0]  # int
    _PLAYER_EXP_PTR = [0x7FC, 0x8, 0x30, 0x78, 0x0, 0x8, 0x10, 0x8, 0x4]  # int
    _KAERIS_LVL_PTR = [0x7FC, 0x8, 0x30, 0x78, 0x0, 0x8, 0x14, 0x8, 0x0]  # int
    _KAERIS_EXP_PTR = [0x7FC, 0x8, 0x30, 0x78, 0x0, 0x8, 0x14, 0x8, 0x4]  # int

    def __init__(self):
        mem = mem_handle()
        self.process = mem.process
        self.base_addr = mem.base_addr
        self.setup_pointers()

    def setup_pointers(self):
        self.player_hp_overworld_ptr = self.process.get_pointer(
            self.base_addr + LIBHL_OFFSET, offsets=self._PLAYER_HP_OVERWORLD_PTR
        )
        self.gli_ptr = self.process.get_pointer(
            self.base_addr + LIBHL_OFFSET, offsets=self._GLI_PTR
        )
        self.map_id_ptr = self.process.get_pointer(
            self.base_addr + LIBHL_OFFSET, self._MAP_ID_PTR
        )
        self.lvl_ptr = self.process.get_pointer(
            self.base_addr + LIBHL_OFFSET, self._PLAYER_LVL_PTR
        )

    # Only valid in zelda map
    @property
    def player_hearts(self) -> float:
        player_hearts_ptr = self.process.get_pointer(
            self.base_addr + LIBHL_OFFSET, offsets=self._PLAYER_HP_ZELDA_PTR
        )
        return self.process.read_double(player_hearts_ptr)

    @property
    def gli(self) -> int:
        return self.process.read_u32(self.gli_ptr)

    @property
    def lvl(self) -> int:
        return self.process.read_u32(self.lvl_ptr)

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

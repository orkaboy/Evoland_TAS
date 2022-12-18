# Libraries and Core Files
import contextlib
import logging

from memory.core import LIBHL_OFFSET, LocProcess, mem_handle
from memory.evo1.zelda import get_zelda_memory

logger = logging.getLogger(__name__)


class BattleEntity:

    _TIMER_SINCE_TURN_PTR = [0xD0]  # double (could also be animation frame counter?)
    _MAX_HP_PTR = [0xF0]  # int
    _CUR_HP_PTR = [0xF4]  # int
    _ATK_PTR = [0xF8]  # int
    _DEF_PTR = [0xFC]  # int
    _EVADE_PTR = [0x100]  # int
    _MAGIC_PTR = [0x104]  # int
    _TURN_GAUGE_PTR = [0x110]  # double: [0-1.0]
    _TURN_GAUGE_SPEED_PTR = [0x118]  # double
    _TURN_COUNTER_PTR = [0x154]  # int
    _IS_RUNNING_PTR = [0x109]  # byte

    _NAME_BUF_PTR = [0x3C, 0x4, 0x0]  # string buffer (2-byte unicode)
    _NAME_LEN_PTR = [0x3C, 0x8]  # string buffer len

    # 0x3C seems to be the name structure. Followed by 0x4 the string buffer, 0x8 the amount of chars

    def __init__(self, process: LocProcess, entity_ptr: int):
        self.process = process
        self.entity_ptr = entity_ptr
        self.setup_pointers()

    def setup_pointers(self) -> None:
        self.max_hp_ptr = self.process.get_pointer(
            self.entity_ptr, offsets=self._MAX_HP_PTR
        )
        self.cur_hp_ptr = self.process.get_pointer(
            self.entity_ptr, offsets=self._CUR_HP_PTR
        )
        self.atk_ptr = self.process.get_pointer(self.entity_ptr, offsets=self._ATK_PTR)
        self.def_ptr = self.process.get_pointer(self.entity_ptr, offsets=self._DEF_PTR)
        self.evade_ptr = self.process.get_pointer(
            self.entity_ptr, offsets=self._EVADE_PTR
        )
        self.magic_ptr = self.process.get_pointer(
            self.entity_ptr, offsets=self._MAGIC_PTR
        )
        self.turn_gauge_ptr = self.process.get_pointer(
            self.entity_ptr, offsets=self._TURN_GAUGE_PTR
        )
        self.turn_gauge_speed_ptr = self.process.get_pointer(
            self.entity_ptr, offsets=self._TURN_GAUGE_SPEED_PTR
        )
        self.turn_counter_ptr = self.process.get_pointer(
            self.entity_ptr, offsets=self._TURN_COUNTER_PTR
        )
        self.timer_since_turn_ptr = self.process.get_pointer(
            self.entity_ptr, offsets=self._TIMER_SINCE_TURN_PTR
        )
        self.name_buf_ptr = self.process.get_pointer(
            self.entity_ptr, offsets=self._NAME_BUF_PTR
        )
        self.name_len_ptr = self.process.get_pointer(
            self.entity_ptr, offsets=self._NAME_LEN_PTR
        )
        self.is_running_ptr = self.process.get_pointer(
            self.entity_ptr, offsets=self._IS_RUNNING_PTR
        )

    @property
    def name(self) -> str:
        # TODO: Verify, doesn't work yet
        num_chars = self.process.read_u32(self.name_len_ptr)
        name_str = self.process.read_string(self.name_buf_ptr, num_chars)
        return name_str

    @property
    def max_hp(self) -> int:
        return self.process.read_u32(self.max_hp_ptr)

    @property
    def cur_hp(self) -> int:
        return self.process.read_u32(self.cur_hp_ptr)

    @property
    def attack(self) -> int:
        return self.process.read_u32(self.atk_ptr)

    @property
    def defense(self) -> int:
        return self.process.read_u32(self.def_ptr)

    @property
    def evade(self) -> int:
        return self.process.read_u32(self.evade_ptr)

    @property
    def magic(self) -> int:
        return self.process.read_u32(self.magic_ptr)

    @property
    def turn_gauge(self) -> float:
        return self.process.read_double(self.turn_gauge_ptr)

    @property
    def turn_gauge_speed(self) -> float:
        return self.process.read_double(self.turn_gauge_speed_ptr)

    @property
    def timer_since_turn(self) -> float:
        return self.process.read_double(self.timer_since_turn_ptr)

    @property
    def turn_counter(self) -> int:
        return self.process.read_u32(self.turn_counter_ptr)

    @property
    def running(self) -> bool:
        return self.process.read_u8(self.is_running_ptr) == 1


class BattleMemory:
    # All battle data is stored here
    _BATTLE_BASE_PTR = [0x860, 0x0, 0x244]
    # All allies are listed here
    _ALLIES_ARR_SIZE_PTR = [0x2C, 0x4]
    _ALLIES_ARR_BASE_PTR = [0x2C, 0x8]
    # All enemies are listed here
    _ENEMIES_ARR_SIZE_PTR = [0x30, 0x4]
    _ENEMIES_ARR_BASE_PTR = [0x30, 0x8]
    # Each list has these properties
    _FIRST_ENT_OFFSET = 0x10  # Offset from base ptr
    _ENT_PTR_SIZE = 0x4  # 0x10, 0x14...

    # Only valid when menu is open
    _PLAYER_ATB_MENU_CURSOR_PTR = [0x48, 0x8C]
    # Also used for item menu (not based in battle struct for some reason)
    _PLAYER_ATB_SPECIAL_MENU_CURSOR_PTR = [0x7C8, 0x8, 0x3C, 0x4C, 0x8, 0x1C, 0xC, 0x8C]

    def __init__(self):
        # Check if we are in battle
        self.active = False
        mem = get_zelda_memory()
        if mem.player.in_control:
            return

        # Set up memory access, get the base pointer to the battle structure
        mem = mem_handle()
        self.process = mem.process
        self.base_addr = mem.base_addr
        self.base_offset = self.process.get_pointer(
            self.base_addr + LIBHL_OFFSET, offsets=self._BATTLE_BASE_PTR
        )

        self.menu_open = False
        self.active = True
        self.update()

    def update(self):
        self.menu_open = False
        try:
            self.allies = self._init_entities(
                array_size_ptr=self._ALLIES_ARR_SIZE_PTR,
                array_base_ptr=self._ALLIES_ARR_BASE_PTR,
            )
            self.enemies = self._init_entities(
                array_size_ptr=self._ENEMIES_ARR_SIZE_PTR,
                array_base_ptr=self._ENEMIES_ARR_BASE_PTR,
            )
            # TODO: Other battle related data? Cursors gui etc.
        except ReferenceError:
            self.active = False

        if self.active:
            with contextlib.suppress(ValueError):
                self.cursor_ptr = self.process.get_pointer(
                    self.base_offset, offsets=self._PLAYER_ATB_MENU_CURSOR_PTR
                )
                self.menu_open = True

    def _init_entities(
        self, array_size_ptr: list[int], array_base_ptr: list[int]
    ) -> list[BattleEntity]:
        entities: list[BattleEntity] = []
        entities_arr_size_ptr = self.process.get_pointer(
            self.base_offset, offsets=array_size_ptr
        )
        entities_arr_size = self.process.read_u32(entities_arr_size_ptr)
        entities_arr_offset = self.process.get_pointer(
            self.base_offset, offsets=array_base_ptr
        )
        for i in range(entities_arr_size):
            # Set enemy offsets
            entity_offset = self._FIRST_ENT_OFFSET + i * self._ENT_PTR_SIZE
            entity_ptr = self.process.get_pointer(entities_arr_offset, [entity_offset])
            entities.append(BattleEntity(self.process, entity_ptr))
        return entities

    @property
    def ended(self) -> bool:
        # Check if every enemy is defeated, if so, battle has ended
        if len(self.enemies) == 0:
            return True
        # Check if every ally has fallen, if so, battle has ended
        return all(ally.cur_hp <= 0 for ally in self.allies)

    @property
    def cursor(self) -> int:
        return self.process.read_u32(self.cursor_ptr)

    @property
    def battle_active(self) -> bool:
        mem = get_zelda_memory()
        in_control = mem.player.in_control
        battle_active = False if in_control else self.active
        return battle_active

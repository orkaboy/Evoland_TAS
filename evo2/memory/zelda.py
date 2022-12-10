# Libraries and Core Files
import logging
import math

from engine.mathlib import Vec2
from memory.core import LIBHL_OFFSET, LocProcess, mem_handle

logger = logging.getLogger(__name__)


# Only valid when instantiated, on the screen that they live
class PlayerEntity:
    _CUR_HP_PTR = [0x64]
    _IFRAME_PTR = [0x74]
    _IN_CONTROL_PTR = [0x90]
    _X_PTR = [0x188]
    _Y_PTR = [0x190]
    _ROTATION_PTR = [0x1A8]

    def __init__(self, process: LocProcess, entity_ptr: int) -> None:
        self.process = process
        self.entity_ptr = entity_ptr
        self.setup_pointers()

    def setup_pointers(self) -> None:
        self.x_ptr = self.process.get_pointer(self.entity_ptr, offsets=self._X_PTR)
        self.y_ptr = self.process.get_pointer(self.entity_ptr, offsets=self._Y_PTR)
        self.rotation_ptr = self.process.get_pointer(
            self.entity_ptr, offsets=self._ROTATION_PTR
        )
        self.cur_hp_ptr = self.process.get_pointer(
            self.entity_ptr, offsets=self._CUR_HP_PTR
        )
        self.iframe_ptr = self.process.get_pointer(
            self.entity_ptr, offsets=self._IFRAME_PTR
        )
        self.in_control_ptr = self.process.get_pointer(
            self.entity_ptr, offsets=self._IN_CONTROL_PTR
        )

    @property
    def pos(self) -> Vec2:
        return Vec2(
            self.process.read_double(self.x_ptr),
            self.process.read_double(self.y_ptr),
        )

    @property
    def rotation(self) -> float:
        return self.process.read_double(self.rotation_ptr)

    @property
    def cur_hp(self) -> int:
        return self.process.read_u32(self.cur_hp_ptr)

    @property
    # When this is true, we cannot take damage
    def iframe(self) -> bool:
        return self.process.read_u32(self.iframe_ptr) == 1

    @property
    def not_in_control(self) -> bool:
        return self.process.read_u32(self.in_control_ptr) == 1

    @property
    def in_control(self) -> bool:
        return self.process.read_u32(self.in_control_ptr) == 0


class GameEntity2D:
    # TODO: Enemy HP?
    # Note, same relative offsets as on the player
    _X_PTR = [0x130]
    _Y_PTR = [0x138]
    _ROTATION_PTR = [0x150]

    def __init__(self, process: LocProcess, entity_ptr: int) -> None:
        self.process = process
        self.entity_ptr = entity_ptr
        self.setup_pointers()

    def setup_pointers(self) -> None:
        self.x_ptr = self.process.get_pointer(self.entity_ptr, offsets=self._X_PTR)
        self.y_ptr = self.process.get_pointer(self.entity_ptr, offsets=self._Y_PTR)
        self.rotation_ptr = self.process.get_pointer(
            self.entity_ptr, offsets=self._ROTATION_PTR
        )

    def __eq__(self, other: object) -> bool:
        # kind_match = self.kind == other.kind
        pos_match = self.pos.close_to(other.pos, 0.2)
        # return kind_match and pos_match
        return pos_match

    @property
    def pos(self) -> Vec2:
        return Vec2(
            self.process.read_double(self.x_ptr),
            self.process.read_double(self.y_ptr),
        )

    @property
    # Note, this is not restricted to [-3.14 .. 3.14]; it needs to be adjusted into range
    def rotation(self) -> float:
        raw_rot = self.process.read_double(self.rotation_ptr)
        while raw_rot >= math.pi:
            raw_rot -= 2 * math.pi
        while raw_rot < math.pi:
            raw_rot += 2 * math.pi
        return raw_rot


class ZeldaMemory:
    # Zelda-related things:
    _ZELDA_PTR = [0x37C, 0x0, 0x58]
    _PLAYER_PTR = [0x30]

    _ACTOR_ARR_PTR = [0x44, 0x8]
    _ACTOR_ARR_SIZE_PTR = [0x44, 0x4]  # TODO: Verify
    _ACTOR_PTR_SIZE = 4
    _ACTOR_BASE_ADDR = 0x18  # TODO: Verify

    def __init__(self):
        mem = mem_handle()
        self.process = mem.process
        self.base_addr = mem.base_addr
        self.base_offset = self.process.get_pointer(
            self.base_addr + LIBHL_OFFSET, offsets=self._ZELDA_PTR
        )

        self._init_player()
        self._init_actors()

    def _init_player(self):
        player_ptr = self.process.get_pointer(self.base_offset, self._PLAYER_PTR)
        self.player = PlayerEntity(self.process, player_ptr)

    def _init_actors(self):
        self.actors: list[GameEntity2D] = []
        actor_arr_size_ptr = self.process.get_pointer(
            self.base_offset, offsets=self._ACTOR_ARR_SIZE_PTR
        )
        actor_arr_size = self.process.read_u32(actor_arr_size_ptr)
        actor_arr_offset = self.process.get_pointer(
            self.base_offset, offsets=self._ACTOR_ARR_PTR
        )
        for i in range(actor_arr_size):
            # Set enemy offsets
            actor_offset = self._ACTOR_BASE_ADDR + i * self._ACTOR_PTR_SIZE
            actor_ptr = self.process.get_pointer(actor_arr_offset, [actor_offset])
            self.actors.append(GameEntity2D(self.process, actor_ptr))


_zelda_mem = None


def load_zelda_memory() -> None:
    global _zelda_mem
    _zelda_mem = ZeldaMemory()


def get_zelda_memory() -> ZeldaMemory:
    return _zelda_mem

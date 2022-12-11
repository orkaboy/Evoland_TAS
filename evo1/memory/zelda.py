# Libraries and Core Files
import logging
from enum import IntEnum
from typing import Optional, Tuple

from engine.mathlib import Facing, Vec2
from memory.core import LIBHL_OFFSET, LocProcess
from memory.zelda_base import GameEntity2D, ZeldaMemory

logger = logging.getLogger(__name__)


# Only valid when instantiated, on the screen that they live
class Evo1GameEntity2D(GameEntity2D):
    _ENT_KIND_PTR = [0x4, 0x4]  # int
    _X_PTR = [0x8]  # double
    _Y_PTR = [0x10]  # double
    _X_TILE_PTR = [0x14]  # int
    _Y_TILE_PTR = [0x18]  # int
    _SPEED_PTR = [0x20]  # double (quite small numbers, 0.05 for player)
    _TARGET_PTR = [0x40]  # Target pointer. Only valid if != 0
    _TARGET_X_OFFSET = 0x18  # In reference to Target
    _TARGET_Y_OFFSET = 0x20  # In reference to Target
    _TIMER_PTR = [0x48]  # double (timeout in s)
    _FACING_PTR = [0x58]  # int
    _ATTACK_PTR = [0x5C]  # byte, bit 5
    _ROTATION_PTR = [0x90]  # double (left = 0.0, up = 1.57, right = 3.14, down = -1.57)
    _HP_PTR = [0x100]  # int, for enemies such as knights
    # TODO: _ATTACK_TIMER_PTR = [0xC8]  # double. unclear purpose, resets when swinging sword
    _ENCOUNTER_TIMER_PTR = [0xD0]  # double. Steps to encounter
    _IN_CONTROL_PTR = [0xA4]

    def __init__(self, process: LocProcess, entity_ptr: int):
        super().__init__(process=process, entity_ptr=entity_ptr)
        self.setup_pointers()

    def __eq__(self, other: object) -> bool:
        kind_match = self.kind == other.kind
        pos_match = self.pos == other.pos
        return kind_match and pos_match

    def setup_pointers(self) -> None:
        self.ent_kind_ptr = self.process.get_pointer(
            self.entity_ptr, offsets=self._ENT_KIND_PTR
        )
        self.x_ptr = self.process.get_pointer(self.entity_ptr, offsets=self._X_PTR)
        self.y_ptr = self.process.get_pointer(self.entity_ptr, offsets=self._Y_PTR)
        self.x_tile_ptr = self.process.get_pointer(
            self.entity_ptr, offsets=self._X_TILE_PTR
        )
        self.y_tile_ptr = self.process.get_pointer(
            self.entity_ptr, offsets=self._Y_TILE_PTR
        )
        self.speed_ptr = self.process.get_pointer(
            self.entity_ptr, offsets=self._SPEED_PTR
        )
        self.target_ptr = self.process.get_pointer(
            self.entity_ptr, offsets=self._TARGET_PTR
        )
        self.timer_ptr = self.process.get_pointer(
            self.entity_ptr, offsets=self._TIMER_PTR
        )
        self.facing_ptr = self.process.get_pointer(
            self.entity_ptr, offsets=self._FACING_PTR
        )
        self.attack_ptr = self.process.get_pointer(
            self.entity_ptr, offsets=self._ATTACK_PTR
        )
        self.rotation_ptr = self.process.get_pointer(
            self.entity_ptr, offsets=self._ROTATION_PTR
        )
        self.hp_ptr = self.process.get_pointer(self.entity_ptr, offsets=self._HP_PTR)
        self.in_control_ptr = self.process.get_pointer(
            self.entity_ptr, offsets=self._IN_CONTROL_PTR
        )
        self.encounter_timer_ptr = self.process.get_pointer(
            self.entity_ptr, offsets=self._ENCOUNTER_TIMER_PTR
        )

    class EKind(IntEnum):
        PLAYER = 0
        # TODO 1=?
        ENEMY = 2
        CHEST = 3
        ITEM = 4
        NPC = 5
        PARTICLE = 6  # When breaking pots, closing bars?
        SPECIAL = 7
        UNKNOWN = 999

    @property
    def kind(self) -> EKind:
        kind_val = self.process.read_u32(self.ent_kind_ptr)
        try:
            return Evo1GameEntity2D.EKind(kind_val)
        except ValueError:
            logger.error(f"Unknown GameEntity2D EKind: {kind_val}")
            return Evo1GameEntity2D.EKind.UNKNOWN

    @property
    def ch(self) -> str:
        actor_kind = self.kind
        match actor_kind:
            case Evo1GameEntity2D.EKind.PLAYER:
                return "@"
            case Evo1GameEntity2D.EKind.ENEMY:
                return "!"
            case Evo1GameEntity2D.EKind.CHEST:
                return "C"
            case Evo1GameEntity2D.EKind.ITEM:
                return "$"
            case Evo1GameEntity2D.EKind.NPC:
                return "&"
            case Evo1GameEntity2D.EKind.PARTICLE:
                return "%"
            case Evo1GameEntity2D.EKind.SPECIAL:
                return "*"
            case _:
                return "?"

    @property
    def pos(self) -> Vec2:
        return Vec2(
            self.process.read_double(self.x_ptr),
            self.process.read_double(self.y_ptr),
        )

    @property
    def tile_pos(self) -> Tuple[int, int]:
        return [
            self.process.read_u32(self.x_tile_ptr),
            self.process.read_u32(self.y_tile_ptr),
        ]

    @property
    def speed(self) -> float:
        return self.process.read_double(self.speed_ptr)

    @property
    def target(self) -> Optional[Vec2]:
        target_ptr = self.process.read_u32(self.target_ptr)
        if target_ptr != 0:
            return Vec2(
                x=self.process.read_double(target_ptr + self._TARGET_X_OFFSET),
                y=self.process.read_double(target_ptr + self._TARGET_Y_OFFSET),
            )
        return None

    @property
    def timer(self) -> float:
        return self.process.read_double(self.timer_ptr)

    # 0=left,1=right,2=up,3=down. Doesn't do diagonal facings.
    @property
    def facing(self) -> Facing:
        return self.process.read_u32(self.facing_ptr)

    @property
    def is_attacking(self) -> bool:
        attacking = self.process.read_u8(self.attack_ptr)
        return attacking & 0x10  # Bit5 denotes attacking

    @property
    def rotation(self) -> float:
        return self.process.read_double(self.rotation_ptr)

    @property
    def hp(self) -> int:
        return self.process.read_u32(self.hp_ptr)

    @property
    def not_in_control(self) -> bool:
        return self.process.read_u8(self.in_control_ptr) == 1

    @property
    def in_control(self) -> bool:
        return self.process.read_u8(self.in_control_ptr) == 0

    @property
    def encounter_timer(self) -> float:
        return self.process.read_double(self.encounter_timer_ptr)

    def __repr__(self) -> str:
        kind = self.kind
        hp_str = f", hp: {self.hp}" if kind == self.EKind.ENEMY else ""
        return f"Ent({kind.name}, {self.pos}{hp_str})"


class Evo1ZeldaMemory(ZeldaMemory):

    # Zelda-related things:
    _ZELDA_PTR = [0x7C8, 0x8, 0x3C]
    _PLAYER_PTR = [0x30]

    _ACTOR_ARR_PTR = [0x48, 0x8]
    _ACTOR_ARR_SIZE_PTR = [0x48, 0x4]
    _ACTOR_PTR_SIZE = 4
    _ACTOR_BASE_ADDR = 0x10

    def __init__(self):
        super().__init__()
        self.base_offset = self.process.get_pointer(
            self.base_addr + LIBHL_OFFSET, offsets=self._ZELDA_PTR
        )

        self._init_player()
        self._init_actors()

    def _init_player(self):
        player_ptr = self.process.get_pointer(self.base_offset, self._PLAYER_PTR)
        self.player = Evo1GameEntity2D(self.process, player_ptr)

    def _init_actors(self):
        self.actors: list[Evo1GameEntity2D] = []
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
            self.actors.append(Evo1GameEntity2D(self.process, actor_ptr))


_zelda_mem = None


def load_zelda_memory() -> None:
    global _zelda_mem
    _zelda_mem = Evo1ZeldaMemory()


def get_zelda_memory() -> Evo1ZeldaMemory:
    return _zelda_mem

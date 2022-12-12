from engine.mathlib import Facing, Vec2
from memory.core import LocProcess, mem_handle


class GameEntity2D:
    def __init__(self, process: LocProcess, entity_ptr: int = 0) -> None:
        self.process = process
        self.entity_ptr = entity_ptr

    @property
    def pos(self) -> Vec2:
        return Vec2(0, 0)

    @property
    def rotation(self) -> float:
        return 0.0

    # 0=left,1=right,2=up,3=down. Doesn't do diagonal facings.
    @property
    def facing(self) -> Facing:
        return Facing.DOWN

    @property
    def in_control(self) -> bool:
        return False

    @property
    def is_enemy(self) -> bool:
        return True

    @property
    def is_alive(self) -> bool:
        return True

    @property
    def ch(self) -> str:
        return "?"


class ZeldaMemory:
    def __init__(self) -> None:
        mem = mem_handle()
        self.process = mem.process
        self.base_addr = mem.base_addr

        self.player = GameEntity2D(self.process)
        self.actors: list[GameEntity2D] = []

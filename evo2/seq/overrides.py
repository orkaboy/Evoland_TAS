from typing import Optional

from engine.combat import CombatPlan, SeqArenaCombat, SeqCombat
from engine.mathlib import Box2, Vec2
from engine.move2d import SeqMove2D, SeqMove2DConfirm
from engine.pathing import TileMap
from evo2.memory import Evo2ZeldaMemory, get_zelda_memory


class Evo2SeqBase:
    def get_tilemap(self) -> Optional[TileMap]:
        # TODO:
        return None

    def zelda_mem(self) -> Evo2ZeldaMemory:
        return get_zelda_memory()


# MOVE2D
class Evo2SeqMove2D(Evo2SeqBase, SeqMove2D):
    def __init__(
        self, name: str, coords: list[Vec2], precision: float = 0.2, func=None
    ):
        super().__init__(name=name, coords=coords, precision=precision, func=func)


class Evo2SeqMove2DConfirm(Evo2SeqBase, SeqMove2DConfirm):
    def __init__(self, name: str, coords: list[Vec2], precision: float = 0.2):
        super().__init__(name=name, coords=coords, precision=precision)


# COMBAT
class Evo2CombatPlan(CombatPlan):
    def __init__(self, arena: Box2, num_targets: int, retracking: bool = False) -> None:
        super().__init__(
            mem_func=get_zelda_memory,
            arena=arena,
            num_targets=num_targets,
            retracking=retracking,
        )


class Evo2SeqCombat(Evo2SeqBase, SeqCombat):
    def __init__(
        self,
        name: str,
        arena: Box2,
        num_targets: int,
        precision: float = 0.2,
        retracking: bool = False,
    ) -> None:
        super().__init__(
            name,
            arena=arena,
            num_targets=num_targets,
            precision=precision,
            retracking=retracking,
            planner=Evo2CombatPlan,
        )


class Evo2SeqArenaCombat(Evo2SeqBase, SeqArenaCombat):
    def __init__(
        self,
        name: str,
        arena: Box2,
        num_targets: int,
        precision: float = 0.2,
        retracking: bool = False,
    ) -> None:
        super().__init__(
            name,
            arena=arena,
            num_targets=num_targets,
            precision=precision,
            retracking=retracking,
            planner=Evo2CombatPlan,
        )

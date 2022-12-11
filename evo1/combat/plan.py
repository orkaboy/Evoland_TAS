from engine.combat import CombatPlan
from evo1.memory import Evo1GameEntity2D


class Evo1CombatPlan(CombatPlan):
    # OVERRIDE
    def is_enemy(self, actor: Evo1GameEntity2D) -> bool:
        return actor.kind == Evo1GameEntity2D.EKind.ENEMY

    # OVERRIDE
    def is_alive(self, actor: Evo1GameEntity2D) -> bool:
        return actor.hp > 0

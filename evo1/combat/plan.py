import contextlib
import logging
from typing import List, Optional

from engine.mathlib import Box2, dist
from evo1.memory import GameEntity2D, ZeldaMemory, get_zelda_memory

logger = logging.getLogger(__name__)


class CombatPlan:
    def __init__(self, mem: ZeldaMemory, arena: Box2, num_targets: int) -> None:
        self.targets: List[GameEntity2D] = []
        self.next_target: Optional[GameEntity2D] = None
        # Map start positions to array of GameEntity2D to track
        with contextlib.suppress(
            ReferenceError
        ):  # Needed until I figure out which enemies are valid (broken pointers will throw an exception)
            for actor in mem.actors:
                if actor.kind != GameEntity2D.EKind.ENEMY:
                    continue
                enemy_pos = actor.pos
                # Check if target is found. If so, initialize the tracking entity
                if arena.contains(enemy_pos):
                    self.targets.append(actor)
        if num_targets != len(self.targets):
            logger.error(
                f"Couldn't track all entities! Found {len(self.targets)}/{num_targets} enemies"
            )

    def done(self) -> bool:
        return len(self.targets) == 0

    def get_next_target(self) -> Optional[GameEntity2D]:
        if self.next_target:
            return self.next_target

        mem = get_zelda_memory()
        player_pos = mem.player.pos
        # Using key sorting, order by closest target to player
        key_list = [(dist(player_pos, target.pos), target) for target in self.targets]
        sorted_list = sorted(key_list)
        if sorted_list:
            self.next_target = sorted_list[0][1]
            return self.next_target
        else:
            return None

    def remove_dead(self) -> None:
        self.targets = [enemy for enemy in self.targets if enemy.hp > 0]
        if self.next_target not in self.targets:
            self.next_target = None

    def enemies_left(self) -> int:
        return len(self.targets)

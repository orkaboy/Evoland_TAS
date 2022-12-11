import contextlib
import logging
from typing import Callable, Optional

from engine.mathlib import Box2, dist
from memory.zelda_base import GameEntity2D, ZeldaMemory

logger = logging.getLogger(__name__)


class CombatPlan:
    def __init__(
        self,
        mem_func: Callable[[], ZeldaMemory],
        arena: Box2,
        num_targets: int,
        retracking: bool = False,
    ) -> None:
        self.mem_func = mem_func
        self.next_target: Optional[GameEntity2D] = None
        self.num_targets = num_targets
        self.total_enemies: int = 0
        self.arena = arena
        self.retracking = retracking
        self.targets = self.track_targets()
        if self.num_targets != len(self.targets):
            logger.error(
                f"Couldn't track all entities! Found {len(self.targets)}/{self.num_targets} enemies"
            )

    def track_targets(self) -> list[GameEntity2D]:
        ret = []
        mem = self.mem_func()
        # Map enemies in arena to array of GameEntity2D to track
        # Needed until I figure out which enemies are valid (broken pointers will throw an exception)
        with contextlib.suppress(ReferenceError):
            for actor in mem.actors:
                if not self.is_enemy(actor):
                    continue
                enemy_pos = actor.pos
                # Check if target is found. If so, initialize the tracking entity
                if self.arena.contains(enemy_pos):
                    ret.append(actor)
        return ret

    def done(self) -> bool:
        return len(self.targets) == 0

    def get_next_target(self) -> Optional[GameEntity2D]:
        if self.next_target:
            return self.next_target

        mem = self.mem_func()
        player_pos = mem.player.pos
        # Using key sorting, order by closest target to player
        key_list = [(dist(player_pos, target.pos), target) for target in self.targets]
        sorted_list = sorted(key_list)
        if sorted_list:
            self.next_target = sorted_list[0][1]
            return self.next_target
        else:
            return None

    # TODO: This only works for the knights, not the bats that die in one hit
    def remove_dead(self) -> None:
        if self.retracking:
            scan = self.track_targets()
            self.targets = [enemy for enemy in self.targets if enemy in scan]
        else:
            self.targets = [enemy for enemy in self.targets if self.is_alive(enemy)]
        if self.next_target not in self.targets:
            self.next_target = None

    def enemies_left(self) -> int:
        return len(self.targets)

    # OVERRIDE
    def is_enemy(self, actor: GameEntity2D) -> bool:
        return True

    # OVERRIDE
    def is_alive(self, actor: GameEntity2D) -> bool:
        return False

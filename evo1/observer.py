import contextlib
import logging

from evo1.memory import get_zelda_memory
from engine.mathlib import Vec2, dist
from evo1.move2d import SeqSection2D
from term.window import WindowLayout

logger = logging.getLogger(__name__)


class SeqObserver2D(SeqSection2D):
    def __init__(self, name: str, annotations: dict = None, func=None):
        self.tracked: set[Vec2] = set()
        super().__init__(name, annotations=annotations, func=func)

    def reset(self) -> None:
        self.tracked = set()

    def execute(self, delta: float) -> bool:
        super().execute(delta=delta)
        mem = get_zelda_memory()
        player_pos = mem.player.pos
        with contextlib.suppress(
            ReferenceError
        ):  # Needed until I figure out which actors are valid (broken pointers will throw an exception)
            for i, actor in enumerate(mem.actors):
                actor_pos = actor.pos
                if actor_pos in self.tracked:
                    continue
                dist_to_player = dist(player_pos, actor_pos)
                if dist_to_player < 3:  # TODO Arbitrary magic number, distance to enemy
                    logger.info(f"Actor[{i}] {actor}")
                    self.tracked.add(actor_pos)
        return False # Never finishes

    def render(self, window: WindowLayout) -> None:
        super().render(window)
        self._print_actors(map_win=window.map)

        mem = get_zelda_memory()

        if target := mem.player.target:
            window.stats.addstr(Vec2(1, 9), f" Target X: {target.x:.3f}")
            window.stats.addstr(Vec2(1, 10), f" Target Y: {target.y:.3f}")


import contextlib
import logging

from engine.mathlib import Vec2, dist
from evo1.atb import SeqATBCombatManual, SeqATBmove2D
from evo1.memory import get_zelda_memory
from term.window import WindowLayout

logger = logging.getLogger(__name__)


class SeqObserver2D(SeqATBmove2D):
    def __init__(self, name: str, func=None):
        self.tracked: set[Vec2] = set()
        super().__init__(
            name,
            coords=[],
            func=func,
            battle_handler=SeqATBCombatManual(),
        )

    def reset(self) -> None:
        self.tracked = set()

    def execute(self, delta: float) -> bool:
        if self.func:
            self.func()

        self.calc_next_encounter()
        self.handle_combat(delta)

        mem = get_zelda_memory()
        player_pos = mem.player.pos
        # Needed until I figure out which actors are valid (broken pointers will throw an exception)
        with contextlib.suppress(ReferenceError):
            for i, actor in enumerate(mem.actors):
                actor_pos = actor.pos
                if actor_pos in self.tracked:
                    continue
                dist_to_player = dist(player_pos, actor_pos)
                if dist_to_player < 3:  # TODO Arbitrary magic number, distance to enemy
                    logger.info(f"Actor[{i}] {actor}")
                    self.tracked.add(actor_pos)

        return False  # Never finishes

    def render(self, window: WindowLayout) -> None:
        super().render(window)
        self._print_actors(map_win=window.map)

        if (
            self.battle_handler.active
            and not self.battle_handler.mem.ended
            and self.battle_handler.mem.enemies[0].turn_gauge < -1
        ):
            window.main.addstr(Vec2(3, 10), "INVINCIBLE")


#       mem = get_zelda_memory()
#
#       if target := mem.player.target:
#           window.stats.addstr(Vec2(1, 9), f" Target X: {target.x:.3f}")
#           window.stats.addstr(Vec2(1, 10), f" Target Y: {target.y:.3f}")

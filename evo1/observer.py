import contextlib
import logging

from engine.mathlib import Vec2, dist
from evo1.atb import SeqATBCombatManual, SeqATBmove2D, calc_next_encounter
from evo1.memory import get_memory, get_zelda_memory
from memory.rng import EvolandRNG
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
        mem = get_zelda_memory()
        player_pos = mem.player.pos

        # For some reason, this flag is set when in ATB combat
        if mem.player.not_in_control:
            # Check for active battle (returns True on completion/non-execution)
            self.battle_handler.execute(delta=delta)

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

        mem = get_memory()
        rng = EvolandRNG().get_rng()
        self.next_enc = calc_next_encounter(
            rng=rng, has_3d_monsters=False, clink_level=mem.lvl
        )

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

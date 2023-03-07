import contextlib
import logging
import math

from control import evo_ctrl
from engine.mathlib import dist
from engine.move2d import SeqMove2D

logger = logging.getLogger(__name__)


class SeqMove2DClunkyCombat(SeqMove2D):
    DETECTION_DISTANCE = 1.5

    # OVERRIDE
    def should_move(self) -> bool:
        return True

    def execute(self, delta: float) -> bool:
        if self._clunky_combat2d():
            pass
        elif self.should_move():
            self.navigate_to_checkpoint()

        done = self._nav_done()

        if done:
            logger.info(f"Finished moved2D section: {self.name}")
        return done

    # ============
    # = Algoritm =
    # ============
    # TODO: Implement
    # * Check where we are going in the next few steps (TODO: need to know player speed)
    # * Check where nearby enemies are, and which squares are threatened. Enemies has a threat of 1 in the current square they are in, 0.5 in adjacent (transferred over when moving)
    # * Adjacent threat is adjusted by timer
    # * Avoid moving into threatened squares
    # * Keep track on our weapon cooldown
    # * Keep track of our attack potential (stab hitbox is smaller than our hurtbox)
    # * The goal is not to kill the enemy, but to get past them!

    # TODO: Handle some edge cases, like when the enemy is at a diagonal, moving into the target space
    def _clunky_combat2d(self) -> bool:
        mem = self.zelda_mem()
        player_pos = mem.player.pos

        with contextlib.suppress(ReferenceError):
            for actor in mem.actors:
                if not actor.is_enemy:
                    continue
                enemy_pos = actor.pos
                dist_to_player = dist(player_pos, enemy_pos)
                if dist_to_player < self.DETECTION_DISTANCE and self.turn_towards_pos(
                    target_pos=enemy_pos, precision=math.pi / 4
                ):
                    ctrl = evo_ctrl()
                    ctrl.attack(tapping=False)
                    return True
        return False

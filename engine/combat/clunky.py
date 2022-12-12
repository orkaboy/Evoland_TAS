import contextlib
import logging
import math

from control import evo_ctrl
from engine.mathlib import Vec2, angle_between, dist
from engine.move2d import SeqMove2D

logger = logging.getLogger(__name__)


class SeqMove2DClunkyCombat(SeqMove2D):

    DETECTION_DISTANCE = 1.5

    def execute(self, delta: float) -> bool:
        self._navigate_to_checkpoint()

        target = (
            self.coords[self.step] if self.step < len(self.coords) else self.coords[-1]
        )
        self._clunky_combat2d(target=target)

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
    def _clunky_combat2d(self, target: Vec2) -> None:
        mem = self.zelda_mem()
        player_pos = mem.player.pos
        player_angle = (target - player_pos).angle
        # Needed until I figure out which enemies are valid (broken pointers will throw an exception)
        with contextlib.suppress(ReferenceError):
            for actor in mem.actors:
                if not actor.is_enemy:
                    continue
                enemy_pos = actor.pos
                dist_to_player = dist(player_pos, enemy_pos)
                if dist_to_player < self.DETECTION_DISTANCE:
                    enemy_angle = (enemy_pos - player_pos).angle
                    angle = angle_between(enemy_angle, player_angle)
                    # logger.debug(f"Enemy {i} dist: {dist_to_player}, angle_to_e: {enemy_angle}. angle: {angle}")
                    self._clunky_counter_with_sword(
                        angle=angle, enemy_angle=enemy_angle
                    )

    def _clunky_counter_with_sword(self, angle: float, enemy_angle: float) -> None:
        # If in front, attack!
        # TODO Arbitrary magic number, angle difference between where we are heading and where the enemy is
        if abs(angle) < math.pi / 4:
            ctrl = evo_ctrl()
            ctrl.attack(tapping=False)
        elif abs(angle) <= math.pi / 2:  # TODO On our sides
            ctrl = evo_ctrl()
            ctrl.attack(tapping=False)
            ctrl.dpad.none()
            # Turn and attack (angle is in the range +PI to -PI, with 0 to our right)
            if abs(enemy_angle) < math.pi / 4:
                ctrl.dpad.right()
            elif abs(enemy_angle) > 3 * math.pi / 4:
                ctrl.dpad.left()
            elif enemy_angle > 0:
                ctrl.dpad.down()
            else:
                ctrl.dpad.up()

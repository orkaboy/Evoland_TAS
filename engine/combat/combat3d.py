import logging
import math

from control import evo_ctrl
from engine.combat.base import SeqCombat
from engine.mathlib import (
    Vec2,
    angle_between,
    dist,
    find_closest_point,
    get_box_with_size,
)
from engine.move2d import move_to
from memory.zelda_base import GameEntity2D

logger = logging.getLogger(__name__)


# TODO: WIP base
# TODO: This class can be used as the base of 3D combat, both for killing bats, skeletons/mages and even Dark Clink
class SeqCombat3D(SeqCombat):

    # TODO: This isn't going to work for the skeletons (need to attack them from the sides/behind, just like the knights)
    def _get_attack_vectors(self, target: GameEntity2D) -> list[Vec2]:
        mem = self.zelda_mem()
        player_pos = mem.player.pos
        enemy_pos = target.pos
        # Calculate direction from enemy to player
        direction = (player_pos - enemy_pos).normalized
        # TODO: Make this more intelligent/give more options
        # For the time being, beeline for the enemy
        attack_vector = enemy_pos + (direction * self.MIN_DISTANCE)
        return [attack_vector]

    def _try_attack(self, target: GameEntity2D, weak_spot: Vec2) -> bool:
        ctrl = evo_ctrl()
        mem = self.zelda_mem()
        player_pos = mem.player.pos
        box = get_box_with_size(center=player_pos, half_size=self.precision)
        # Check angle to enemy
        enemy_pos = target.pos
        # Check position (must be in range, in a weak spot)
        if box.contains(weak_spot) or dist(player_pos, enemy_pos) < self.MIN_DISTANCE:
            angle_to_enemy = (enemy_pos - player_pos).angle
            # The rotation is stored somewhat strangely in memory
            rot = mem.player.rotation
            player_angle = rot + math.pi if rot < 0 else rot - math.pi
            # Compare player rotation to angle_to_enemy
            angle = angle_between(angle_to_enemy, player_angle)
            if angle < math.pi / 3:  # Roughly turned in the right direction
                # We are aligned and in position. Attack!
                ctrl.dpad.none()
                ctrl.attack()
                return True
            else:
                # Turn to the correct direction, facing the enemy
                # Split into 8 directions. 0 is to the right
                # Horizontal axis
                if abs(angle_to_enemy) < 3 * math.pi / 8:
                    ctrl.dpad.right()
                elif abs(angle_to_enemy) > 5 * math.pi / 8:
                    ctrl.dpad.left()
                # Vertical axis
                if angle_to_enemy > math.pi / 8 and angle_to_enemy < 5 * math.pi / 8:
                    ctrl.dpad.down()
                elif (
                    angle_to_enemy < -math.pi / 8 and angle_to_enemy > -5 * math.pi / 8
                ):
                    ctrl.dpad.up()
                return False
        return False

    def try_move_into_position_and_attack(self, target: GameEntity2D) -> bool:
        # Find all the ways that the enemy is vulnerable
        # TODO: For 3D, we don't need to work with static positions, but rather, we should use angles.
        # TODO: This is true for the skeletons as well; we just need to be behind/to the sides of them.
        attack_vectors = self._get_attack_vectors(target=target)

        # TODO: Filter out invalid/threatened?

        if len(attack_vectors) == 0:
            return False
        # Find the closest point to attack
        mem = self.zelda_mem()
        player_pos = mem.player.pos
        closest_weak_spot = find_closest_point(origin=player_pos, points=attack_vectors)
        # Move towards target weak point
        move_to(player=player_pos, target=closest_weak_spot, precision=self.precision)
        # Attempt to attack if in range
        return self._try_attack(target=target, weak_spot=closest_weak_spot)

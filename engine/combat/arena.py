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


class SeqArenaCombat(SeqCombat):
    def _get_attack_vectors(self, target: GameEntity2D) -> list[Vec2]:
        enemy_pos = target.pos
        return [
            enemy_pos + Vec2(0, 1.1),
            enemy_pos + Vec2(0, -1.1),
            enemy_pos + Vec2(1.1, 0),
            enemy_pos + Vec2(-1.1, 0),
        ]

    def _try_attack(self, target: GameEntity2D, weak_spot: Vec2) -> bool:
        ctrl = evo_ctrl()
        mem = self.zelda_mem()
        player_pos = mem.player.pos
        box = get_box_with_size(center=player_pos, half_size=self.precision)
        # Check facing (are we facing enemy)
        enemy_pos = target.pos
        dir_to_enemy = (enemy_pos - player_pos).normalized
        horizontal = abs(dir_to_enemy.x) > abs(dir_to_enemy.y)
        rot_to_enemy = dir_to_enemy.angle
        player_rot = mem.player.rotation
        angle = angle_between(player_rot, rot_to_enemy)
        # Check position (must be in range, in a weak spot)
        if box.contains(weak_spot) or dist(player_pos, enemy_pos) < 1.2:
            if abs(angle) < math.pi / 4:
                # We are aligned and in position. Attack!
                ctrl.dpad.none()
                ctrl.attack()
                return True
            else:  # Not currently facing the enemy. Turn towards enemy
                ctrl.dpad.none()
                if horizontal:
                    if dir_to_enemy.x > 0:
                        ctrl.dpad.right()
                    else:
                        ctrl.dpad.left()
                # Vertical
                elif dir_to_enemy.y > 0:
                    ctrl.dpad.down()
                else:
                    ctrl.dpad.up()
                return False
        return False  # Couldn't attack this target right now

    # TODO: Possibly refactor this so parts of it can be reused for SeqCombat3D
    def try_move_into_position_and_attack(self, target: GameEntity2D) -> bool:
        # Find all the ways that the knight is vulnerable
        attack_vectors = self._get_attack_vectors(target=target)
        # TODO: Filter out invalid positions due to pathing (blocked by terrain)
        # Filter out threatened positions so we don't walk into another enemy
        for enemy in self.plan.targets:
            # For each enemy get a hitbox around them
            # TODO: enemy collision magic number. Get bounding box?
            enemy_hitbox = get_box_with_size(center=enemy.pos, half_size=0.2)
            # Remove any weak points that fall inside the enemy hitbox
            attack_vectors = [
                wp for wp in attack_vectors if not enemy_hitbox.contains(wp)
            ]
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

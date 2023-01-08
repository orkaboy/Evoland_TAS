import math

from control import evo_ctrl
from engine.combat.base import SeqCombat
from engine.mathlib import Vec2, dist, find_closest_point, get_box_with_size
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
        # Check position (must be in range, in a weak spot)
        if (
            box.contains(weak_spot) or dist(player_pos, enemy_pos) < self.MIN_DISTANCE
        ) and self.turn_towards_pos(enemy_pos, precision=math.pi / 4):
            ctrl.attack()
            return True
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
        # Attempt to attack if in range
        if self._try_attack(target=target, weak_spot=closest_weak_spot):
            return True
        # Move towards target weak point
        move_to(player=player_pos, target=closest_weak_spot, precision=self.precision)
        return False

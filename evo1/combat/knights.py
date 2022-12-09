import evo1.control
from engine.mathlib import (
    Facing,
    Vec2,
    find_closest_point,
    get_2d_facing_from_dir,
    get_box_with_size,
)
from evo1.combat.base import SeqCombat
from evo1.memory import GameEntity2D, get_zelda_memory
from evo1.move2d import move_to


class SeqKnight2D(SeqCombat):
    def _get_attack_vectors(self, target: GameEntity2D) -> list[Vec2]:
        enemy_facing = target.facing
        enemy_pos = target.pos
        match enemy_facing:
            case Facing.UP:
                forward = Vec2(0, -1)
                right = Vec2(1, 0)
            case Facing.RIGHT:
                forward = Vec2(1, 0)
                right = Vec2(0, 1)
            case Facing.DOWN:
                forward = Vec2(0, 1)
                right = Vec2(-1, 0)
            case Facing.LEFT:
                forward = Vec2(-1, 0)
                right = Vec2(0, -1)
        # Get us a bit further away for safety
        forward = 1.1 * forward
        right = 1.1 * right
        return [
            enemy_pos - forward,  # Behind enemy
            enemy_pos + right,  # To the right of enemy
            enemy_pos - right,  # To the left of enemy
        ]

    def _try_attack(self, target: GameEntity2D, weak_spot: Vec2) -> bool:
        ctrl = evo1.control.handle()
        mem = get_zelda_memory()
        player_pos = mem.player.pos
        box = get_box_with_size(center=player_pos, half_size=self.precision)
        # Check facing (are we facing enemy)
        dir_to_enemy = target.pos - player_pos
        facing_to_enemy = get_2d_facing_from_dir(dir_to_enemy)
        player_facing = mem.player.facing
        # Check position (must be in range, in a weak spot)
        if box.contains(weak_spot):
            if player_facing == facing_to_enemy:
                # We are aligned and in position. Attack!
                ctrl.dpad.none()
                ctrl.attack()
                return True
            else:  # Not currently facing the enemy. Turn towards enemy
                ctrl.dpad.none()
                match facing_to_enemy:
                    case Facing.UP:
                        ctrl.dpad.up()
                    case Facing.DOWN:
                        ctrl.dpad.down()
                    case Facing.LEFT:
                        ctrl.dpad.left()
                    case Facing.RIGHT:
                        ctrl.dpad.right()
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
            enemy_hitbox = get_box_with_size(
                center=enemy.pos, half_size=0.3
            )  # TODO: enemy collision magic number. Get bounding box?
            # Remove any weak points that fall inside the enemy hitbox
            attack_vectors = [
                wp for wp in attack_vectors if not enemy_hitbox.contains(wp)
            ]
        if len(attack_vectors) == 0:
            return False
        # Find the closest point to attack
        mem = get_zelda_memory()
        player_pos = mem.player.pos
        closest_weak_spot = find_closest_point(origin=player_pos, points=attack_vectors)
        # Move towards target weak point
        move_to(player=player_pos, target=closest_weak_spot, precision=self.precision)
        # Attempt to attack if in range
        return self._try_attack(target=target, weak_spot=closest_weak_spot)

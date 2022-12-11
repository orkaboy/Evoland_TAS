from control import evo_ctrl
from engine.combat import SeqArenaCombat
from engine.mathlib import Facing, Vec2, get_2d_facing_from_dir, get_box_with_size
from evo1.memory import Evo1GameEntity2D


class SeqKnight2D(SeqArenaCombat):
    def _get_attack_vectors(self, target: Evo1GameEntity2D) -> list[Vec2]:
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

    def _try_attack(self, target: Evo1GameEntity2D, weak_spot: Vec2) -> bool:
        ctrl = evo_ctrl()
        mem = self.zelda_mem()
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

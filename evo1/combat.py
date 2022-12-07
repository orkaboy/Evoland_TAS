import contextlib
import logging
import math
from typing import List, Optional

from engine.mathlib import Facing, Vec2, Box2, get_box_with_size, grow_box, get_2d_facing_from_dir, dist, angle_between
from evo1.memory import GameEntity2D, ZeldaMemory, get_zelda_memory
from evo1.move2d import SeqSection2D, move_to
import evo1.control
from term.window import WindowLayout, SubWindow

logger = logging.getLogger(__name__)


class CombatPlan:
    def __init__(self, mem: ZeldaMemory, arena: Box2, num_targets: int) -> None:
        self.targets: List[GameEntity2D] = []
        self.next_target: Optional[GameEntity2D] = None
        # Map start positions to array of GameEntity2D to track
        with contextlib.suppress(
                ReferenceError
            ):  # Needed until I figure out which enemies are valid (broken pointers will throw an exception)
            for actor in mem.actors:
                if actor.kind != GameEntity2D.EKind.ENEMY:
                    continue
                enemy_pos = actor.pos
                # Check if target is found. If so, initialize the tracking entity
                if arena.contains(enemy_pos):
                    self.targets.append(actor)
        if num_targets != len(self.targets):
            logger.error(f"Couldn't track all entities! Found {len(self.targets)}/{num_targets} enemies")

    def done(self) -> bool:
        return len(self.targets) == 0

    def get_next_target(self) -> Optional[GameEntity2D]:
        if self.next_target:
            return self.next_target

        mem = get_zelda_memory()
        player_pos = mem.player.pos
        # Using key sorting, order by closest target to player
        key_list = [(dist(player_pos, target.pos), target) for target in self.targets]
        sorted_list = sorted(key_list)
        if sorted_list:
            self.next_target = sorted_list[0][1]
            return self.next_target
        else:
            return None

    def remove_dead(self) -> None:
        self.targets = [enemy for enemy in self.targets if enemy.hp > 0]
        if self.next_target not in self.targets:
            self.next_target = None

    def enemies_left(self) -> int:
        return len(self.targets)


def find_closest_point(origin: Vec2, points: List[Vec2]) -> Vec2:
    closest_point = None
    closest_dist = 999
    for point in points:
        dist_to_point = dist(origin, point)
        if dist_to_point < closest_dist:
            closest_dist = dist_to_point
            closest_point = point
    return closest_point


# Base class for combat. Mostly handles target selection and rendering
class SeqCombat(SeqSection2D):
    def __init__(self, name: str, arena: Box2, num_targets: int, precision: float = 0.2) -> None:
        self.plan = None
        self.arena = arena
        self.precision = precision
        self.num_targets = num_targets
        super().__init__(name)

    def reset(self) -> None:
        self.plan = None

    # Should be overloaded by inherited classes
    def try_move_into_position_and_attack(self, target: GameEntity2D) -> bool:
        return True

    def execute(self, delta: float) -> bool:
        mem = get_zelda_memory()

        if self.plan is None:
            self.plan = CombatPlan(mem=mem, arena=self.arena, num_targets=self.num_targets)

        with contextlib.suppress(
            ReferenceError
        ):  # Needed until I figure out which enemies are valid (broken pointers will throw an exception)
            # TODO Track decisions, so we are not being wishy-washy
            target = self.plan.get_next_target()

            if target:
                self.try_move_into_position_and_attack(target=target)
            # for target in self.plan.targets:
            #     if self.try_move_into_position_and_attack(target=target):
            #         continue

        # Remove dead enemies from tracking
        self.plan.remove_dead()

        # We are done if all enemies are dead
        if self.plan.done():
            logger.info(f"Finished battle section: {self.name}")
            return True
        return False

    def render(self, window: WindowLayout) -> None:
        # Update stats window
        super().render(window=window)
        self._print_arena(map_win=window.map)
        self._print_actors(map_win=window.map)

    def _print_arena(self, map_win: SubWindow) -> None:
        # Draw a box representing the arena on the map. The representation is one tile
        # bigger so no entities inside the actual arena are overwritten.
        mem = get_zelda_memory()
        center = mem.player.pos

        arena_borders = grow_box(self.arena, 1)
        # Print corners
        self._print_ch_in_map(map_win=map_win, pos=arena_borders.tl()-center, ch="+")
        self._print_ch_in_map(map_win=map_win, pos=arena_borders.tr()-center, ch="+")
        self._print_ch_in_map(map_win=map_win, pos=arena_borders.bl()-center, ch="+")
        self._print_ch_in_map(map_win=map_win, pos=arena_borders.br()-center, ch="+")
        # Print horizontal sections
        for x in range(arena_borders.pos.x+1, arena_borders.pos.x+arena_borders.w):
            self._print_ch_in_map(map_win=map_win, pos=Vec2(x, arena_borders.pos.y)-center, ch="-")
            self._print_ch_in_map(map_win=map_win, pos=Vec2(x, arena_borders.bl().y)-center, ch="-")
        # Print vertical sections
        for y in range(arena_borders.pos.y+1, arena_borders.pos.y+arena_borders.h):
            self._print_ch_in_map(map_win=map_win, pos=Vec2(arena_borders.pos.x, y)-center, ch="|")
            self._print_ch_in_map(map_win=map_win, pos=Vec2(arena_borders.tr().x, y)-center, ch="|")

    def __repr__(self) -> str:
        dead_targets = self.num_targets - self.plan.enemies_left() if self.plan else 0
        tracking = f" Tracking: {self.plan.targets}" if self.plan else ""
        return f"{self.name}[{dead_targets}/{self.num_targets}] in arena: {self.arena}.{tracking}"


# TODO: WIP base
# TODO: This class can be used as the base of 3D combat, both for killing bats, skeletons/mages and even Dark Clink
class SeqCombat3D(SeqCombat):

    # TODO: Implement combat using rotation instead of facing
    # TODO: This isn't going to work for the skeletons (need to attack them from the sides/behind, just like the knights)
    def _get_attack_vectors(self, target: GameEntity2D) -> List[Vec2]:
        mem = get_zelda_memory()
        player_pos = mem.player.pos
        enemy_pos = target.pos
        # Calculate direction from enemy to player
        direction = (player_pos - enemy_pos).normalized()
        # TODO: Make this more intelligent/give more options
        # For the time being, beeline for the enemy
        distance_to_enemy = 1.2 # TODO: Test if this is a good distance or if we should be closer/farther away
        attack_vector = enemy_pos + (direction * distance_to_enemy)
        return [attack_vector]

    # TODO: Implement combat using rotation instead of facing
    def _try_attack(self, target: GameEntity2D, weak_spot: Vec2) -> bool:
        ctrl = evo1.control.handle()
        mem = get_zelda_memory()
        player_pos = mem.player.pos
        box = get_box_with_size(center=player_pos, half_size=self.precision)
        # Check position (must be in range, in a weak spot)
        if box.contains(weak_spot):
            # Check angle to enemy
            enemy_pos = target.pos
            angle_to_enemy = (enemy_pos - player_pos).angle
            player_angle = mem.player.rotation
            # Compare player rotation to angle_to_enemy
            angle = angle_between(angle_to_enemy, player_angle)
            if angle < math.pi / 3: # Roughly turned in the right direction
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
                elif angle_to_enemy < -math.pi / 8 and angle_to_enemy > -5 * math.pi / 8:
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
        mem = get_zelda_memory()
        player_pos = mem.player.pos
        closest_weak_spot = find_closest_point(origin=player_pos, points=attack_vectors)
        # Move towards target weak point
        move_to(player=player_pos, target=closest_weak_spot, precision=self.precision)
        # Attempt to attack if in range
        return self._try_attack(target=target, weak_spot=closest_weak_spot)


class SeqKnight2D(SeqCombat):

    def _get_attack_vectors(self, target: GameEntity2D) -> List[Vec2]:
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
            enemy_pos - forward, # Behind enemy
            enemy_pos + right, # To the right of enemy
            enemy_pos - right, # To the left of enemy
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
            else: # Not currently facing the enemy. Turn towards enemy
                ctrl.dpad.none()
                match facing_to_enemy:
                    case Facing.UP: ctrl.dpad.up()
                    case Facing.DOWN: ctrl.dpad.down()
                    case Facing.LEFT: ctrl.dpad.left()
                    case Facing.RIGHT: ctrl.dpad.right()
                return False
        return False # Couldn't attack this target right now

    # TODO: Possibly refactor this so parts of it can be reused for SeqCombat3D
    def try_move_into_position_and_attack(self, target: GameEntity2D) -> bool:
        # Find all the ways that the knight is vulnerable
        attack_vectors = self._get_attack_vectors(target=target)
        # TODO: Filter out invalid positions due to pathing (blocked by terrain)
        # Filter out threatened positions so we don't walk into another enemy
        for enemy in self.plan.targets:
            # For each enemy get a hitbox around them
            enemy_hitbox = get_box_with_size(center=enemy.pos, half_size=0.3) # TODO: enemy collision magic number. Get bounding box?
            # Remove any weak points that fall inside the enemy hitbox
            attack_vectors = [wp for wp in attack_vectors if not enemy_hitbox.contains(wp)]
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


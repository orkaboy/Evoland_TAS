import math
import contextlib
import logging
from typing import List

import evo1.control
from engine.seq import SeqBase, SeqDelay
from evo1.memory import GameEntity2D, get_zelda_memory, get_memory, MapID
from term.window import WindowLayout, SubWindow
from engine.mathlib import Facing, facing_str, Vec2, is_close, dist, angle_between
from evo1.maps import CurrentTilemap

logger = logging.getLogger(__name__)


def move_to(player: Vec2, target: Vec2, precision: float) -> None:
    ctrl = evo1.control.handle()
    ctrl.dpad.none()
    # Very dumb
    diff = target - player
    controller_precision = (
        precision / 2
    )  # Need to get closer so that is_close() will trigger on diagonals
    # Left right
    if diff.x > controller_precision:
        ctrl.dpad.right()
    elif diff.x < -controller_precision:
        ctrl.dpad.left()
    # Up down
    if diff.y > controller_precision:
        ctrl.dpad.down()
    elif diff.y < -controller_precision:
        ctrl.dpad.up()


# TODO: Improve on class to be able to handle free move/3d
class SeqGrabChest(SeqBase):
    def __init__(self, name: str, direction: Facing):
        self.dir = direction
        self.tapped = False
        super().__init__(name)

    def reset(self) -> None:
        self.tapped = False

    def execute(self, delta: float) -> bool:
        if not self.tapped:
            logger.info(f"Picking up {self.name}!")
            self.tapped = True
            ctrl = evo1.control.handle()
            match self.dir:
                case Facing.LEFT:
                    ctrl.dpad.tap_left()
                case Facing.RIGHT:
                    ctrl.dpad.tap_right()
                case Facing.UP:
                    ctrl.dpad.tap_up()
                case Facing.DOWN:
                    ctrl.dpad.tap_down()
        # Wait out any cutscene/pickup animation
        mem = get_zelda_memory()
        return mem.player.in_control

    def __repr__(self) -> str:
        return f"Chest({self.name})... awaiting control"


# TODO: Improve on class to be able to handle free move/3D
class SeqGrabChestKeyItem(SeqBase):
    def __init__(self, name: str, direction: Facing):
        self.dir = direction
        self.grabbed = False
        super().__init__(name)

    def reset(self) -> None:
        self.grabbed = False

    def execute(self, delta: float) -> bool:
        ctrl = evo1.control.handle()
        mem = get_zelda_memory()
        if not self.grabbed:
            ctrl.dpad.none()
            match self.dir:
                case Facing.LEFT:
                    ctrl.dpad.left()
                case Facing.RIGHT:
                    ctrl.dpad.right()
                case Facing.UP:
                    ctrl.dpad.up()
                case Facing.DOWN:
                    ctrl.dpad.down()
            if mem.player.not_in_control:
                logger.info(f"Picking up {self.name}!")
                self.grabbed = True
            return False
        # Tap past any popups
        ctrl.dpad.none()
        ctrl.confirm(tapping=True)
        # Wait out any cutscene/pickup animation
        return mem.player.in_control

    def __repr__(self) -> str:
        if self.grabbed:
            return f"Chest({self.name})... awaiting control"
        return f"Chest({self.name})... grabbing"


class SeqZoneTransition(SeqBase):
    def __init__(self, name: str, direction: Facing, target_zone: MapID):
        self.direction = direction
        self.target_zone = target_zone
        super().__init__(name)

    def execute(self, delta: float) -> bool:
        ctrl = evo1.control.handle()
        ctrl.dpad.none()
        match self.direction:
            case Facing.LEFT:
                ctrl.dpad.left()
            case Facing.RIGHT:
                ctrl.dpad.right()
            case Facing.UP:
                ctrl.dpad.up()
            case Facing.DOWN:
                ctrl.dpad.down()

        mem = get_memory()
        if mem.map_id == self.target_zone:
            ctrl.dpad.none()
            logger.info(f"Transitioned to zone: {self.target_zone.name}")
            return True
        return False

    def __repr__(self) -> str:
        return f"Transition to {self.name}, walking {facing_str(self.direction)}"


class SeqAttack(SeqBase):
    def __init__(self, name: str):
        super().__init__(name)

    def execute(self, delta: float) -> bool:
        ctrl = evo1.control.handle()
        ctrl.attack(tapping=False)
        # TODO: Await control?
        return True

    def __repr__(self) -> str:
        return f"Attack({self.name})"


# Temp testing
class SeqManualUntilClose(SeqBase):
    def __init__(self, name: str, target: Vec2, precision: float = 0.2, func=None):
        self.target = target
        self.precision = precision
        super().__init__(name, func)

    def execute(self, delta: float) -> bool:
        super().execute(delta)
        # Stay still
        ctrl = evo1.control.handle()
        ctrl.dpad.none()
        # Check if we have reached the goal
        mem = get_zelda_memory()
        player_pos = mem.player.pos
        return is_close(player_pos, self.target, precision=self.precision)

    def __repr__(self) -> str:
        return f"MANUAL CONTROL({self.name}) until reaching {self.target}"


class SeqHoldInPlace(SeqDelay):
    def __init__(self, name: str, target: Vec2, timeout_in_s: float, precision: float = 0.1):
        self.target = target
        self.precision = precision
        self.timer = 0
        super().__init__(name=name, timeout_in_s=timeout_in_s)

    def execute(self, delta: float) -> bool:
        mem = get_zelda_memory()
        player_pos = mem.player.pos
        # If arrived, go to next coordinate in the list
        if not is_close(player_pos, self.target, precision=self.precision):
            move_to(player=player_pos, target=self.target, precision=self.precision)
            return False
        # Stay still
        ctrl = evo1.control.handle()
        ctrl.dpad.none()
        # Wait for a while
        self.timer = self.timer + delta
        if self.timer >= self.timeout:
            self.timer = self.timeout
            return True
        return False

    def __repr__(self) -> str:
        return f"Waiting({self.name}) at {self.target}... {self.timer:.2f}/{self.timeout:.2f}"


# Base class for 2D movement areas
class SeqSection2D(SeqBase):
    def __init__(self, name: str, func=None):
        super().__init__(name, func=func)

    # Map starts at line 2 and fills the rest of the map window
    _map_start_y = 2

    def _print_player_stats(self, window: WindowLayout) -> None:
        window.stats.write_centered(line=1, text="Evoland 1 TAS")
        window.stats.write_centered(line=2, text="2D section")
        mem = get_zelda_memory()
        pos = mem.player.pos
        window.stats.addstr(Vec2(1, 4), f" Player X: {pos.x:.3f}")
        window.stats.addstr(Vec2(1, 5), f" Player Y: {pos.y:.3f}")
        window.stats.addstr(Vec2(1, 6), f"  Facing: {facing_str(mem.player.facing)}")
        # Draw the player at the center for reference
        self._print_ch_in_map(map_win=window.map, pos=Vec2(0, 0), ch="@")

    # (0,0) is at center of map. Y-axis increases going down the screen.
    def _print_ch_in_map(self, map_win: SubWindow, pos: Vec2, ch: str):
        size = map_win.size
        centerx, centery = size.x / 2, self._map_start_y + (size.y - self._map_start_y) / 2
        draw_x, draw_y = int(centerx + pos.x), int(centery + pos.y)
        with contextlib.suppress(Exception):
            if draw_x in range(size.x) and draw_y in range(self._map_start_y, size.y):
                map_win.addch(Vec2(draw_x, draw_y), ch)

    def _print_env(self, map_win: SubWindow) -> None:
        size = map_win.size
        # Fill box with .
        for y in range(self._map_start_y, size.y):
            map_win.hline(Vec2(0, y), " ", size.x)

    def _print_map(self, window: WindowLayout) -> None:
        if tilemap := CurrentTilemap():
            mem = get_zelda_memory()
            center = mem.player.pos
            # Render map
            window.map.write_centered(0, tilemap.name)
            for i, line in enumerate(tilemap.tiles):
                y_pos = i + tilemap.origin.y
                for j, tile in enumerate(line):
                    x_pos = j + tilemap.origin.x
                    draw_pos = Vec2(x_pos, y_pos) - center
                    self._print_ch_in_map(window.map, pos=draw_pos, ch=tile)

    def _print_actors(self, map_win: SubWindow) -> None:
        mem = get_zelda_memory()
        center = mem.player.pos

        with contextlib.suppress(
            ReferenceError
        ):  # Needed until I figure out which actors are valid (broken pointers will throw an exception)
            for actor in mem.actors:
                actor_kind = actor.kind
                match actor_kind:
                    case GameEntity2D.EKind.ENEMY: ch = "!"
                    case GameEntity2D.EKind.CHEST: ch = "C"
                    case GameEntity2D.EKind.ITEM: ch = "$"
                    case GameEntity2D.EKind.NPC: ch = "&"
                    case GameEntity2D.EKind.SPECIAL: ch = "*"
                    case _: ch = "?"
                actor_pos = actor.pos
                self._print_ch_in_map(map_win=map_win, pos=actor_pos-center, ch=ch)

    def render(self, window: WindowLayout) -> None:
        window.stats.erase()
        window.map.erase()
        self._print_env(map_win=window.map)
        self._print_map(window=window)
        self._print_player_stats(window=window)


class SeqMove2D(SeqSection2D):
    def __init__(self, name: str, coords: List[Vec2], precision: float = 0.2):
        self.step = 0
        self.coords = coords
        self.precision = precision
        super().__init__(name)

    def reset(self) -> None:
        self.step = 0

    def _nav_done(self) -> bool:
        num_coords = len(self.coords)
        # If we are already done with the entire sequence, terminate early
        return self.step >= num_coords

    def _navigate_to_checkpoint(self) -> None:
        # Move towards target
        if self.step >= len(self.coords):
            return
        target = self.coords[self.step]
        mem = get_zelda_memory()
        cur_pos = mem.player.pos

        move_to(player=cur_pos, target=target, precision=self.precision)

        # If arrived, go to next coordinate in the list
        if is_close(cur_pos, target, self.precision):
            logger.debug(
                f"Checkpoint reached {self.step}. Player: {cur_pos} Target: {target}"
            )
            self.step = self.step + 1

    def execute(self, delta: float) -> bool:
        self._navigate_to_checkpoint()

        done = self._nav_done()

        if done:
            logger.debug(f"Finished moved2D section: {self.name}")
        return done

    def _print_target(self, window: WindowLayout) -> None:
        num_coords = len(self.coords)
        if self.step >= num_coords:
            return

        target = self.coords[self.step]
        step = self.step + 1
        window.stats.write_centered(
            line=8, text=f"Moving to [{step}/{num_coords}]"
        )
        window.stats.addstr(Vec2(1, 9), f" Target X: {target.x:.3f}")
        window.stats.addstr(Vec2(1, 10), f" Target Y: {target.y:.3f}")

        # Draw target in relation to player
        mem = get_zelda_memory()
        center = mem.player.pos
        self._print_ch_in_map(map_win=window.map, pos=target-center, ch="X")

    def render(self, window: WindowLayout) -> None:
        # Update stats window
        super().render(window=window)
        self._print_target(window=window)
        self._print_actors(map_win=window.map)

    def __repr__(self) -> str:
        num_coords = len(self.coords)
        if self.step >= num_coords:
            return f"{self.name}[{num_coords}/{num_coords}]"
        target = self.coords[self.step]
        step = self.step + 1
        return f"{self.name}[{step}/{num_coords}]: {target}"


# Mash confirm while moving along a path
class SeqMove2DConfirm(SeqMove2D):
    def __init__(self, name: str, coords: List[Vec2], precision: float = 0.2):
        super().__init__(name, coords, precision)

    def execute(self, delta: float) -> bool:
        done = super().execute(delta=delta)
        ctrl = evo1.control.handle()
        ctrl.confirm(tapping=True)
        return done


class SeqMove2DClunkyCombat(SeqMove2D):
    def execute(self, delta: float) -> bool:
        self._navigate_to_checkpoint()

        target = self.coords[self.step] if self.step < len(self.coords) else self.coords[-1]
        self._clunky_combat2d(target=target)

        done = self._nav_done()

        if done:
            logger.debug(f"Finished moved2D section: {self.name}")
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
        mem = get_zelda_memory()
        player_pos = mem.player.pos
        player_angle = (target-player_pos).angle
        with contextlib.suppress(
            ReferenceError
        ):  # Needed until I figure out which enemies are valid (broken pointers will throw an exception)
            for actor in mem.actors:
                if actor.kind != GameEntity2D.EKind.ENEMY:
                    continue
                enemy_pos = actor.pos
                dist_to_player = dist(player_pos, enemy_pos)
                if dist_to_player < 1.5:  # TODO Arbitrary magic number, distance to enemy
                    enemy_angle = (enemy_pos-player_pos).angle
                    angle = angle_between(enemy_angle, player_angle)
                    # logger.debug(f"Enemy {i} dist: {dist_to_player}, angle_to_e: {enemy_angle}. angle: {angle}")
                    self._clunky_counter_with_sword(angle=angle, enemy_angle=enemy_angle)

    def _clunky_counter_with_sword(self, angle: float, enemy_angle: float) -> None:
        # If in front, attack!
        if abs(angle) < math.pi/4:  # TODO Arbitrary magic number, angle difference between where we are heading and where the enemy is
            ctrl = evo1.control.handle()
            ctrl.attack(tapping=False)
        elif abs(angle) <= math.pi/2:  # TODO On our sides
            ctrl = evo1.control.handle()
            ctrl.attack(tapping=False)
            ctrl.dpad.none()
            # Turn and attack (angle is in the range +PI to -PI, with 0 to our right)
            if abs(enemy_angle) < math.pi/4:
                ctrl.dpad.right()
            elif abs(enemy_angle) > 3*math.pi/4:
                ctrl.dpad.left()
            elif enemy_angle > 0:
                ctrl.dpad.down()
            else:
                ctrl.dpad.up()

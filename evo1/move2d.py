import contextlib
import logging
from typing import List

import evo1.control
from engine.seq import SeqBase
from engine.navmap import NavMap
from evo1.memory import GameFeatures, GameEntity2D, get_zelda_memory
from term.curses import WindowLayout
from engine.mathlib import Facing, facing_str, Vec2, is_close, dist, get_angle

logger = logging.getLogger(__name__)


def move_to(player: Vec2, target: Vec2, precision: float, blackboard: dict) -> None:
    # TODO: Different behavior depending on if certain game features are acquired
    features: GameFeatures = blackboard.get("features", {})
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


# TODO: Improve on class to be able to handle free move
class SeqGrabChest(SeqBase):
    def __init__(self, name: str, direction: Facing):
        self.dir = direction
        self.tapped = False
        super().__init__(name)

    def reset(self) -> None:
        self.tapped = False

    def execute(self, delta: float, blackboard: dict) -> bool:
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
        return not mem.player.get_inv_open()

    def __repr__(self) -> str:
        return f"Chest({self.name})... awaiting control"


class SeqZoneTransition(SeqBase):
    def __init__(self, name: str, direction: Facing, timeout_in_s: float):
        self.direction = direction
        self.timeout = timeout_in_s
        self.timer = 0
        super().__init__(name)

    def reset(self) -> None:
        self.timer = 0

    def execute(self, delta: float, blackboard: dict) -> bool:
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

        self.timer = self.timer + delta
        if self.timer >= self.timeout:
            self.timer = self.timeout
            ctrl.dpad.none()
            return True
        return False

    def __repr__(self) -> str:
        return f"Transition to {self.name}, walking {facing_str(self.direction)} for {self.timer:.2f}/{self.timeout:.2f}"

class SeqAttack(SeqBase):
    def __init__(self, name: str):
        super().__init__(name)

    def execute(self, delta: float, blackboard: dict) -> bool:
        ctrl = evo1.control.handle()
        ctrl.attack(tapping=False)
        # TODO: Await control?
        return True

    def __repr__(self) -> str:
        return f"Attack({self.name})"


# Base class for 2D movement areas
class SeqSection2D(SeqBase):

    def __init__(self, name: str, tilemap: NavMap = None, annotations: dict = None, func=None):
        self.tilemap = tilemap
        super().__init__(name, annotations=annotations, func=func)

    # Map starts at line 2 and fills the rest of the map window
    _map_start_y = 2

    def _print_player_stats(self, window: WindowLayout, blackboard: dict) -> None:
        window.write_stats_centered(line=1, text="Evoland 1 TAS")
        window.write_stats_centered(line=2, text="2D section")
        mem = get_zelda_memory()
        pos = mem.player.get_pos()
        window.stats.addstr(4, 1, f" Player X: {pos.x:.3f}")
        window.stats.addstr(5, 1, f" Player Y: {pos.y:.3f}")
        window.stats.addstr(6, 1, f"  Facing: {facing_str(mem.player.get_facing())}")
        # Draw the player at the center for reference
        self._print_ch_in_map(map_win=window.map, pos=Vec2(0, 0), ch="@")

    # (0,0) is at center of map. Y-axis increases going down the screen.
    def _print_ch_in_map(self, map_win, pos: Vec2, ch: str):
        maxy, maxx = map_win.getmaxyx()
        centerx, centery = maxx / 2, self._map_start_y + (maxy - self._map_start_y) / 2
        draw_x, draw_y = int(centerx + pos.x), int(centery + pos.y)
        with contextlib.suppress(Exception):
            if draw_x in range(maxx) and draw_y in range(self._map_start_y, maxy):
                map_win.addch(draw_y, draw_x, ch)

    def _print_env(self, map_win, blackboard: dict) -> None:
        maxy, maxx = map_win.getmaxyx()
        # Fill box with .
        for y in range(self._map_start_y, maxy):
            map_win.hline(y, 0, " ", maxx)

    def _print_map(self, window: WindowLayout, blackboard: dict) -> None:
        mem = get_zelda_memory()
        center = mem.player.get_pos()
        # Render map
        window.write_map_centered(0, self.tilemap.name)
        for i, line in enumerate(self.tilemap.tiles):
            y_pos = i + self.tilemap.origin.y
            for j, tile in enumerate(line):
                x_pos = j + self.tilemap.origin.x
                draw_pos = Vec2(x_pos, y_pos) - center
                self._print_ch_in_map(window.map, pos=draw_pos, ch=tile)

    def _print_actors(self, map_win, blackboard: dict) -> None:
        mem = get_zelda_memory()
        center = mem.player.get_pos()

        with contextlib.suppress(
            ReferenceError
        ):  # Needed until I figure out which actors are valid (broken pointers will throw an exception)
            for actor in mem.actors:
                actor_kind = actor.get_kind()
                match actor_kind:
                    case GameEntity2D.EKind.ENEMY: ch = "!"
                    case GameEntity2D.EKind.CHEST: ch = "C"
                    case GameEntity2D.EKind.ITEM: ch = "$"
                    case GameEntity2D.EKind.NPC: ch = "&"
                    case GameEntity2D.EKind.SPECIAL: ch = "*"
                    case _: ch = "?"
                actor_pos = actor.get_pos()
                self._print_ch_in_map(map_win=map_win, pos=actor_pos-center, ch=ch)

    def render(self, window: WindowLayout, blackboard: dict) -> None:
        window.stats.erase()
        window.map.erase()
        self._print_env(map_win=window.map, blackboard=blackboard)
        if self.tilemap:
            self._print_map(window=window, blackboard=blackboard)
        self._print_player_stats(window=window, blackboard=blackboard)


class SeqMove2D(SeqSection2D):
    def __init__(self, name: str, coords: List[Vec2], precision: float = 0.2, tilemap: NavMap = None):
        self.step = 0
        self.coords = coords
        self.precision = precision
        super().__init__(name, tilemap=tilemap)

    def reset(self) -> None:
        self.step = 0

    def _nav_done(self) -> bool:
        num_coords = len(self.coords)
        # If we are already done with the entire sequence, terminate early
        return self.step >= num_coords

    def _navigate_to_checkpoint(self, blackboard: dict) -> None:
        # Move towards target
        if self.step >= len(self.coords):
            return
        target = self.coords[self.step]
        mem = get_zelda_memory()
        cur_pos = mem.player.get_pos()

        move_to(player=cur_pos, target=target, precision=self.precision, blackboard=blackboard)

        # If arrived, go to next coordinate in the list
        if is_close(cur_pos, target, self.precision):
            logger.debug(
                f"Checkpoint reached {self.step}. Player: {cur_pos} Target: {target}"
            )
            self.step = self.step + 1

    def execute(self, delta: float, blackboard: dict) -> bool:
        self._navigate_to_checkpoint(blackboard=blackboard)

        done = self._nav_done()

        if done:
            logger.debug(f"Finished moved2D section: {self.name}")
        return done

    def _print_target(self, window: WindowLayout, blackboard: dict) -> None:
        num_coords = len(self.coords)
        if self.step >= num_coords:
            return

        target = self.coords[self.step]
        step = self.step + 1
        window.write_stats_centered(
            line=8, text=f"Moving to [{step}/{num_coords}]"
        )
        window.stats.addstr(9, 1, f" Target X: {target.x:.3f}")
        window.stats.addstr(10, 1, f" Target Y: {target.y:.3f}")

        # Draw target in relation to player
        mem = get_zelda_memory()
        center = mem.player.get_pos()
        self._print_ch_in_map(map_win=window.map, pos=target-center, ch="X")

    def render(self, window: WindowLayout, blackboard: dict) -> None:
        # Update stats window
        super().render(window=window, blackboard=blackboard)
        self._print_target(window=window, blackboard=blackboard)
        self._print_actors(map_win=window.map, blackboard=blackboard)

    def __repr__(self) -> str:
        num_coords = len(self.coords)
        if self.step >= num_coords:
            return f"{self.name}[{num_coords}/{num_coords}]"
        target = self.coords[self.step]
        step = self.step + 1
        return f"{self.name}[{step}/{num_coords}]: {target}"


class SeqMove2DClunkyCombat(SeqMove2D):
    def execute(self, delta: float, blackboard: dict) -> bool:
        self._navigate_to_checkpoint(blackboard=blackboard)

        target = self.coords[self.step] if self.step < len(self.coords) else self.coords[-1]
        self._clunky_combat2d(target=target, blackboard=blackboard)

        done = self._nav_done()

        if done:
            logger.debug(f"Finished moved2D section: {self.name}")
        return done

    # ============
    # = Algoritm =
    # ============
    # * Check where we are going in the next few steps (TODO: need to know player speed)
    # * Check where nearby enemies are, and which squares are threatened. Enemies has a threat of 1 in the current square they are in, 0.5 in adjacent (transferred over when moving)
    # * Adjacent threat is adjusted by timer
    # * Avoid moving into threatened squares
    # * Keep track on our weapon cooldown
    # * Keep track of our attack potential (stab hitbox is smaller than our hurtbox)
    # * The goal is not to kill the enemy, but to get past them!

    # TODO: Handle some edge cases, like when the enemy is at a diagonal, moving into the target space
    def _clunky_combat2d(self, target: Vec2, blackboard: dict) -> None:
        mem = get_zelda_memory()
        player_pos = mem.player.get_pos()
        player_angle = get_angle(target, player_pos)
        with contextlib.suppress(
            ReferenceError
        ):  # Needed until I figure out which enemies are valid (broken pointers will throw an exception)
            for actor in mem.actors:
                if actor.get_kind() != GameEntity2D.EKind.ENEMY:
                    continue
                enemy_pos = actor.get_pos()
                dist_to_player = dist(player_pos, enemy_pos)
                if dist_to_player < 1.5:  # TODO Arbitrary magic number, distance to enemy
                    enemy_angle = get_angle(enemy_pos, player_pos)
                    angle = enemy_angle - player_angle
                    # logger.debug(f"Enemy {i} dist: {dist_to_player}, angle_to_e: {enemy_angle}. angle: {angle}")
                    self._clunky_counter_with_sword(angle=angle, enemy_angle=enemy_angle)

    def _clunky_counter_with_sword(self, angle: float, enemy_angle: float) -> None:
        # If in front, attack!
        if abs(angle) < 0.7:  # TODO Arbitrary magic number, angle difference between where we are heading and where the enemy is
            ctrl = evo1.control.handle()
            ctrl.attack(tapping=False)
        elif abs(angle) <= 1.5:  # TODO On our sides
            ctrl = evo1.control.handle()
            ctrl.attack(tapping=False)
            ctrl.dpad.none()
            # Turn and attack
            if abs(enemy_angle) < 0.7:
                # logger.debug("Attacking right")
                ctrl.dpad.right()
            elif abs(enemy_angle) > 2:
                # logger.debug("Attacking left")
                ctrl.dpad.left()
            elif enemy_angle > 0:
                # logger.debug("Attacking down")
                ctrl.dpad.down()
            else:
                # logger.debug("Attacking up")
                ctrl.dpad.up()

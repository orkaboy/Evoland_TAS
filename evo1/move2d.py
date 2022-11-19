import contextlib
import logging
import math
from typing import List

import evo1.control
from engine.seq import SeqBase
from evo1.memory import Facing, GameFeatures, Vec2, get_zelda_memory
from term.curses import write_stats_centered

logger = logging.getLogger(__name__)


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


class SeqAttack(SeqBase):
    def __init__(self, name: str):
        super().__init__(name)

    def execute(self, delta: float, blackboard: dict) -> bool:
        ctrl = evo1.control.handle()
        ctrl.attack()
        # TODO: Await control?
        return True

    def __repr__(self) -> str:
        return f"Attack({self.name})"


def _get_angle(a: Vec2, b: Vec2) -> float:
    direction = Vec2(a.x - b.x, a.y - b.y)
    return math.atan2(direction.y, direction.x)


def _clunky_counter_with_sword(angle: float, enemy_angle: float) -> None:
    # If in front, attack!
    if abs(angle) < 0.7:  # TODO Arbitrary magic number
        ctrl = evo1.control.handle()
        ctrl.attack()
    elif abs(angle) <= 2:  # TODO On our side
        ctrl = evo1.control.handle()
        ctrl.attack()
        ctrl.set_neutral()
        # Turn and attack
        if abs(enemy_angle) < 0.7:
            ctrl.dpad.right()
        elif abs(enemy_angle) > 2:
            ctrl.dpad.left()
        elif enemy_angle > 0:
            ctrl.dpad.down()
        else:
            ctrl.dpad.up()


def clunky_combat2d(target: Vec2, blackboard: dict) -> None:
    mem = get_zelda_memory()
    player_pos = mem.player.get_pos()
    player_angle = _get_angle(target, player_pos)
    with contextlib.suppress(
        ReferenceError
    ):  # Needed until I figure out which enemies are valid
        for i, enemy in enumerate(mem.enemies):
            if not enemy.get_alive():
                continue
            enemy_pos = enemy.get_pos()
            dist_to_player = _dist(player_pos, enemy_pos)
            if dist_to_player < 1.5:  # TODO Arbitrary magic number, distance to enemy
                enemy_angle = _get_angle(enemy_pos, player_pos)
                angle = enemy_angle - player_angle
                # logger.debug(f"Enemy {i} dist: {dist_to_player}, angle_to_e: {enemy_angle}. angle: {angle}")
                _clunky_counter_with_sword(angle=angle, enemy_angle=enemy_angle)


def _dist(a: Vec2, b: Vec2) -> float:
    dx = b.x - a.x
    dy = b.y - a.y
    return math.sqrt(dx * dx + dy * dy)


def _is_close(player: Vec2, target: Vec2, precision: float) -> bool:
    return _dist(player, target) <= precision


class SeqMove2D(SeqBase):
    def __init__(self, name: str, coords: List[Vec2], precision: float = 0.2):
        self.step = 0
        self.coords = coords
        self.precision = precision
        super().__init__(name)

    def _move_to(self, player: Vec2, target: Vec2, blackboard: dict) -> None:
        ctrl = evo1.control.handle()
        features: GameFeatures = blackboard.get("features", {})
        combat_handler = blackboard.get("combat")
        # TODO: Different behavior depending on if certain game features are acquired
        ctrl.set_neutral()
        # Very dumb
        dx = target.x - player.x
        dy = target.y - player.y
        # Left right
        if dx > self.precision:
            ctrl.dpad.right()
        elif dx < -self.precision:
            ctrl.dpad.left()
        # Up down
        if dy > self.precision:
            ctrl.dpad.down()
        elif dy < -self.precision:
            ctrl.dpad.up()

        if combat_handler:
            combat_handler(target, blackboard)

    def execute(self, delta: float, blackboard: dict) -> bool:
        num_coords = len(self.coords)
        # If we are already done with the entire sequence, terminate early
        if self.step >= num_coords:
            return True
        # Move towards target
        target = self.coords[self.step]
        mem = get_zelda_memory()
        cur_pos = mem.player.get_pos()
        self._move_to(cur_pos, target, blackboard=blackboard)

        # If arrived, go to next coordinate in the list
        if _is_close(cur_pos, target, self.precision):
            self.step = self.step + 1

        return False

    def _print_player_stats(self, stats_win, blackboard: dict) -> None:
        write_stats_centered(stats_win=stats_win, line=1, text="Evoland 1 TAS")
        write_stats_centered(stats_win=stats_win, line=2, text="2D section")
        mem = get_zelda_memory()
        pos = mem.player.get_pos()
        stats_win.addstr(4, 1, f"  Player X: {pos.x:.3f}")
        stats_win.addstr(5, 1, f"  Player Y: {pos.y:.3f}")
        facing = mem.player.get_facing_str()
        stats_win.addstr(6, 1, f"    Facing: {facing}")

    def _print_target(self, stats_win, blackboard: dict) -> None:
        num_coords = len(self.coords)
        if self.step >= num_coords:
            return

        target = self.coords[self.step]
        step = self.step + 1
        write_stats_centered(
            stats_win=stats_win, line=8, text=f"Moving to [{step}/{num_coords}]"
        )
        stats_win.addstr(9, 1, f"  Target X: {target.x:.3f}")
        stats_win.addstr(10, 1, f"  Target Y: {target.y:.3f}")

    def render(self, main_win, stats_win, blackboard: dict) -> None:
        # Update stats window
        stats_win.erase()
        self._print_player_stats(stats_win=stats_win, blackboard=blackboard)
        self._print_target(stats_win=stats_win, blackboard=blackboard)

    def __repr__(self) -> str:
        num_coords = len(self.coords)
        if self.step >= num_coords:
            return f"{self.name}[{num_coords}/{num_coords}]"
        target = self.coords[self.step]
        step = self.step + 1
        return f"{self.name}[{step}/{num_coords}] > {target}"

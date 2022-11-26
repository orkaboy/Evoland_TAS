import contextlib
import logging
import math
import copy
from typing import List

import evo1.control
from engine.seq import SeqBase
from evo1.memory import Facing, facing_str, facing_ch, GameFeatures, Vec2, Box2, grow_box, GameEntity2D, ZeldaMemory, get_zelda_memory
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


class SeqZoneTransition(SeqBase):
    def __init__(self, name: str, direction: Facing, time_in_s: float):
        self.direction = direction
        self.timeout = time_in_s
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
        ctrl.attack()
        # TODO: Await control?
        return True

    def __repr__(self) -> str:
        return f"Attack({self.name})"


def _get_angle(a: Vec2, b: Vec2) -> float:
    direction = a - b
    return math.atan2(direction.y, direction.x)


def _clunky_counter_with_sword(angle: float, enemy_angle: float) -> None:
    # If in front, attack!
    if abs(angle) < 0.7:  # TODO Arbitrary magic number
        ctrl = evo1.control.handle()
        ctrl.attack()
    elif abs(angle) <= 2:  # TODO On our sides
        ctrl = evo1.control.handle()
        ctrl.attack()
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


def clunky_combat2d(target: Vec2, blackboard: dict) -> None:
    mem = get_zelda_memory()
    player_pos = mem.player.get_pos()
    player_angle = _get_angle(target, player_pos)
    with contextlib.suppress(
        ReferenceError
    ):  # Needed until I figure out which enemies are valid (broken pointers will throw an exception)
        for enemy in mem.enemies:
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


def _is_close(a: Vec2, b: Vec2, precision: float) -> bool:
    return _dist(a, b) <= precision


# Base class for 2D movement areas
class SeqSection2D(SeqBase):
    # Map starts at line 12 and fills the rest of the stats window
    _map_start_y = 12

    def _print_player_stats(self, stats_win, blackboard: dict) -> None:
        write_stats_centered(stats_win=stats_win, line=1, text="Evoland 1 TAS")
        write_stats_centered(stats_win=stats_win, line=2, text="2D section")
        mem = get_zelda_memory()
        pos = mem.player.get_pos()
        stats_win.addstr(4, 1, f" Player X: {pos.x:.3f}")
        stats_win.addstr(5, 1, f" Player Y: {pos.y:.3f}")
        stats_win.addstr(6, 1, f"  Facing: {facing_str(mem.player.get_facing())}")
        # Draw the player at the center for reference
        self._print_ch_in_map(stats_win=stats_win, pos=Vec2(0, 0), ch="@")

    # (0,0) is at center of map. Y-axis increases going down the screen.
    def _print_ch_in_map(self, stats_win, pos: Vec2, ch: str):
        maxy, maxx = stats_win.getmaxyx()
        centerx, centery = maxx / 2, self._map_start_y + (maxy - self._map_start_y) / 2
        draw_x, draw_y = int(centerx + pos.x), int(centery + pos.y)
        if draw_x in range(maxx) and draw_y in range(self._map_start_y, maxy - 1):
            stats_win.addch(draw_y, draw_x, ch)

    def _print_env(self, stats_win, blackboard: dict) -> None:
        maxy, maxx = stats_win.getmaxyx()
        # Fill box with .
        for y in range(self._map_start_y, maxy - 1):
            stats_win.hline(y, 0, ".", maxx)

    def _print_actors(self, stats_win, blackboard: dict) -> None:
        mem = get_zelda_memory()
        center = mem.player.get_pos()

        with contextlib.suppress(
            ReferenceError
        ):  # Needed until I figure out which enemies are valid (broken pointers will throw an exception)
            for enemy in mem.enemies:
                enemy_pos = enemy.get_pos()
                enemy_dir_ch = facing_ch(enemy.get_facing())
                self._print_ch_in_map(stats_win=stats_win, pos=enemy_pos-center, ch=enemy_dir_ch)

    def render(self, main_win, stats_win, blackboard: dict) -> None:
        stats_win.erase()
        self._print_env(stats_win=stats_win, blackboard=blackboard)
        self._print_player_stats(stats_win=stats_win, blackboard=blackboard)


class SeqMove2D(SeqSection2D):
    def __init__(self, name: str, coords: List[Vec2], precision: float = 0.2):
        self.step = 0
        self.coords = coords
        self.precision = precision
        super().__init__(name)

    def reset(self) -> None:
        self.step = 0

    def _move_to(self, player: Vec2, target: Vec2, blackboard: dict) -> None:
        ctrl = evo1.control.handle()
        features: GameFeatures = blackboard.get("features", {})
        combat_handler = blackboard.get("combat")
        # TODO: Different behavior depending on if certain game features are acquired
        ctrl.dpad.none()
        # Very dumb
        diff = target - player
        controller_precision = (
            self.precision / 2
        )  # Need to get closer so that _is_close() will trigger on diagonals
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

        # TODO: Need to handle this better, can't override gamepad all the time to do combat
        if combat_handler:
            combat_handler(target, blackboard)

    def execute(self, delta: float, blackboard: dict) -> bool:
        num_coords = len(self.coords)
        # If we are already done with the entire sequence, terminate early
        if self.step >= num_coords:
            logger.debug(f"Finished moved2D section: {self.name}")
            return True
        # Move towards target
        target = self.coords[self.step]
        mem = get_zelda_memory()
        cur_pos = mem.player.get_pos()
        self._move_to(cur_pos, target, blackboard=blackboard)

        # If arrived, go to next coordinate in the list
        if _is_close(cur_pos, target, self.precision):
            logger.debug(
                f"Checkpoint reached {self.step}. Player: {cur_pos} Target: {target}"
            )
            self.step = self.step + 1

        return False

    def _print_target(self, stats_win, blackboard: dict) -> None:
        num_coords = len(self.coords)
        if self.step >= num_coords:
            return

        target = self.coords[self.step]
        step = self.step + 1
        write_stats_centered(
            stats_win=stats_win, line=8, text=f"Moving to [{step}/{num_coords}]"
        )
        stats_win.addstr(9, 1, f" Target X: {target.x:.3f}")
        stats_win.addstr(10, 1, f" Target Y: {target.y:.3f}")

        # Draw target in relation to player
        mem = get_zelda_memory()
        center = mem.player.get_pos()
        self._print_ch_in_map(stats_win=stats_win, pos=target-center, ch="X")

    def render(self, main_win, stats_win, blackboard: dict) -> None:
        # Update stats window
        super().render(main_win=main_win, stats_win=stats_win, blackboard=blackboard)
        self._print_target(stats_win=stats_win, blackboard=blackboard)
        self._print_actors(stats_win=stats_win, blackboard=blackboard)

    def __repr__(self) -> str:
        num_coords = len(self.coords)
        if self.step >= num_coords:
            return f"{self.name}[{num_coords}/{num_coords}]"
        target = self.coords[self.step]
        step = self.step + 1
        return f"{self.name}[{step}/{num_coords}]: {target}"


def _get_tracker(last_pos: Vec2, movement: float) -> Box2:
    return Box2(pos=Vec2(last_pos.x - movement, last_pos.y - movement), w=2*movement, h=2*movement)

class SeqKnight2D(SeqSection2D):

    class _Plan:
        def __init__(self, mem: ZeldaMemory, targets: List[Vec2], track_size: float):
            self.targets: List[GameEntity2D] = []
            targets_copy = targets.copy()
            with contextlib.suppress(
                    ReferenceError
                ):  # Needed until I figure out which enemies are valid (broken pointers will throw an exception)
                for enemy in mem.enemies:
                    enemy_pos = enemy.get_pos()
                    search_box = _get_tracker(last_pos=enemy_pos, movement=track_size)
                    for target in targets_copy:
                        # Check if target is found. If so, initialize the tracking entity
                        if search_box.contains(target):
                            self.targets.append(enemy)
            # TODO Track decisions
            if len(targets) != len(self.targets):
                logger.error(f"Couldn't track all entities! Found {len(self.targets)}/{len(targets)} enemies")

        def done(self) -> bool:
            return len(self.targets) == 0

        def remove_dead(self) -> None:
            self.targets = [enemy for enemy in self.targets if enemy.get_hp() > 0]

        def enemies_left(self) -> int:
            return len(self.targets)

    # TODO: Change List[Vec2] to some kind of ID or monster structure instead to make tracking easier
    def __init__(self, name: str, arena: Box2, targets: List[Vec2], track_size: float = 0.2):
        self.plan = None
        self.arena = arena
        self.target_coords = targets
        self.track_size = track_size
        self.num_targets = len(targets)
        super().__init__(name)

    def reset(self):
        self.plan = None

    def execute(self, delta: float, blackboard: dict) -> bool:
        mem = get_zelda_memory()
        player_pos = mem.player.get_pos()

        if self.plan is None:
            self.plan = SeqKnight2D._Plan(mem=mem, targets=self.target_coords, track_size=self.track_size)

        # TODO: Move
        ctrl = evo1.control.handle()
        ctrl.dpad.none()

        # TODO: Should reuse the stuff from move2d or refactor out?
        with contextlib.suppress(
            ReferenceError
        ):  # Needed until I figure out which enemies are valid (broken pointers will throw an exception)
            for target in self.plan.targets:
                pass
                # TODO: need to deal with enemies dying

        # Remove dead enemies from tracking
        self.plan.remove_dead()

        # We are done if all enemies are dead
        if self.plan.done():
            logger.info(f"Finished knight battle section: {self.name}")
            return True
        return False

    def render(self, main_win, stats_win, blackboard: dict) -> None:
        # Update stats window
        super().render(main_win=main_win, stats_win=stats_win, blackboard=blackboard)
        self._print_arena(stats_win=stats_win, blackboard=blackboard)
        self._print_actors(stats_win=stats_win, blackboard=blackboard)

    def _print_arena(self, stats_win, blackboard: dict) -> None:
        # Draw a box representing the arena on the map. The representation is one tile
        # bigger so no entities inside the actual arena are overwritten.
        mem = get_zelda_memory()
        center = mem.player.get_pos()

        arena_borders = grow_box(self.arena, 1)
        # Print corners
        self._print_ch_in_map(stats_win=stats_win, pos=arena_borders.tl()-center, ch="+")
        self._print_ch_in_map(stats_win=stats_win, pos=arena_borders.tr()-center, ch="+")
        self._print_ch_in_map(stats_win=stats_win, pos=arena_borders.bl()-center, ch="+")
        self._print_ch_in_map(stats_win=stats_win, pos=arena_borders.br()-center, ch="+")
        # Print horizontal sections
        for x in range(arena_borders.pos.x+1, arena_borders.pos.x+arena_borders.w):
            self._print_ch_in_map(stats_win=stats_win, pos=Vec2(x, arena_borders.pos.y)-center, ch="-")
            self._print_ch_in_map(stats_win=stats_win, pos=Vec2(x, arena_borders.bl().y)-center, ch="-")
        # Print vertical sections
        for y in range(arena_borders.pos.y+1, arena_borders.pos.y+arena_borders.h):
            self._print_ch_in_map(stats_win=stats_win, pos=Vec2(arena_borders.pos.x, y)-center, ch="|")
            self._print_ch_in_map(stats_win=stats_win, pos=Vec2(arena_borders.tr().x, y)-center, ch="|")


    def __repr__(self) -> str:
        dead_targets = self.num_targets - self.plan.enemies_left() if self.plan else 0
        tracking = f" Tracking: {self.plan.targets}" if self.plan else ""
        return f"{self.name}[{dead_targets}/{self.num_targets}] in arena: {self.arena}.{tracking}"


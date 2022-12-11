import contextlib
import logging

from control import evo_ctrl
from engine.mathlib import Vec2, is_close
from engine.seq import SeqBase
from evo2.memory import get_zelda_memory
from term.window import SubWindow, WindowLayout

logger = logging.getLogger(__name__)


def move_to(player: Vec2, target: Vec2, precision: float) -> None:
    ctrl = evo_ctrl()
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


# TODO: Overlap with Evo1 code
# Base class for 2D movement areas
class SeqSection2D(SeqBase):
    def __init__(self, name: str, func=None):
        super().__init__(name, func=func)

    # Map starts at line 2 and fills the rest of the map window
    _map_start_y = 2

    def _print_player_stats(self, window: WindowLayout) -> None:
        window.stats.write_centered(line=1, text="Evoland 2 TAS")
        window.stats.write_centered(line=2, text="2D section")
        mem = get_zelda_memory()
        pos = mem.player.pos
        window.stats.addstr(Vec2(1, 4), f" Player X: {pos.x:.3f}")
        window.stats.addstr(Vec2(1, 5), f" Player Y: {pos.y:.3f}")
        window.stats.addstr(Vec2(1, 6), f"  Rot: {mem.player.rotation:.2f}")
        # Draw the player at the center for reference
        self._print_ch_in_map(map_win=window.map, pos=Vec2(0, 0), ch="@")

    # (0,0) is at center of map. Y-axis increases going down the screen.
    def _print_ch_in_map(self, map_win: SubWindow, pos: Vec2, ch: str):
        size = map_win.size
        centerx, centery = (
            size.x / 2,
            self._map_start_y + (size.y - self._map_start_y) / 2,
        )
        draw_x, draw_y = int(centerx + pos.x), int(centery + pos.y)
        with contextlib.suppress(Exception):
            if draw_x in range(size.x) and draw_y in range(self._map_start_y, size.y):
                map_win.addch(Vec2(draw_x, draw_y), ch)

    def _print_env(self, map_win: SubWindow) -> None:
        size = map_win.size
        # Fill box with .
        for y in range(self._map_start_y, size.y):
            map_win.hline(Vec2(0, y), " ", size.x)

    # TODO:
    # def _print_map(self, window: WindowLayout) -> None:
    #     if tilemap := CurrentTilemap():
    #         mem = get_zelda_memory()
    #         center = mem.player.pos
    #         # Render map
    #         window.map.write_centered(0, tilemap.name)
    #         for i, line in enumerate(tilemap.tiles):
    #             y_pos = i + tilemap.origin.y
    #             for j, tile in enumerate(line):
    #                 x_pos = j + tilemap.origin.x
    #                 draw_pos = Vec2(x_pos, y_pos) - center
    #                 self._print_ch_in_map(window.map, pos=draw_pos, ch=tile)

    def _print_actors(self, map_win: SubWindow) -> None:
        mem = get_zelda_memory()
        center = mem.player.pos

        # Needed until I figure out which actors are valid (broken pointers will throw an exception)
        with contextlib.suppress(ReferenceError):
            for actor in mem.actors:
                ch = "?"
                # TODO:
                # actor_kind = actor.kind
                # match actor_kind:
                #     case GameEntity2D.EKind.ENEMY:
                #         ch = "!"
                #     case GameEntity2D.EKind.CHEST:
                #         ch = "C"
                #     case GameEntity2D.EKind.ITEM:
                #         ch = "$"
                #     case GameEntity2D.EKind.NPC:
                #         ch = "&"
                #     case GameEntity2D.EKind.SPECIAL:
                #         ch = "*"
                #     case _:
                #         ch = "?"

                actor_pos = actor.pos
                self._print_ch_in_map(map_win=map_win, pos=actor_pos - center, ch=ch)

    def render(self, window: WindowLayout) -> None:
        window.stats.erase()
        window.map.erase()
        self._print_env(map_win=window.map)
        # TODO:
        # self._print_map(window=window)
        self._print_player_stats(window=window)


# TODO Massive overlap with Evo1 code
class SeqMove2D(SeqSection2D):
    def __init__(
        self, name: str, coords: list[Vec2], precision: float = 0.2, func=None
    ):
        self.step = 0
        self.coords = coords
        self.precision = precision
        super().__init__(name, func=func)

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
            logger.info(f"Finished moved2D section: {self.name}")
        return done

    def _print_target(self, window: WindowLayout) -> None:
        num_coords = len(self.coords)
        if self.step >= num_coords:
            return

        target = self.coords[self.step]
        step = self.step + 1
        window.stats.write_centered(line=8, text=f"Moving to [{step}/{num_coords}]")
        window.stats.addstr(Vec2(1, 9), f" Target X: {target.x:.3f}")
        window.stats.addstr(Vec2(1, 10), f" Target Y: {target.y:.3f}")

        # Draw target in relation to player
        mem = get_zelda_memory()
        center = mem.player.pos
        self._print_ch_in_map(map_win=window.map, pos=target - center, ch="X")

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


# TODO: Overlap with Evo1
# Mash confirm while moving along a path (to get past talk triggers)
class SeqMove2DConfirm(SeqMove2D):
    def __init__(self, name: str, coords: list[Vec2], precision: float = 0.2):
        super().__init__(name, coords, precision)

    def execute(self, delta: float) -> bool:
        done = super().execute(delta=delta)
        mem = get_zelda_memory()
        if mem.player.not_in_control:
            ctrl = evo_ctrl()
            ctrl.confirm(tapping=True)
        return done

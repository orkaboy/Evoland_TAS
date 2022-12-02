import contextlib
import logging
from typing import List

from engine.mathlib import Vec2, Box2, grow_box
from engine.navmap import NavMap
from evo1.memory import GameEntity2D, ZeldaMemory, get_zelda_memory
from evo1.move2d import SeqSection2D
import evo1.control
from term.curses import WindowLayout

logger = logging.getLogger(__name__)


def _get_tracker(last_pos: Vec2, movement: float) -> Box2:
    return Box2(pos=Vec2(last_pos.x - movement, last_pos.y - movement), w=2*movement, h=2*movement)

class SeqKnight2D(SeqSection2D):

    class _Plan:
        def __init__(self, mem: ZeldaMemory, targets: List[Vec2], track_size: float):
            self.targets: List[GameEntity2D] = []
            targets_copy = targets.copy()
            # Map start positions to array of GameEntity2D to track
            with contextlib.suppress(
                    ReferenceError
                ):  # Needed until I figure out which enemies are valid (broken pointers will throw an exception)
                for actor in mem.actors:
                    if actor.get_kind() != GameEntity2D.EKind.ENEMY:
                        continue
                    enemy_pos = actor.get_pos()
                    search_box = _get_tracker(last_pos=enemy_pos, movement=track_size)
                    for target in targets_copy:
                        # Check if target is found. If so, initialize the tracking entity
                        if search_box.contains(target):
                            self.targets.append(actor)
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
    def __init__(self, name: str, arena: Box2, targets: List[Vec2], track_size: float = 0.2, tilemap: NavMap = None):
        self.plan = None
        self.arena = arena
        self.target_coords = targets
        self.track_size = track_size
        self.num_targets = len(targets)
        super().__init__(name, tilemap=tilemap)

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

        # Remove dead enemies from tracking
        self.plan.remove_dead()

        # We are done if all enemies are dead
        if self.plan.done():
            logger.info(f"Finished knight battle section: {self.name}")
            return True
        return False

    def render(self, window: WindowLayout, blackboard: dict) -> None:
        # Update stats window
        super().render(window=window, blackboard=blackboard)
        self._print_arena(map_win=window.map, blackboard=blackboard)
        self._print_actors(map_win=window.map, blackboard=blackboard)

    def _print_arena(self, map_win, blackboard: dict) -> None:
        # Draw a box representing the arena on the map. The representation is one tile
        # bigger so no entities inside the actual arena are overwritten.
        mem = get_zelda_memory()
        center = mem.player.get_pos()

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


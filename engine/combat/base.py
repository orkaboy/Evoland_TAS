import contextlib
import logging

from engine.combat.plan import CombatPlan
from engine.mathlib import Box2, Vec2, grow_box
from engine.move2d import SeqSection2D
from memory.zelda_base import GameEntity2D
from term.window import SubWindow, WindowLayout

logger = logging.getLogger(__name__)


# Base class for combat. Mostly handles target selection and rendering
class SeqCombat(SeqSection2D):
    MIN_DISTANCE = 1.2

    def __init__(
        self,
        name: str,
        arena: Box2,
        num_targets: int,
        precision: float = 0.2,
        retracking: bool = False,
        func=None,
    ) -> None:
        self.plan = None
        self.arena = arena
        self.precision = precision
        self.retracking = retracking
        self.num_targets = num_targets
        super().__init__(name, func)

    def reset(self) -> None:
        self.plan = None

    # Should be overloaded by inherited classes
    def try_move_into_position_and_attack(self, target: GameEntity2D) -> bool:
        return True

    def execute(self, delta: float) -> bool:
        super().execute(delta=delta)
        if self.plan is None:
            self.plan = CombatPlan(
                arena=self.arena,
                num_targets=self.num_targets,
                retracking=self.retracking,
            )

        # Needed until I figure out which enemies are valid (broken pointers will throw an exception)
        with contextlib.suppress(ReferenceError):
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
            # logger.info(f"Finished battle section: {self.name}")
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
        mem = self.zelda_mem()
        center = mem.player.pos

        arena_borders = grow_box(self.arena, 1)
        # Print corners
        self._print_ch_in_map(map_win=map_win, pos=arena_borders.tl() - center, ch="+")
        self._print_ch_in_map(map_win=map_win, pos=arena_borders.tr() - center, ch="+")
        self._print_ch_in_map(map_win=map_win, pos=arena_borders.bl() - center, ch="+")
        self._print_ch_in_map(map_win=map_win, pos=arena_borders.br() - center, ch="+")
        # Print horizontal sections
        for x in range(arena_borders.pos.x + 1, arena_borders.pos.x + arena_borders.w):
            self._print_ch_in_map(
                map_win=map_win, pos=Vec2(x, arena_borders.pos.y) - center, ch="-"
            )
            self._print_ch_in_map(
                map_win=map_win, pos=Vec2(x, arena_borders.bl().y) - center, ch="-"
            )
        # Print vertical sections
        for y in range(arena_borders.pos.y + 1, arena_borders.pos.y + arena_borders.h):
            self._print_ch_in_map(
                map_win=map_win, pos=Vec2(arena_borders.pos.x, y) - center, ch="|"
            )
            self._print_ch_in_map(
                map_win=map_win, pos=Vec2(arena_borders.tr().x, y) - center, ch="|"
            )

    def __repr__(self) -> str:
        dead_targets = self.num_targets - self.plan.enemies_left() if self.plan else 0
        tracking = f" Tracking: {self.plan.targets}" if self.plan else ""
        return f"{self.name}[{dead_targets}/{self.num_targets}] in arena: {self.arena}.{tracking}"

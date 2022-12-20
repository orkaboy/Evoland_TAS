import contextlib
import itertools
from typing import Optional

from control import evo_ctrl
from engine.combat import SeqCombat3D, SeqMove2DClunkyCombat
from engine.mathlib import Box2, Facing, Vec2, get_box_with_size
from engine.move2d import (
    SeqGrabChest,
    SeqGrabChestKeyItem,
    SeqHoldInPlace,
    SeqManualUntilClose,
    SeqMove2D,
    SeqMove2DCancel,
    SeqSection2D,
    move_to,
)
from engine.seq import SeqAttack, SeqDelay, SeqList, SeqMenu
from evo1.move2d import SeqZoneTransition
from maps.evo1 import GetAStar, GetTilemap
from memory.evo1 import Evo1GameEntity2D, MapID, get_zelda_memory

_noria_astar = GetAStar(MapID.NORIA)
_noria_start_astar = GetAStar(MapID.NORIA_CLOSED)


# TODO: Improve on the chest grab to be more concise (don't require the approach)
class NoriaToMaze(SeqList):
    """Handle the entire first sequence of the Noria Mines, from entry to the start of the first maze."""

    def __init__(self):
        super().__init__(
            name="Navigate to maze",
            children=[
                SeqMove2D(
                    "Move to chest",
                    coords=_noria_start_astar.calculate(
                        start=Vec2(47, 67), goal=Vec2(46, 56), final_pos=Vec2(46, 55.6)
                    ),
                ),
                SeqGrabChest("Opening the mines", direction=Facing.UP),
                SeqMove2DClunkyCombat(
                    "Move to chest",
                    coords=_noria_astar.calculate(
                        start=Vec2(46, 55), goal=Vec2(51, 48), final_pos=Vec2(51, 47.6)
                    ),
                ),
                SeqGrabChest("Breakable pots", direction=Facing.UP),
                SeqMove2DClunkyCombat(
                    "Move to chest",
                    coords=_noria_astar.calculate(
                        start=Vec2(51, 47), goal=Vec2(54, 40), final_pos=Vec2(54, 39.6)
                    ),
                ),
                SeqGrabChest("Pressure plates", direction=Facing.UP),
                SeqMove2DClunkyCombat(
                    "Trigger plate(R)",
                    coords=_noria_astar.calculate(
                        start=Vec2(54, 39), goal=Vec2(58, 37)
                    ),
                ),
                SeqHoldInPlace(
                    name="Trigger plate(R)", target=Vec2(58, 37), timeout_in_s=0.5
                ),
                SeqMove2DClunkyCombat(
                    "Trigger plate(L)",
                    coords=_noria_astar.calculate(
                        start=Vec2(58, 37), goal=Vec2(50, 37)
                    ),
                    precision=0.1,
                ),
                SeqMenu("Menu manip"),
                SeqDelay(name="Trigger plate(L)", timeout_in_s=1.5),
                SeqMenu("Menu manip"),
                # TODO: Full menu glitch (important)
                SeqMove2DClunkyCombat(
                    "Move to chest",
                    coords=_noria_astar.calculate(
                        start=Vec2(50, 37), goal=Vec2(48, 45), final_pos=Vec2(48, 44.6)
                    ),
                ),
                SeqGrabChest("Red Mage", direction=Facing.UP),
                SeqMove2DClunkyCombat(
                    "Move to chest",
                    coords=_noria_astar.calculate(
                        start=Vec2(48, 44), goal=Vec2(35, 41), final_pos=Vec2(35, 40.6)
                    ),
                ),
                # TODO: Trigger menu glitch to get two keys
                SeqGrabChest("Trap room", direction=Facing.UP),
                SeqCombat3D(
                    "Killing bats",
                    arena=Box2(Vec2(32, 40), w=8, h=8),
                    num_targets=3,
                    retracking=True,
                ),
                SeqMove2DClunkyCombat("Move to chest", coords=[Vec2(34, 41)]),
                # Get in position for chest
                SeqMove2D("Move to chest", coords=[Vec2(33.6, 41)]),
                SeqGrabChest("Key", direction=Facing.LEFT),
                SeqMove2DClunkyCombat(
                    "Move to door",
                    coords=_noria_astar.calculate(
                        start=Vec2(37, 44), goal=Vec2(41, 42)
                    ),
                ),
                # TODO: Open door(N)
                SeqMove2DClunkyCombat(
                    "Move to chest",
                    coords=_noria_astar.calculate(
                        start=Vec2(41, 41), goal=Vec2(41, 40), final_pos=Vec2(41, 39.6)
                    ),
                ),
                SeqGrabChest("Skellies", direction=Facing.UP),
                # Skip past first skeleton
                SeqMove2DCancel(
                    "Move to trigger",
                    coords=_noria_astar.calculate(
                        start=Vec2(41, 40), goal=Vec2(30, 40)
                    ),
                ),
                # TODO: Deal with mage enemy here?
                SeqMove2DClunkyCombat(
                    "Trigger plate",
                    coords=_noria_astar.calculate(
                        start=Vec2(30, 39), goal=Vec2(27, 42)
                    ),
                ),
                SeqMenu("Menu manip"),
                SeqDelay(name="Trigger plate", timeout_in_s=0.5),
                SeqMenu("Menu manip"),
                SeqMove2D(name="Menu manip", coords=[Vec2(28.5, 43)]),
                SeqMenu("Menu manip"),
                SeqMove2DClunkyCombat(
                    "Move to chest",
                    coords=_noria_astar.calculate(
                        start=Vec2(29, 43), goal=Vec2(22, 40), final_pos=Vec2(22, 39.6)
                    ),
                ),
                SeqGrabChest("Maze", direction=Facing.UP),
            ],
        )


class NoriaMazeAndBlocks(SeqList):
    """Handle movement through the various mazes."""

    def __init__(self):
        super().__init__(
            name="Maze and blocks",
            children=[
                SeqMove2DClunkyCombat(
                    "Maze",
                    coords=_noria_astar.calculate(
                        start=Vec2(22, 39), goal=Vec2(27, 24), final_pos=Vec2(27, 23.6)
                    ),
                ),
                SeqGrabChestKeyItem("Key", direction=Facing.UP, manip=True),
                SeqMove2DClunkyCombat(
                    "Maze",
                    coords=_noria_astar.calculate(
                        start=Vec2(27, 24), goal=Vec2(15, 23)
                    ),
                ),
                # TODO: Open door(N)
                SeqMove2D("Door", coords=[Vec2(15, 22)]),
                SeqMove2DClunkyCombat(
                    "Juke skellies",
                    coords=_noria_astar.calculate(
                        start=Vec2(15, 21), goal=Vec2(14, 18)
                    ),
                ),
                # TODO: Better juking so we can avoid fighting the skellies?
                SeqMove2DClunkyCombat(
                    "Juke skellies",
                    coords=_noria_astar.calculate(
                        start=Vec2(14, 18), goal=Vec2(9, 14), final_pos=Vec2(9, 13.6)
                    ),
                ),
                SeqGrabChest("Push blocks", direction=Facing.UP),
                SeqMove2DClunkyCombat(
                    "Move to block",
                    coords=_noria_astar.calculate(start=Vec2(9, 14), goal=Vec2(12, 15)),
                ),
                SeqMove2D(
                    "Push block", coords=[Vec2(12, 13), Vec2(12, 14.5), Vec2(11.5, 15)]
                ),
                SeqMenu("Menu manip"),
                SeqDelay(name="Menu manip", timeout_in_s=0.5),
                SeqMenu("Menu manip"),
                SeqMove2D(
                    "Move to block",
                    coords=_noria_astar.calculate(start=Vec2(12, 15), goal=Vec2(8, 11)),
                ),
                SeqMove2DClunkyCombat(
                    "Move to block",
                    coords=_noria_astar.calculate(start=Vec2(8, 11), goal=Vec2(4, 4)),
                ),
                SeqMove2D("Push block", coords=[Vec2(4, 3)]),
                SeqMove2DClunkyCombat(
                    "Move to block",
                    coords=_noria_astar.calculate(start=Vec2(4, 4), goal=Vec2(11, 4)),
                ),
                SeqMove2D("Push block", coords=[Vec2(11, 3), Vec2(11, 5)]),
                SeqMenu("Menu manip"),
                SeqDelay(name="Menu manip", timeout_in_s=0.5),
                SeqMenu("Menu manip"),
                SeqMove2D("Menu manip", coords=[Vec2(15, 5)]),
                SeqMenu("Menu manip"),
                SeqMove2DClunkyCombat(
                    "Move to trap",
                    coords=_noria_astar.calculate(start=Vec2(15, 5), goal=Vec2(22, 15)),
                ),
            ],
        )


class KaerisSkip(SeqSection2D):
    def __init__(self):
        # TODO: Gets stuck on Kaeris, need better controls (check pos feedback if we're not progressing)
        super().__init__(
            name="Kaeris skip",
        )
        self.timer = 0
        self.timeout = 0.2
        self.state = False
        self.move_down = True

    def reset(self):
        self.timer = 0
        self.state = False
        self.move_down = True

    _TOP_Y = 17.8
    _BOT_Y = 19
    _TARGET_X = 27

    def execute(self, delta: float) -> bool:
        player_pos = get_zelda_memory().player.pos

        ctrl = evo_ctrl()
        ctrl.dpad.right()
        # Try to wiggle past Kaeris
        if self.move_down:
            ctrl.dpad.down()
            if player_pos.y > self._BOT_Y:
                ctrl.dpad.none()
                self.move_down = False
        else:
            ctrl.dpad.up()
            if player_pos.y < self._TOP_Y:
                ctrl.dpad.none()
                self.move_down = True

        # Check if we're past
        done = player_pos.x > self._TARGET_X
        self.timer += delta
        # Release button before continuing
        if done:
            ctrl.dpad.none()
            ctrl.toggle_cancel(state=False)
            return True
        # Check if we should toggle button
        if self.timer >= self.timeout:
            self.timer = 0
            self.state = not self.state
            ctrl.toggle_cancel(self.state)
        return False


class Whackamole(SeqSection2D):
    """Bump armored enemy into pit."""

    _BOUNDS = Box2(pos=Vec2(30, 12), w=7, h=10)
    _ARENA = [
        Vec2(x, y)
        for x, y in itertools.product(
            range(_BOUNDS.pos.x, _BOUNDS.pos.x + _BOUNDS.w),
            range(_BOUNDS.pos.y, _BOUNDS.pos.y + _BOUNDS.h),
        )
    ]

    def __init__(self) -> None:
        super().__init__(name="Whackamole")
        tilemap = GetTilemap(MapID.NORIA)
        # Set up navigable arena, removing abyss tiles
        self.arena = [pos for pos in self._ARENA if pos in tilemap.map]
        self.spawned = False

    def reset(self) -> None:
        self.spawned = False

    @property
    def enemy(self) -> Optional[Evo1GameEntity2D]:
        mem = get_zelda_memory()
        with contextlib.suppress(ReferenceError):
            for actor in mem.actors:
                if (
                    self._BOUNDS.contains(actor.pos)
                    and actor.kind == Evo1GameEntity2D.EKind.ENEMY
                ):
                    return actor
        return None

    def execute(self, delta: float) -> bool:
        # Bump enemy into pit algorithm

        # 1. Detect and track enemy
        enemy = self.enemy
        if enemy is None:
            # TODO:
            # 4. Detect when enemy falls into pit
            # 5. Trigger menu glitch before cutscene triggers
            return self.spawned
        self.spawned = True

        player_pos = get_zelda_memory().player.pos
        enemy_pos = enemy.pos
        target_pos = enemy_pos - Vec2(0, 1)
        target_area = get_box_with_size(center=target_pos, half_size=0.3)

        if not target_area.contains(player_pos):
            # 2. Move above enemy (around if necessary)
            move_to(player=player_pos, target=target_pos, precision=0.3)
        else:
            # 3. Attack downwards to push enemy towards pit
            ctrl = evo_ctrl()
            ctrl.dpad.none()
            ctrl.dpad.down()
            ctrl.attack(tapping=True)

        return False


class NavigateWindtraps(SeqSection2D):
    """Avoid windtraps."""

    def __init__(self):
        super().__init__(name="Windtraps")

    def execute(self, delta: float) -> bool:
        # TODO: Avoid windtraps

        # 1. Walk south
        # 2. Time wind traps
        # 3. If caught (detect target?), open menu
        # 4. Detect when it's ok to move on
        return False


class SolveFloorPuzzle(SeqSection2D):
    """Solve floor puzzle, avoiding getting hit by the mages."""

    def __init__(self):
        super().__init__(name="Solve puzzle")
        self.step = 0

    def reset(self):
        self.step = 0

    def execute(self, delta: float) -> bool:
        # TODO: Solve puzzle

        # 1. Move to maze entrypoint Vec2(45, 26)
        # 2. Move through maze: [Vec2(45, 28), Vec2(43, 28), Vec2(43, 24), Vec2(46, 24), Vec2(46, 28)]
        # 3. Check for failures and reset
        # While navigating the maze, keep an eye out for enemies/fireballs. Open menu to avoid damage
        return False


class NoriaPuzzles(SeqList):
    """Handle movement through the various mazes and puzzles, up until grabbing the lava chest."""

    def __init__(self):
        super().__init__(
            name="Puzzles",
            children=[
                # Skip past skeletons
                SeqMenu("Menu manip"),
                SeqMove2DClunkyCombat(
                    "Move to chest",
                    coords=_noria_astar.calculate(
                        start=Vec2(22, 15), goal=Vec2(22, 17), final_pos=Vec2(22, 17.4)
                    ),
                ),
                SeqGrabChest("GUI", direction=Facing.DOWN),
                KaerisSkip(),
                SeqMove2D(
                    "Move to chest",
                    coords=_noria_astar.calculate(
                        start=Vec2(30, 18), goal=Vec2(33, 17), final_pos=Vec2(33, 16.6)
                    ),
                ),
                SeqGrabChest("Pit", direction=Facing.UP),
                # Bump enemy into pit
                # TODO: A bit inefficient, could be better with check for enemy position
                SeqMove2D("Move above enemy", coords=[Vec2(32, 14), Vec2(32, 13)]),
                Whackamole(),
                # TODO: Menu manip on fall (carry to plates?)
                SeqMove2D("Move to chest", coords=[Vec2(34, 13), Vec2(34, 4.6)]),
                SeqGrabChest("Trick plate", direction=Facing.UP),
                SeqMove2DClunkyCombat(
                    "Trigger plate(R)",
                    coords=_noria_astar.calculate(start=Vec2(34, 5), goal=Vec2(36, 4)),
                ),
                SeqHoldInPlace(
                    name="Trigger plate(R)", target=Vec2(36, 4), timeout_in_s=0.5
                ),
                SeqMove2DClunkyCombat(
                    "Trigger plate(L)",
                    coords=_noria_astar.calculate(start=Vec2(36, 4), goal=Vec2(32, 4)),
                    precision=0.1,
                ),
                SeqMenu("Menu manip"),
                SeqDelay(name="Trigger plate(L)", timeout_in_s=0.5),
                SeqMenu("Menu manip"),
                # TODO: Full menu manip
                # TODO: Just move here? Ignore skellies?
                SeqMove2D(
                    "Move to chest",
                    coords=_noria_astar.calculate(
                        start=Vec2(32, 4), goal=Vec2(38, 14), final_pos=Vec2(38, 14.4)
                    ),
                ),
                SeqGrabChest("Wind trap", direction=Facing.DOWN),
                # TODO: Navigate the wind traps
                # TODO: NavigateWindtraps(),
                SeqManualUntilClose("NAVIGATE WIND TRAPS", target=Vec2(44, 23)),
                # TODO: Remove manual
                # Get in position for chest
                SeqMove2D("Move to chest", coords=[Vec2(44, 22.6)]),
                SeqGrabChest("Puzzle", direction=Facing.UP),
                # TODO: Solve puzzle
                # SolveFloorPuzzle(),
                SeqManualUntilClose("SOLVE PUZZLE", target=Vec2(61, 27)),
                # TODO: Remove manual
                # Get in position for chest
                # TODO: Can ignore this key if we do the skip earlier
                SeqMove2D("Move to chest", coords=[Vec2(61.4, 27)]),
                SeqGrabChest("Key", direction=Facing.RIGHT),
                SeqMove2DClunkyCombat(
                    "Move to door",
                    coords=_noria_astar.calculate(
                        start=Vec2(61, 27), goal=Vec2(51, 24)
                    ),
                ),
                # TODO: Open door(N)
                SeqMove2D("Door", coords=[Vec2(51, 23)]),
                SeqMove2DClunkyCombat(
                    "Move to chest",
                    coords=_noria_astar.calculate(
                        start=Vec2(51, 23), goal=Vec2(53, 19), final_pos=Vec2(53, 18.6)
                    ),
                ),
                SeqMove2D("Move to chest", coords=[Vec2(53, 18.6)]),
                SeqGrabChest("Lava", direction=Facing.UP),
            ],
        )


class NavigateFireballs(SeqSection2D):
    """Avoid fireballs."""

    def __init__(self):
        super().__init__(name="Fireballs")
        self.coords = _noria_astar.calculate(start=Vec2(70, 31), goal=Vec2(70, 49))
        self.step = 0

    def reset(self):
        self.step = 0

    def execute(self, delta: float) -> bool:
        # TODO: Avoid fireballs

        # (1). Prep death warp by repeatedly moving into lava: Vec2(71, 31)
        # 2. Navigate over bridge and through maze: AStar start=Vec2(70, 31), goal=Vec2(70, 49)
        # While navigating the maze, keep an eye out for fireballs. Open menu to avoid damage
        return False


class NoriaLavaMaze(SeqList):
    """Handle movement through the lava mazes, up until grabbing the boss key."""

    def __init__(self):
        super().__init__(
            name="Lava Maze",
            children=[
                SeqMove2DClunkyCombat(
                    "Move to trigger",
                    coords=_noria_astar.calculate(
                        start=Vec2(53, 18), goal=Vec2(66, 20)
                    ),
                ),
                SeqMove2DCancel("Talk", coords=[Vec2(67, 22)], precision=0.4),
                SeqMove2DClunkyCombat(
                    "Lava Maze",
                    coords=_noria_astar.calculate(
                        start=Vec2(67, 22), goal=Vec2(72, 22)
                    ),
                ),
                SeqAttack("Pot"),
                SeqMove2DClunkyCombat(
                    "Lava Maze", coords=[Vec2(72.5, 22), Vec2(73, 22.5)], precision=0.1
                ),
                SeqMove2DClunkyCombat(
                    "Lava Maze",
                    coords=_noria_astar.calculate(
                        start=Vec2(73, 23),
                        goal=Vec2(70, 26),
                        final_pos=Vec2(69.5, 25.8),
                    ),
                    precision=0.1,
                ),
                SeqAttack("Pot"),
                SeqMove2DClunkyCombat(
                    "Lava Maze", coords=[Vec2(68.5, 25)], precision=0.1
                ),
                SeqMove2DClunkyCombat(
                    "Lava Maze",
                    coords=_noria_astar.calculate(
                        start=Vec2(68, 25), goal=Vec2(70, 30), final_pos=Vec2(70, 30.4)
                    ),
                ),
                SeqGrabChest("Fire maze", direction=Facing.DOWN),
                # TODO: Fire maze! Have fallback for dying here to recover (can also lower health to deathwarp later)
                # NavigateFireballs(),
                SeqManualUntilClose("NAVIGATE FIRE MAZE", target=Vec2(70, 51)),
                # TODO: Remove manual
                SeqMove2DClunkyCombat(
                    "Move to chest",
                    coords=_noria_astar.calculate(
                        start=Vec2(70, 51), goal=Vec2(78, 56), final_pos=Vec2(78.4, 56)
                    ),
                ),
                SeqGrabChest("Boss key", direction=Facing.RIGHT),
                # TODO: Deathwarp or kill everything here
                SeqManualUntilClose("GO TO BOSS DOOR", target=Vec2(41, 55)),
                # TODO: Remove manual
            ],
        )


class NoriaBossFight(SeqList):
    """Handle navigating to and defeating Dark Clink, and leaving the Mines for the overworld."""

    def __init__(self):
        super().__init__(
            name="Boss segment",
            children=[
                # SeqMove2DClunkyCombat("Move to door", coords=_noria_astar.calculate(start=Vec2(47, 67), goal=Vec2(41, 55))),
                # Get in position for chest
                # TODO: Open door(N)
                SeqMove2D("Boss door", coords=[Vec2(41, 53)]),
                SeqMove2DClunkyCombat(
                    "Move to trigger",
                    coords=_noria_astar.calculate(
                        start=Vec2(41, 53), goal=Vec2(32, 51)
                    ),
                ),
                SeqMove2DCancel("Talk", coords=[Vec2(32, 56)], precision=0.4),
                # TODO: Defeat the Dark Clink boss
                SeqManualUntilClose("DEFEAT BOSS", target=Vec2(27, 62)),
                # TODO: Remove manual
                SeqMove2D(
                    "Move to chest",
                    coords=_noria_astar.calculate(
                        start=Vec2(27, 62), goal=Vec2(21, 61), final_pos=Vec2(21, 60.6)
                    ),
                ),
                SeqGrabChest("Buster sword", direction=Facing.UP),
                # TODO: Skip (need to use cancel instead of confirm!)
                SeqMove2DCancel("Talk", coords=[Vec2(21, 69)], precision=0.4),
                SeqZoneTransition(
                    "To overworld", direction=Facing.DOWN, target_zone=MapID.OVERWORLD
                ),
            ],
        )


class NoriaMines(SeqList):
    """Top level sequence for Noria Mines."""

    def __init__(self):
        super().__init__(
            name="Noria Mines",
            children=[
                NoriaToMaze(),
                NoriaMazeAndBlocks(),
                NoriaPuzzles(),
                NoriaLavaMaze(),
                NoriaBossFight(),
            ],
        )

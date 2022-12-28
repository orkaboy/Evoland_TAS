import contextlib
import itertools
from time import sleep
from typing import Optional

from control import SeqLoadGame, SeqMenuConfirm, SeqMenuDown, evo_ctrl
from engine.combat import SeqCombat3D, SeqMove2DClunkyCombat
from engine.mathlib import Box2, Facing, Vec2, get_box_with_size, is_close
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
from engine.seq import SeqAttack, SeqDebug, SeqDelay, SeqList, SeqMenu
from evo1.move2d import SeqZoneTransition
from maps.evo1 import GetNavmap, GetTilemap
from memory.evo1 import Evo1GameEntity2D, MapID, MKind, get_memory, get_zelda_memory

_noria_astar = GetNavmap(MapID.NORIA)
_noria_start_astar = GetNavmap(MapID.NORIA_CLOSED)


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
                SeqDelay(name="Trigger plate(L)", timeout_in_s=0.7),
                SeqMenu("Menu manip"),
                SeqMove2D(
                    "Move to chest",
                    coords=_noria_astar.calculate(
                        start=Vec2(50, 37),
                        goal=Vec2(48, 47),
                    ),
                ),
                SeqMenu("Menu manip"),
                SeqMove2D(
                    "Move to chest",
                    coords=_noria_astar.calculate(
                        start=Vec2(48, 47), goal=Vec2(48, 45), final_pos=Vec2(48, 44.6)
                    ),
                ),
                SeqGrabChest("Red Mage", direction=Facing.UP),
                SeqMove2D(
                    "Move to chest",
                    coords=_noria_astar.calculate(
                        start=Vec2(48, 44), goal=Vec2(35, 41), final_pos=Vec2(35, 40.6)
                    ),
                ),
                SeqGrabChestKeyItem("Trap room", direction=Facing.UP, manip=True),
                SeqMove2D(
                    "Retrigger room",
                    coords=_noria_astar.calculate(
                        start=Vec2(35, 41), goal=Vec2(38, 44)
                    ),
                ),
                SeqDelay(name="Wait for bats", timeout_in_s=3),
                SeqCombat3D(
                    "Killing bats",
                    arena=Box2(Vec2(32, 40), w=8, h=8),
                    num_targets=6,
                    retracking=True,
                ),
                SeqMove2DClunkyCombat("Move to chest", coords=[Vec2(34, 41)]),
                # Get in position for chest
                SeqMove2D("Move to chest", coords=[Vec2(33.6, 41)]),
                SeqGrabChest("Key", direction=Facing.LEFT),
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
                SeqMove2D("Menu manip", coords=[Vec2(14.5, 5)]),
                SeqMenu("Menu manip"),
                SeqMove2DClunkyCombat(
                    "Move to trap",
                    coords=_noria_astar.calculate(start=Vec2(15, 5), goal=Vec2(22, 15)),
                ),
            ],
        )


class KaerisSkip(SeqSection2D):
    def __init__(self):
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
            ctrl.toggle_confirm(state=False)
            return True
        # Check if we should toggle button
        if self.timer >= self.timeout:
            self.timer = 0
            self.state = not self.state
            ctrl.toggle_confirm(self.state)
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
                    actor.kind == Evo1GameEntity2D.EKind.ENEMY
                    and actor.mkind == MKind.OCTOROC_ARMOR
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
            # 5. Move towards exit instead of following enemy
            # 6. Trigger menu glitch before cutscene triggers
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

    _WIND_HITBOX_SIZE = 0.5

    def execute(self, delta: float) -> bool:
        ctrl = evo_ctrl()
        # 1. Walk south [start=Vec2(39, 16), goal=Vec2(39, 26)]
        ctrl.dpad.down()

        mem = get_zelda_memory()
        player_pos = mem.player.pos
        player_hitbox = get_box_with_size(
            center=player_pos, half_size=self._WIND_HITBOX_SIZE
        )

        with contextlib.suppress(ReferenceError):
            for actor in mem.actors:
                if (
                    actor.kind == Evo1GameEntity2D.EKind.SPECIAL
                    and player_hitbox.contains(actor.pos)
                ):
                    # 2. Time wind traps
                    # 3. If caught (detect target?), open menu
                    ctrl.menu(tapping=True)
                    sleep(0.2)
                    ctrl.menu(tapping=True)

        # 4. Detect when we've reached the bottom
        done = player_pos.y >= 26

        if done:
            ctrl.dpad.none()
        return done


class SolveFloorPuzzle(SeqSection2D):
    """Solve floor puzzle, avoiding getting hit by the mages."""

    _COORDS = [
        Vec2(45, 26),
        Vec2(45, 28),
        Vec2(43, 28),
        Vec2(43, 24),
        Vec2(46, 24),
        Vec2(46, 28),
    ]

    _FIRE_HITBOX_SIZE = 0.5

    def __init__(self, precision: float = 0.2):
        super().__init__(name="Solve puzzle")
        self.step = 0
        self.precision = precision

    def reset(self):
        self.step = 0

    def execute(self, delta: float) -> bool:
        num_coords = len(self._COORDS)
        if self.step >= num_coords:
            return True

        mem = get_zelda_memory()
        target = self._COORDS[self.step]
        player_pos = mem.player.pos

        if is_close(player_pos, target, precision=self.precision):
            self.step += 1
        else:
            # Move through puzzle: [Vec2(45, 28), Vec2(43, 28), Vec2(43, 24), Vec2(46, 24), Vec2(46, 28)]
            move_to(player=player_pos, target=target, precision=self.precision)

        player_hitbox = get_box_with_size(
            center=player_pos, half_size=self._FIRE_HITBOX_SIZE
        )

        # While navigating the puzzle, keep an eye out for enemies/fireballs. Open menu to avoid damage
        ctrl = evo_ctrl()
        with contextlib.suppress(ReferenceError):
            for actor in mem.actors:
                # Some issues with detection here; the floor is entities in the same cathegory as the fireballs
                if player_hitbox.contains(actor.pos):
                    kind = actor.kind
                    is_enemy = kind == Evo1GameEntity2D.EKind.ENEMY
                    # Fireballs will have target set, the floor will not
                    is_projectile = (
                        kind == Evo1GameEntity2D.EKind.SPECIAL
                        and actor.target is not None
                    )
                    if is_projectile or is_enemy:
                        # 2. Time fireballs
                        # 3. If caught (detect target?), open menu
                        ctrl.menu()
                        sleep(0.3)
                        ctrl.menu()
        # TODO: Check for failures and reset
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
                SeqDelay(name="Trigger plate(L)", timeout_in_s=0.7),
                SeqMenu("Menu manip"),
                SeqMove2D(
                    "Move to chest",
                    coords=_noria_astar.calculate(
                        start=Vec2(32, 4), goal=Vec2(38, 14), final_pos=Vec2(38, 14.4)
                    ),
                ),
                SeqGrabChest("Wind trap", direction=Facing.DOWN),
                SeqMove2D(
                    "Move to wind traps",
                    coords=_noria_astar.calculate(
                        start=Vec2(38, 14), goal=Vec2(39, 16)
                    ),
                ),
                NavigateWindtraps(),
                SeqMove2DClunkyCombat(
                    "Move to chest",
                    coords=_noria_astar.calculate(
                        start=Vec2(39, 26), goal=Vec2(44, 23), final_pos=Vec2(44, 22.6)
                    ),
                ),
                SeqGrabChest("Puzzle", direction=Facing.UP),
                SeqMove2DClunkyCombat(
                    "Move to puzzle",
                    coords=_noria_astar.calculate(
                        start=Vec2(44, 23), goal=Vec2(45, 26)
                    ),
                ),
                # TODO: Can be somewhat unreliable
                SolveFloorPuzzle(),
                # Get in position for chest
                # Can ignore this key if we do the skip earlier
                # SeqMove2D("Move to chest", coords=[Vec2(61.4, 27)]),
                # SeqGrabChest("Key", direction=Facing.RIGHT),
                SeqMove2DClunkyCombat(
                    "Move to door",
                    coords=_noria_astar.calculate(
                        start=Vec2(47, 27), goal=Vec2(51, 24)
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
                # TODO: Can fail at picking up the chest if the bat throws it off
            ],
        )


class NavigateFireballs(SeqSection2D):
    """Avoid fireballs."""

    def __init__(self, precision: float = 0.2):
        super().__init__(name="Fireballs")
        self.coords = _noria_astar.calculate(start=Vec2(70, 31), goal=Vec2(70, 49))
        self.step = 0
        self.precision = precision

    def reset(self):
        self.step = 0

    _FIRE_HITBOX_SIZE = 0.5

    def execute(self, delta: float) -> bool:
        num_coords = len(self.coords)
        if self.step >= num_coords:
            return True

        mem = get_zelda_memory()
        target = self.coords[self.step]
        player_pos = mem.player.pos

        if is_close(player_pos, target, precision=self.precision):
            self.step += 1
        else:
            move_to(player=player_pos, target=target, precision=self.precision)

        player_hitbox = get_box_with_size(
            center=player_pos, half_size=self._FIRE_HITBOX_SIZE
        )

        # While navigating the maze, keep an eye out for fireballs. Open menu to avoid damage
        ctrl = evo_ctrl()
        with contextlib.suppress(ReferenceError):
            for actor in mem.actors:
                if player_hitbox.contains(actor.pos):
                    kind = actor.kind
                    # Fireballs will have target set, the floor will not
                    is_projectile = (
                        kind == Evo1GameEntity2D.EKind.SPECIAL
                        and actor.target is not None
                    )
                    if is_projectile:
                        # 2. Time fireballs
                        # 3. If caught (detect target?), open menu
                        ctrl.menu()
                        sleep(0.3)
                        ctrl.menu()
        # TODO: Prep deathwarp
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
                NavigateFireballs(),
                # Use move here; fighting can cause death before picking up the chest
                SeqMove2D(
                    "Move to chest",
                    coords=_noria_astar.calculate(
                        start=Vec2(70, 50), goal=Vec2(78, 56), final_pos=Vec2(78.4, 56)
                    ),
                ),
                SeqGrabChest("Boss key", direction=Facing.RIGHT),
            ],
        )


class SeekDeath(SeqSection2D):
    def __init__(self, name: str, target: Vec2):
        super().__init__(name)
        self.target = target

    def execute(self, delta: float) -> bool:
        player_pos = self.zelda_mem().player.pos
        move_to(player=player_pos, target=self.target, precision=0.2)
        # TODO: Actively bump into enemies
        # Check if we are dead, if so, return to menu
        return get_memory().player_hearts <= 0

    def __repr__(self) -> str:
        return f"Seeking death ({self.name})"


class NoriaDeathwarp(SeqList):
    def __init__(self):
        super().__init__(
            name="Noria Deathwarp",
            children=[
                # Move to center of room to draw enemies in
                SeekDeath("Boss key room", target=Vec2(70, 56)),
                SeqDelay("Wait for game over", timeout_in_s=1.0),
                SeqMenuConfirm("Game over"),
                # Wait for game to load into menu
                SeqDelay("Wait for menu", timeout_in_s=6.0),
                SeqDebug(name="SYSTEM", text="Press confirm to activate main menu."),
                SeqMenuConfirm(),
                SeqDelay(name="Menu", timeout_in_s=1.0),
                SeqMenuDown("Load game"),
                SeqDelay(name="Menu", timeout_in_s=0.5),
                SeqMenuConfirm(),
                SeqDelay(name="Menu", timeout_in_s=1.0),
                # TODO: Currently always save slot 0
                SeqLoadGame("Select save slot", 0),
                SeqMenuConfirm("Load save slot"),
                SeqDelay("Wait for game to load", timeout_in_s=3.0),
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
                NoriaDeathwarp(),
            ],
        )


# Separate section (checkpoint between)
class NoriaBoss(SeqList):
    """Handle navigating to and defeating Dark Clink, and leaving the Mines for the overworld."""

    def __init__(self):
        super().__init__(
            name="Boss segment",
            children=[
                SeqMove2D(
                    "Move to door",
                    coords=_noria_astar.calculate(
                        start=Vec2(47, 67), goal=Vec2(41, 55)
                    ),
                ),
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

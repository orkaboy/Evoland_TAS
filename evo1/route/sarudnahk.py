import contextlib
import logging
from enum import Enum, auto
from typing import Optional

from control import evo_ctrl

# from engine.combat import SeqMove2DClunkyCombat
from engine.blackboard import blackboard
from engine.mathlib import Facing, Vec2, dist, is_close
from engine.move2d import (
    SeqGrabChest,
    SeqGrabChestKeyItem,
    SeqMove2D,
    SeqSection2D,
    move_to,
)
from engine.seq import SeqList
from evo1.move2d import SeqZoneTransition
from memory import ZeldaMemory
from memory.evo1 import EKind, Evo1DiabloEntity, IKind, MapID, MKind, get_diablo_memory
from term.window import WindowLayout

logger = logging.getLogger(__name__)


# TODO: Should maybe inherit SeqMove2D instead, since we usually don't want to attack everything that moves here (slow)
# class SeqDiabloCombat(SeqMove2DClunkyCombat):
class SeqDiabloCombat(SeqMove2D):
    def __init__(self, name: str, coords: list[Vec2], precision: float = 0.2):
        super().__init__(name, coords, precision)
        self.attack_state = False
        self.attack_timer = 0

    def reset(self) -> None:
        super().reset()
        self.attack_state = False
        self.attack_timer = 0

    def zelda_mem(self) -> ZeldaMemory:
        return get_diablo_memory()

    # True if we are carrying heal glitch from Aogai (will be False if we load a save)
    def _has_heal_glitch(self) -> bool:
        return blackboard().get("hack_heal")

    # True if we could use some healing
    def _need_healing(self) -> bool:
        mem = get_diablo_memory()
        health: float = mem.player.hp
        return health < 10

    _HEAL_GLITCH_THRESHOLD = 2.1  # TODO

    # True if we are very low on health and need to use glitch
    def _critical_health(self) -> bool:
        mem = get_diablo_memory()
        health: float = mem.player.hp
        return health < self._HEAL_GLITCH_THRESHOLD

    # Boid rules:
    # 1. Move towards goal
    # 2. Avoid enemies
    # 3. Grab health
    # Move at full speed using the final direction vector from all rules
    # Restrict vision to a cone to avoid distractions?

    _BOID_AVOID_RANGE = 4
    _BOID_AVOID_FACTOR = 0.1

    def _get_boid_enemy_adjustment(self, player_pos: Vec2) -> Vec2:
        mem = get_diablo_memory()
        ret = Vec2(0, 0)
        with contextlib.suppress(ReferenceError):
            for actor in mem.actors:
                actor_kind = actor.kind
                # Avoid enemies and fireballs
                if actor_kind == EKind.MONSTER or (
                    actor_kind == EKind.INTERACT and actor.ikind == IKind.FIRE
                ):
                    actor_pos = actor.pos
                    if is_close(
                        player_pos, actor_pos, precision=self._BOID_AVOID_RANGE
                    ):
                        ret = ret + (player_pos - actor_pos)
        return ret * self._BOID_AVOID_FACTOR

    _BOID_HEALTH_RANGE = 3
    _BOID_HEALTH_FACTOR = 0.2

    def _get_boid_health_adjustment(self, player_pos: Vec2) -> Vec2:
        mem = get_diablo_memory()
        ret = Vec2(0, 0)
        with contextlib.suppress(ReferenceError):
            for actor in mem.actors:
                # Move towards life pickups
                if actor.kind == EKind.INTERACT and actor.ikind == IKind.LIFE_GLOBE:
                    actor_pos = actor.pos
                    if is_close(
                        player_pos, actor_pos, precision=self._BOID_HEALTH_RANGE
                    ):
                        ret = ret + (actor_pos - player_pos)
        heal_factor = (
            self._BOID_HEALTH_FACTOR
            if self._need_healing()
            else self._BOID_HEALTH_FACTOR / 3
        )
        return ret * heal_factor

    _MIN_TARGET_WEIGHT = 10

    def _get_boid_movement(self, player_pos: Vec2, target: Vec2) -> Vec2:
        """Combine movement from target, enemy and health"""
        move_vector = target - player_pos
        if move_vector.norm < self._MIN_TARGET_WEIGHT:
            move_vector = move_vector.normalized * self._MIN_TARGET_WEIGHT
        move_vector = move_vector + self._get_boid_enemy_adjustment(player_pos)
        move_vector = move_vector + self._get_boid_health_adjustment(player_pos)

        return move_vector.normalized

    # OVERRIDE OF SeqMove2d
    def navigate_to_checkpoint(self) -> None:
        # Move towards target
        if self.step >= len(self.coords):
            return
        target = self.coords[self.step]
        mem = self.zelda_mem()
        cur_pos = mem.player.pos

        ctrl = evo_ctrl()
        # If arrived, go to next coordinate in the list
        if is_close(cur_pos, target, self.precision):
            logger.debug(
                f"Checkpoint reached {self.step}. Player: {cur_pos} Target: {target}"
            )
            self.step = self.step + 1
            ctrl.set_neutral()
        else:
            move_vector = self._get_boid_movement(player_pos=cur_pos, target=target)
            # Adjust directions
            move_vector = move_vector.invert_y
            ctrl.set_joystick(move_vector)

    _ATTACK_TIMER = 0.1
    _ATTACK_RANGE = 0.8

    # TODO: Implement application of heal bug using blackboard
    def execute(self, delta: float) -> bool:
        ctrl = evo_ctrl()
        done = super().execute(delta)
        if not done:
            mem = get_diablo_memory()
            player_pos = mem.player.pos

            # Check for healing using glitch
            if self._critical_health() and self._has_heal_glitch():
                blackboard().set("hack_heal", False)
                ctrl.confirm()
                return False

            target = self.coords[self.step]
            direction_vec = (target - player_pos).normalized
            ahead = player_pos + direction_vec * 0.5

            # TODO: More complex attack pattern? Currently clears ahead with combo
            with contextlib.suppress(ReferenceError):
                for actor in mem.actors:
                    if actor.kind == EKind.MONSTER and is_close(
                        ahead, actor.pos, precision=self._ATTACK_RANGE
                    ):
                        self.attack_timer += delta
                        if self.attack_timer >= self._ATTACK_TIMER:
                            self.attack_timer = 0
                            self.attack_state = not self.attack_state
                            ctrl.toggle_attack(self.attack_state)
                        return False
            self.attack_state = False
            self.attack_timer = 0
        ctrl.toggle_attack(False)
        return done

    # TODO: Render?
    # def render(self, window: WindowLayout) -> None:
    #     return super().render(window)


# TODO: NavMap for Sarudnahk


class SeqDiabloBoss(SeqSection2D):
    class FightState(Enum):
        NOT_STARTED = auto()
        SETUP = auto()
        FIGHT = auto()

    def __init__(self):
        super().__init__(name="Lich")
        self.state = self.FightState.NOT_STARTED
        self.lich: Optional[Evo1DiabloEntity] = None
        self.precision = 0.3
        self.attack_state = False
        self.attack_timer = 0

    def reset(self) -> None:
        self.state = self.FightState.NOT_STARTED
        self.lich: Optional[Evo1DiabloEntity] = None
        self.attack_state = False
        self.attack_timer = 0

    _SETUP_POSITION = Vec2(114, 93)
    _ROCK_POSITION = [
        Vec2(112.5, 92.5),
        Vec2(109.5, 86.5),
        Vec2(116, 84),
        Vec2(118, 90),
    ]
    _ROCK_DISTANCE = 0.8

    def _get_closest_rock(self, player_pos: Vec2) -> Vec2:
        shortest_dist = 999
        closest_rock = self._ROCK_POSITION[0]
        for rock in self._ROCK_POSITION:
            distance = dist(player_pos, rock)
            if distance < shortest_dist:
                shortest_dist = distance
                closest_rock = rock
        return closest_rock

    def _get_safe_spot(self, rock_pos: Vec2, lich_pos: Vec2) -> Vec2:
        # Get direction from lich to rock
        direction_vec = (rock_pos - lich_pos).normalized
        # Add offset
        return rock_pos + direction_vec * self._ROCK_DISTANCE

    _ATTACK_TIMER = 0.1

    def _attack_combo(self, delta: float) -> None:
        # Should hold attack for combo
        self.attack_timer += delta
        if self.attack_timer >= self._ATTACK_TIMER:
            ctrl = evo_ctrl()
            self.attack_timer = 0
            self.attack_state = not self.attack_state
            ctrl.toggle_attack(self.attack_state)

    def _handle_lich_fight(self, delta: float) -> None:
        mem = get_diablo_memory()
        player_pos = mem.player.pos
        rock_pos = self._get_closest_rock(player_pos=player_pos)
        lich_pos = self.lich.pos
        # TODO: Need to be able to go around the rock to hide
        target_pos = self._get_safe_spot(rock_pos=rock_pos, lich_pos=lich_pos)
        if is_close(player_pos, target_pos, precision=self.precision):
            if self.turn_towards_pos(target_pos=target_pos):
                self._attack_combo(delta)
        else:
            move_to(player=player_pos, target=target_pos, precision=self.precision)

    def execute(self, delta: float) -> bool:
        mem = get_diablo_memory()
        ctrl = evo_ctrl()
        match self.state:
            case self.FightState.NOT_STARTED:
                with contextlib.suppress(ReferenceError):
                    for actor in mem.actors:
                        if actor.kind == EKind.MONSTER and actor.mkind == MKind.LICH:
                            self.lich = actor
                            if mem.player.in_control:
                                self.state = self.FightState.SETUP
                            else:
                                ctrl.cancel(tapping=True)
            case self.FightState.SETUP:
                player_pos = mem.player.pos
                move_to(
                    player=player_pos,
                    target=self._SETUP_POSITION,
                    precision=self.precision,
                )
                if is_close(player_pos, self._SETUP_POSITION, self.precision):
                    self.state = self.FightState.FIGHT
            case self.FightState.FIGHT:
                self._handle_lich_fight(delta)
                if self.lich.hp <= 0:
                    ctrl.toggle_attack(False)
                    return True
        return False

    _LICH_HP = 15000

    def render(self, window: WindowLayout) -> None:
        super().render(window)
        if self.lich is not None:
            life = self.lich.hp
            window.stats.addstr(pos=Vec2(1, 8), text="")
            window.stats.addstr(
                pos=Vec2(1, 9), text=f"  HP: {int(life):5}/{self._LICH_HP}"
            )

            window_width = window.stats.size.x - 4
            percentage = life / self._LICH_HP
            bar_width = int(window_width * percentage)
            window.stats.addch(pos=Vec2(1, 10), text="[")
            window.stats.addch(pos=Vec2(window.stats.size.x - 2, 10), text="]")
            for i in range(window_width):
                ch = "#" if i <= bar_width else " "
                window.stats.addch(pos=Vec2(2 + i, 10), text=ch)

    def __repr__(self) -> str:
        return f"{self.name} ({self.state.name})"


# TODO: NavMap for Sarudnahk


class SeqCharacterSelect(SeqGrabChest):
    def __init__(self):
        super().__init__(name="Character Select", direction=Facing.UP)
        self.timer = 0

    def reset(self) -> None:
        self.timer = 0
        super().reset()

    # Delay in s for Character Select screen to open
    _GUI_DELAY = 1.9
    _SEL_OFFSET = 10
    # Delay in s for Character Select rotation to complete
    _SEL_DELAY = 1.4

    def execute(self, delta: float) -> bool:
        ctrl = evo_ctrl()
        # Grab chest
        if not self.tapped:
            super().execute(delta)
        # Wait for GUI to appear
        elif self.timer < self._GUI_DELAY:
            self.timer += delta
        # Tap left to select character
        elif self.timer < self._SEL_OFFSET:
            logger.debug("Character select GUI open, tapping left to select Kaeris")
            ctrl.dpad.tap_left()
            self.timer = self._SEL_OFFSET
        # Wait for GUI to respond
        elif (self.timer - self._SEL_OFFSET) < self._SEL_DELAY:
            self.timer += delta
        # Confirm Kaeris character select
        else:
            logger.debug("Selecting Kaeris")
            ctrl.dpad.none()
            # This also advances the heal glitch by one, if open
            ctrl.confirm()
            return True
        return False


class Sarudnahk(SeqList):
    def __init__(self):
        super().__init__(
            name="Sarudnahk",
            children=[
                SeqDiabloCombat(
                    "Move to chest",
                    coords=[Vec2(15, 119), Vec2(15, 112.5)],
                ),
                SeqCharacterSelect(),
                # TODO: Navigate through the Diablo section (Boid behavior?)
                # TODO: Map
                # Pick up chests: Combo, Life meter, Ambient light (can glitch otherwise?), Boss
                # TODO: Extremely crude routing
                SeqDiabloCombat(
                    "Navigate ruins",
                    coords=[
                        Vec2(17, 109),
                        Vec2(25, 102.5),
                        # GC(Combo)
                        Vec2(26, 102),
                        Vec2(32, 100),
                        # TODO: Can fail if hit off course
                        Vec2(39, 96.5),
                        # GC(N) Lifebar
                        Vec2(39, 96),
                        Vec2(40, 94),
                        Vec2(45, 93),
                        Vec2(50, 93.7),
                        Vec2(51, 93.7),
                        Vec2(51.5, 93),
                        Vec2(58, 87),
                        Vec2(58, 78),
                        Vec2(54, 70),
                        Vec2(53.6, 68),
                        # Ambient?
                        Vec2(52, 66),
                        Vec2(52, 62),
                        Vec2(44, 54),
                        Vec2(44, 39),
                        Vec2(47, 36),
                        Vec2(47, 32),
                        Vec2(52, 27),
                        Vec2(53, 23),
                        Vec2(58, 22.3),
                        Vec2(62, 22.3),
                        Vec2(75, 33),
                        Vec2(88, 38),
                        Vec2(90, 45),
                        Vec2(91, 48),
                        Vec2(91, 61),
                        Vec2(100, 68),
                        Vec2(108, 70),
                        Vec2(112, 76),
                        Vec2(113, 89),
                        Vec2(114, 89),
                        Vec2(114, 88.5),
                    ],
                ),
                SeqGrabChestKeyItem("Boss", Facing.UP),
                # TODO: Manip if carrying heal glitch
                SeqDiabloBoss(),
                # Navigate past enemies in the Diablo section and grab the second part of the amulet
                SeqDiabloCombat(
                    "Navigate ruins",
                    coords=[
                        Vec2(113, 86),
                        Vec2(113, 76),
                        Vec2(108, 67),
                    ],
                ),
                SeqMove2D(
                    "Move to chest",
                    coords=[
                        Vec2(107.2, 63),
                        Vec2(107.2, 61),
                        Vec2(115, 54),
                        Vec2(115, 52.5),
                    ],
                    precision=0.1,
                ),
                SeqGrabChest("Amulet", Facing.UP),
                # Grab the portal chest and teleport to Aogai
                SeqDiabloCombat(
                    "Move to chest",
                    coords=[
                        Vec2(114, 53.6),
                        Vec2(113, 53.6),
                    ],
                    precision=0.1,
                ),
                SeqGrabChest("Town portal", Facing.UP),
                SeqMove2D(
                    "Move to portal",
                    coords=[
                        Vec2(115, 53.6),
                    ],
                    precision=0.1,
                ),
                SeqZoneTransition("Town portal", Facing.UP, target_zone=MapID.AOGAI),
            ],
        )

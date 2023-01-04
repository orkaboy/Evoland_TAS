import contextlib
import logging
from enum import Enum, auto
from typing import Optional

from control import evo_ctrl

# from engine.combat import SeqMove2DClunkyCombat
from engine.blackboard import blackboard
from engine.mathlib import Facing, Vec2, is_close
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
from memory.evo1 import EKind, Evo1DiabloEntity, MapID, MKind, get_diablo_memory
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

    _ATTACK_TIMER = 0.1
    _ATTACK_RANGE = 0.8

    def zelda_mem(self) -> ZeldaMemory:
        return get_diablo_memory()

    def _has_heal_glitch(self) -> bool:
        return blackboard().get("hack_heal")

    # TODO: Boid behavior? deviation-from-baseline movement?
    # TODO: Detect and pick up health?
    # TODO: Implement application of heal bug using blackboard
    def execute(self, delta: float) -> bool:
        ctrl = evo_ctrl()
        done = super().execute(delta)
        if not done:
            mem = get_diablo_memory()
            player_pos = mem.player.pos

            target = self.coords[self.step]
            direction_vec = (target - player_pos).normalized
            ahead = player_pos + direction_vec

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
        STARTED = auto()
        # TODO: Hide behind rock state? Attack state?

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

    _ATTACK_TIMER = 0.1

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
                                self.state = self.FightState.STARTED
                            else:
                                # TODO: diag manip
                                ctrl.cancel(tapping=True)
            case self.FightState.STARTED:
                move_to(
                    player=mem.player.pos,
                    target=self.lich.pos,
                    precision=self.precision,
                )
                # Should hold attack for combo
                self.attack_timer += delta
                # TODO: Should be in range
                if self.attack_timer >= self._ATTACK_TIMER:
                    self.attack_timer = 0
                    self.attack_state = not self.attack_state
                    ctrl.toggle_attack(self.attack_state)
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
                # TODO: Move into SeqDiabloBoss
                SeqGrabChestKeyItem("Boss", Facing.UP),
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

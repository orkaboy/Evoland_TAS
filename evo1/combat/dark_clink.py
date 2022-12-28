import contextlib
import logging
from enum import Enum, auto
from typing import Optional

from control import evo_ctrl
from engine.combat import SeqCombat3D
from engine.mathlib import Box2, Vec2
from memory.evo1 import Evo1GameEntity2D, get_zelda_memory
from term.window import WindowLayout

logger = logging.getLogger(__name__)


class SeqDarkClinkObserver(SeqCombat3D):
    """Passive observer that tracks the boss state."""

    _ARENA_BOUNDS = Box2(pos=Vec2(28, 55), w=8, h=14)

    class FightState(Enum):
        NOT_STARTED = auto()
        STARTED = auto()
        IDLE = auto()
        CHARGING = auto()
        DIZZY = auto()
        ATTACKING = auto()
        DEATH = auto()

    def __init__(self, name: str = "Dark Clink Observer", func=None) -> None:
        super().__init__(
            name=name,
            func=func,
            arena=self._ARENA_BOUNDS,
            num_targets=1,
        )
        self.state = self.FightState.NOT_STARTED
        self.last_anim = 0
        self.dark_clink: Optional[Evo1GameEntity2D] = None

    def reset(self) -> None:
        self.state = self.FightState.NOT_STARTED
        self.last_anim = 0
        self.dark_clink: Optional[Evo1GameEntity2D] = None

    _DARK_CLINK_HP = 12

    def _track_dark_clink(self) -> Optional[Evo1GameEntity2D]:
        mem = get_zelda_memory()
        with contextlib.suppress(ReferenceError):
            for actor in mem.actors:
                if self.arena.contains(actor.pos) and actor.hp == self._DARK_CLINK_HP:
                    return actor
        return None

    def _is_done(self) -> bool:
        return self.state == self.FightState.DEATH

    def _update_state(self):
        mem = get_zelda_memory()

        # Check if boss has died
        if self.dark_clink is not None and self.dark_clink.hp == 0:
            self.state = self.FightState.DEATH
            self.dark_clink = None
            logger.info("Dark Clink defeated!")

        # Track boss state
        match self.state:
            case self.FightState.NOT_STARTED:
                self.dark_clink = self._track_dark_clink()
                if self.dark_clink is not None:
                    self.state = self.FightState.STARTED
                    logger.info("Dark Clink fight started!")
            case self.FightState.STARTED:
                if mem.player.in_control:
                    self.state = self.FightState.IDLE
            case self.FightState.IDLE:
                # Super wonky logic
                self.last_anim = self.dark_clink.cur_anim
                if self.last_anim != 0:
                    if self.dark_clink.encounter_timer == 5.0:
                        self.state = self.FightState.CHARGING
                        logger.debug("Dark Clink is charging.")
                    else:
                        self.state = self.FightState.ATTACKING
            case self.FightState.CHARGING:
                cur_anim = self.dark_clink.cur_anim
                if cur_anim == 0:
                    self.state = self.FightState.IDLE
                elif cur_anim != self.last_anim:
                    self.state = self.FightState.DIZZY
                    logger.debug("Dark Clink is vulnerable!")
            case self.FightState.DIZZY:
                if self.dark_clink.cur_anim == 0:
                    self.state = self.FightState.IDLE
            case self.FightState.ATTACKING:
                if self.dark_clink.cur_anim == 0:
                    self.state = self.FightState.IDLE

    def execute(self, delta: float) -> bool:
        self._update_state()
        return self._is_done()

    def render(self, window: WindowLayout) -> None:
        super().render(window)
        if self.dark_clink is not None:
            window.stats.addstr(pos=Vec2(1, 8), text="Dark Clink")
            window.stats.addstr(pos=Vec2(2, 9), text=f"Pos: {self.dark_clink.pos}")
            window.stats.addstr(pos=Vec2(2, 10), text=f"HP: {self.dark_clink.hp}")

    def __repr__(self) -> str:
        return f"Dark Clink ({self.state.name})"


class SeqDarkClinkFight(SeqDarkClinkObserver):
    """Fight logic for the Dark Clink boss."""

    def __init__(self) -> None:
        super().__init__(
            name="Dark Clink",
        )

    def fight_logic(self):
        """The actual fight logic."""
        ctrl = evo_ctrl()
        ctrl.dpad.none()
        # mem = get_zelda_memory()
        # TODO: Fight logic
        # Move so that the boss will point himself to the wall
        # Wait for the boss to charge
        # If attacking, dodge fireballs
        # If charging, dogde out of the way at 90 degrees
        # If dizzy, close in and attack!
        # Repeat until dead

    def execute(self, delta: float) -> bool:
        # Update state
        done = super().execute(delta)
        if not done:
            mem = get_zelda_memory()
            if mem.player.not_in_control:
                # Handle initial cutscene
                evo_ctrl().confirm(tapping=True)
            else:
                self.fight_logic()
        return done

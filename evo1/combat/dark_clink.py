import contextlib
import logging
from enum import Enum, auto
from typing import Optional

from control import evo_ctrl
from engine.combat import SeqCombat3D
from engine.mathlib import Box2, Vec2, get_box_with_size, is_close
from engine.move2d import move_to
from engine.seq import wait_seconds
from memory.evo1 import EKind, Evo1GameEntity2D, MKind, get_zelda_memory
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

    _FIRE_HITBOX_SIZE = 0.7

    # Potentially dodge fireballs and kill bats
    def _handle_bats_and_fireballs(self) -> bool:
        ctrl = evo_ctrl()
        mem = get_zelda_memory()
        player_pos = mem.player.pos

        player_hitbox = get_box_with_size(
            center=player_pos, half_size=self._FIRE_HITBOX_SIZE
        )
        with contextlib.suppress(ReferenceError):
            for actor in mem.actors:
                kind = actor.kind
                # Fireballs will have target set, the floor will not
                is_projectile = kind == EKind.INTERACT and actor.target is not None
                if is_projectile and player_hitbox.contains(actor.pos):
                    # 2. Time fireballs
                    # 3. If caught (detect target?), open menu
                    ctrl.menu()
                    wait_seconds(0.5)
                    ctrl.menu()
                    return True  # We are out of date, refresh state

                # Handle bats
                is_bat = kind == EKind.MONSTER and actor.mkind == MKind.BAT
                if is_bat:
                    enemy_pos = actor.pos
                    if is_close(player_pos, enemy_pos, 1.2) and self.turn_towards_pos(
                        enemy_pos
                    ):
                        ctrl.attack()
                        return True  # We are out of date, refresh state
        return False

    # TODO: Make more dynamic
    _IDLE_POS = Vec2(29, 59)
    _DODGE_OFFSET = Vec2(0, 1.5)

    def fight_logic(self):
        """The actual fight logic."""
        ctrl = evo_ctrl()
        ctrl.dpad.none()
        mem = get_zelda_memory()
        player_pos = mem.player.pos

        if self._handle_bats_and_fireballs():
            return  # We are out of date, refresh state

        # TODO: Currently very dumb logic
        match self.state:
            case self.FightState.IDLE:
                # Need to find and pick the best wall to cling to, not too close or far away from the boss
                move_to(player=player_pos, target=self._IDLE_POS, precision=0.2)
                # TODO: Move so that the boss will point himself to the wall
                # TODO: Wait for the boss to charge
            case self.FightState.CHARGING:
                enemy_pos = self.dark_clink.pos
                # TODO: If charging, dogde out of the way at 90 degrees
                if enemy_pos.y < player_pos.y:
                    dodge_pos = self._IDLE_POS + self._DODGE_OFFSET
                else:
                    dodge_pos = self._IDLE_POS - self._DODGE_OFFSET
                move_to(player=player_pos, target=dodge_pos, precision=0.2)
            case self.FightState.DIZZY:
                # If dizzy, close in and attack!
                enemy_pos = self.dark_clink.pos
                move_to(player=player_pos, target=enemy_pos, precision=0.7)
                if is_close(player_pos, enemy_pos, 0.8) and self.turn_towards_pos(
                    enemy_pos
                ):
                    ctrl.attack(tapping=True)
        # TODO: Handle boss death menu glitch

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

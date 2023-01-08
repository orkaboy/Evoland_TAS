import contextlib
import logging
from enum import Enum, IntEnum, auto
from typing import NamedTuple, Optional

from control import evo_ctrl
from engine.mathlib import Vec2
from engine.seq import SeqBase
from evo1.atb.entity import atb_stats_from_memory
from evo1.atb.predict import predict_attack
from memory.evo1 import BattleEntity, BattleMemory
from memory.rng import EvolandRNG
from term.window import WindowLayout

logger = logging.getLogger(__name__)


def _tap_confirm() -> None:
    ctrl = evo_ctrl()
    ctrl.dpad.none()
    ctrl.set_neutral()
    ctrl.confirm(tapping=True)


class ATBAction(Enum):
    ATTACK = auto()
    POTION = auto()
    HEAL = auto()
    X_CRYSTAL = auto()
    BABAMUT = auto()


class ATBActor(IntEnum):
    CLINK = 0
    KAERIS = 1


class ATBPlan(NamedTuple):
    cur_actor: ATBActor
    action: ATBAction
    target: Optional[ATBActor | int]

    def __repr__(self) -> str:
        if self.target is not None:
            target = (
                f"->{self.target.name}"
                if isinstance(self.target, ATBActor)
                else f"->{self.target}"
            )
        else:
            target = ""
        return f"Plan({self.cur_actor.name}: {self.action.name}{target})"


# Handling of the actual battle logic itself (base class, replace with more complex logic)
class SeqATBCombat(SeqBase):
    # Finite state machine for keeping track of the battle state
    class _BattleFSM(Enum):
        PRE_BATTLE = auto()
        BATTLE = auto()
        POST_BATTLE = auto()

    def __init__(self, name: str = "Generic") -> None:
        self.mem: BattleMemory = None
        self.state = self._BattleFSM.PRE_BATTLE
        self.cur_plan: Optional[ATBPlan] = None
        super().__init__(name=name)

    def reset(self) -> None:
        self.mem = None
        self.state = self._BattleFSM.PRE_BATTLE
        self.cur_plan: Optional[ATBPlan] = None

    def update_mem(self) -> bool:
        # Check if we need to create a new ATB battle structure, or update the old one
        self.mem = BattleMemory()
        # Clear unused memory; we need to try to recreate it next frame
        if not self.active:
            self.mem = None
            return False
        return True

    _ATTACK_CURSOR_POS = 0
    _SPECIAL_CURSOR_POS = 1
    _ITEM_CURSOR_POS = 2
    _RUN_CURSOR_POS = 3

    def _execute_plan(self, plan: ATBPlan) -> bool:
        match plan.action:
            case ATBAction.ATTACK:
                return self._act_attack(plan.target)
            case ATBAction.POTION:
                return self._act_item(item_index=0, target=plan.target)
            # Kaeris/Clink Special (once he has it)
            case ATBAction.HEAL:
                return self._act_special(option=0, target=0)
            # Kaeris Special
            case ATBAction.X_CRYSTAL:
                return self._act_special(option=1, target=plan.target)
            # Clink Special (once he has it)
            case ATBAction.BABAMUT:
                return self._act_special(option=1)
        return True

    def _act_attack(self, target: int) -> bool:
        ctrl = evo_ctrl()
        if self.mem.menu_open:
            ctrl.confirm(tapping=True)
            for _ in range(target):
                ctrl.dpad.tap_down()
            ctrl.confirm()
            return True
        return False

    def _act_special(self, option: int, target: Optional[int] = None) -> bool:
        ctrl = evo_ctrl()
        if self.mem.menu_open:
            # Select special sub-menu
            with contextlib.suppress(ReferenceError):
                while self.mem.cursor != self._SPECIAL_CURSOR_POS:
                    ctrl.dpad.tap_down()
            ctrl.confirm(tapping=True)
            # Select special ability
            for _ in range(option):
                ctrl.dpad.tap_down()
            if target is not None:
                ctrl.confirm(tapping=True)
                for _ in range(target):
                    ctrl.dpad.tap_down()
            ctrl.confirm()
            return True
        return False

    def _act_item(self, item_index: int, target: ATBActor) -> bool:
        ctrl = evo_ctrl()
        if self.mem.menu_open:
            # Select item sub-menu
            with contextlib.suppress(ReferenceError):
                while self.mem.cursor != self._ITEM_CURSOR_POS:
                    ctrl.dpad.tap_down()
            ctrl.confirm(tapping=True)
            # Select item
            for _ in range(item_index):
                ctrl.dpad.tap_down()
            ctrl.confirm(tapping=True)
            # Select target
            for _ in range(target.value):
                ctrl.dpad.tap_down()
            # Use item
            ctrl.confirm()
            return True
        return False

    # TODO: Actual combat logic
    # TODO: Overload with more complex
    def handle_combat(self, should_run: bool = False):
        if should_run:
            if self.mem.menu_open:
                with contextlib.suppress(ReferenceError):
                    ctrl = evo_ctrl()
                    while self.mem.cursor != self._RUN_CURSOR_POS:
                        ctrl.dpad.tap_down()
                    ctrl.confirm()
        else:
            _tap_confirm()

    def execute(self, delta: float, should_run: bool = False) -> bool:
        # Update memory
        active = self.update_mem()
        # Handle FSM
        match self.state:
            case self._BattleFSM.PRE_BATTLE:
                if active and not self.mem.ended:
                    self.state = self._BattleFSM.BATTLE
                    logger.debug("Pre battle => Battle")
                else:
                    # Tap confirm until battle starts
                    _tap_confirm()
                    return False
            case self._BattleFSM.BATTLE:
                if active:
                    self.handle_combat(should_run)
                    if self.mem.ended:
                        logger.debug("Battle => Post battle")
                        self.state = self._BattleFSM.POST_BATTLE
                return False
            case self._BattleFSM.POST_BATTLE:
                # Tap past win screen/cutscenes
                _tap_confirm()

        return not active

    def render(self, window: WindowLayout) -> None:
        if not self.active:
            return
        window.stats.erase()
        # Render header
        window.stats.write_centered(line=1, text="Evoland TAS")
        window.stats.write_centered(line=2, text="ATB Combat")
        # Render party and enemy stats
        window.stats.addstr(Vec2(1, 4), "Party:")
        self._print_group(window=window, group=self.mem.allies, y_offset=5)
        window.stats.addstr(Vec2(1, 8), "Enemies:")
        self._print_group(window=window, group=self.mem.enemies, y_offset=9)
        # Render damage predictions
        if not self.mem.ended:
            self._print_plan(window=window)
            self._render_combat_predictions(window=window)
            # TODO: map representation?

    def _cur_actor(self) -> Optional[ATBActor]:
        # Who is acting?
        clink_turn = self.mem.allies[0].turn_gauge
        if clink_turn >= 1:
            return ATBActor.CLINK
        if len(self.mem.allies) > 1:
            kaeris_turn = self.mem.allies[1].turn_gauge
            if kaeris_turn >= 1:
                return ATBActor.KAERIS
        return None

    def _print_plan(self, window: WindowLayout) -> None:
        if self.cur_plan is not None:
            window.stats.addstr(Vec2(1, 12), f"{self.cur_plan}")

    def _render_combat_predictions(self, window: WindowLayout):
        # Who is next actor?
        clink_turn = self.mem.allies[0].turn_gauge
        if len(self.mem.allies) > 1:
            kaeris_turn = self.mem.allies[1].turn_gauge
            cur_ally = (
                self.mem.allies[1] if kaeris_turn > clink_turn else self.mem.allies[0]
            )
        else:
            cur_ally = self.mem.allies[0]
        ally = atb_stats_from_memory(cur_ally)
        enemy = atb_stats_from_memory(self.mem.enemies[0])
        # Perform damage prediction
        rng = EvolandRNG().get_rng()
        prediction = predict_attack(rng, ally, enemy)
        window.stats.addstr(Vec2(1, 13), "Damage prediction:")
        window.stats.addstr(Vec2(2, 14), f" {prediction}")

    def _print_group(
        self, window: WindowLayout, group: list[BattleEntity], y_offset: int
    ) -> None:
        for i, entity in enumerate(group):
            y_pos = y_offset + i
            window.stats.addstr(
                Vec2(2, y_pos),
                f"{entity.name}: {entity.cur_hp}/{entity.max_hp} [{entity.turn_gauge:.02f}]",
            )

    def __repr__(self) -> str:
        return f"ATB Combat ({self.name}, State: {self.state.name})"

    @property
    def active(self):
        return self.mem is not None and self.mem.battle_active

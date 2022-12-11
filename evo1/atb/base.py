import logging
from enum import Enum, auto

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
    ctrl.confirm(tapping=True)


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
        super().__init__(name=name)

    def reset(self) -> None:
        self.mem = None
        self.state = self._BattleFSM.PRE_BATTLE

    def update_mem(self) -> bool:
        # Check if we need to create a new ATB battle structure, or update the old one
        self.mem = BattleMemory()
        # Clear unused memory; we need to try to recreate it next frame
        if not self.active:
            self.mem = None
            return False
        return True

    # TODO: Actual combat logic
    # TODO: Overload with more complex
    def handle_combat(self):
        _tap_confirm()

    def execute(self, delta: float) -> bool:
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
                    self.handle_combat()
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
        window.stats.write_centered(line=1, text="Evoland 1 TAS")
        window.stats.write_centered(line=2, text="ATB Combat")
        # Render party and enemy stats
        window.stats.addstr(Vec2(1, 4), "Party:")
        self._print_group(window=window, group=self.mem.allies, y_offset=5)
        window.stats.addstr(Vec2(1, 8), "Enemies:")
        self._print_group(window=window, group=self.mem.enemies, y_offset=9)
        # Render damage predictions
        if not self.mem.ended:
            self._render_combat_predictions(window=window)
            # TODO: map representation?

    def _render_combat_predictions(self, window: WindowLayout):
        # Who is acting?
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
                f"{entity.cur_hp}/{entity.max_hp} [{entity.turn_gauge:.02f}]",
            )

    def __repr__(self) -> str:
        return f"ATB Combat ({self.name}, State: {self.state.name})"

    @property
    def active(self):
        return self.mem is not None and self.mem.battle_active

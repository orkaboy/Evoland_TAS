import logging

import evo1.control
from engine.mathlib import Vec2
from engine.seq import SeqBase
from evo1.atb.entity import atb_stats_from_memory
from evo1.atb.predict import predict_attack
from evo1.memory import BattleEntity, BattleMemory
from memory.rng import EvolandRNG
from term.window import WindowLayout

logger = logging.getLogger(__name__)


def _tap_confirm() -> None:
    ctrl = evo1.control.handle()
    ctrl.dpad.none()
    ctrl.confirm(tapping=True)


# Handling of the actual battle logic itself (base class, replace with more complex logic)
class SeqATBCombat(SeqBase):
    def __init__(self, name: str = "Generic", wait_for_battle: bool = False) -> None:
        self.mem: BattleMemory = None
        self.wait_for_battle = wait_for_battle
        # Triggered is used together with wait_for_battle to handle boss sequences
        self.triggered = False
        super().__init__(name=name)

    def reset(self) -> None:
        self.triggered = False

    def execute(self, delta: float) -> bool:
        if not self.update_mem():
            if not self.wait_for_battle or self.triggered:
                return True
            # Tap confirm until battle starts
            _tap_confirm()
            return False
        self.triggered = True

        # Tap past win screen/cutscenes
        if self.mem.ended:
            _tap_confirm()
        else:
            self.handle_combat()

        return not self.active

    def update_mem(self) -> bool:
        # Check if we need to create a new ATB battle structure, or update the old one
        if self.mem is None:
            self.mem = BattleMemory()
        else:
            self.mem.update()
        # Clear unused memory; we need to try to recreate it next frame
        if not self.active:
            self.mem = None
            return False
        return True

    # TODO: Actual combat logic
    # TODO: Overload with more complex
    def handle_combat(self):
        # TODO: Very, very dumb combat.
        _tap_confirm()

    # TODO: Render combat state
    def render(self, window: WindowLayout) -> None:
        if not self.active:
            return
        window.stats.erase()
        window.stats.write_centered(line=1, text="Evoland 1 TAS")
        window.stats.write_centered(line=2, text="ATB Combat")

        window.stats.addstr(Vec2(1, 4), "Party:")
        self._print_group(window=window, group=self.mem.allies, y_offset=5)
        window.stats.addstr(Vec2(1, 8), "Enemies:")
        self._print_group(window=window, group=self.mem.enemies, y_offset=9)

        if not self.mem.ended:
            self._render_combat_predictions(window=window)

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

        # TODO: map representation

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
        if self.active:
            return (
                f"Battle ended ({self.name})"
                if self.mem.ended
                else f"In battle ({self.name})"
            )
        return f"Waiting for battle to start ({self.name})"

    @property
    def active(self):
        return self.mem is not None and self.mem.battle_active

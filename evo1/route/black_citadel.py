from control import evo_ctrl
from engine.seq import SeqList
from evo1.atb import SeqATBCombat


class SeqZephyrosATB(SeqATBCombat):
    def __init__(self) -> None:
        super().__init__(name="Zephyros")

    # TODO: Need to detect when healing is needed
    # TODO: Need to detect when second phase is entered
    # TODO: Need to detect when battle is over
    # TODO: Cutscene
    # TODO: Detect when new battle is started
    # TODO: Summon Babamut

    def handle_combat(self, should_run: bool = False):
        # TODO: Very, very dumb combat. Need to use X-crystal and heal with potions
        ctrl = evo_ctrl()
        ctrl.dpad.none()
        ctrl.confirm(tapping=True)

    def execute(self, delta: float) -> bool:
        super().execute(delta)
        return self.state == self._BattleFSM.POST_BATTLE


class BlackCitadel(SeqList):
    def __init__(self):
        super().__init__(
            name="Black Citadel",
            children=[
                SeqZephyrosATB(),
                # TODO: Fight Zephyros. Need to track health until he does his super move
                # TODO: Summon Babamut and chase away Zephyros
            ],
        )

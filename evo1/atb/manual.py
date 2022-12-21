from evo1.atb.base import SeqATBCombat


# Dummy class for ATB combat testing; requires manual control
class SeqATBCombatManual(SeqATBCombat):
    def __init__(self, name: str = "Generic") -> None:
        super().__init__(name=name)

    def handle_combat(self, should_run: bool = False):
        pass

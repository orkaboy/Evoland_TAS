from evo1.atb.base import SeqATBCombat


# Dummy class for ATB combat testing; requires manual control
class SeqATBCombatManual(SeqATBCombat):
    def __init__(self, name: str = "Generic", wait_for_battle: bool = False) -> None:
        super().__init__(name=name, wait_for_battle=wait_for_battle)

    def handle_combat(self):
        pass

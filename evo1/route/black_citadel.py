from engine.seq import SeqList


class BlackCitadel(SeqList):
    def __init__(self):
        super().__init__(
            name="Black Citadel",
            children=[
                # TODO: Fight Zephyros. Need to track health until he does his super move
                # TODO: Summon Babamut and chase away Zephyros
            ],
        )

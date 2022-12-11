from engine.seq import SeqList
from evo1.route import (
    CrystalCavern,
    MeadowFight,
    NoriaMines,
    OverworldToCavern,
    OverworldToMeadow,
)


class CavernCheckpoint(SeqList):
    def __init__(self):
        super().__init__(
            name="Caverns experimental",
            children=[
                OverworldToCavern(),
                CrystalCavern(),
            ],
        )


def Checkpoints():
    return {
        "overworld_expr": OverworldToMeadow(),
        "meadow_expr": MeadowFight(),
        "caverns_expr": CavernCheckpoint(),
        "noria_expr": NoriaMines(),
    }

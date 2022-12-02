from evo1.seq.edel_vale import EdelExperimental
from evo1.seq import OverworldToMeadow, MeadowFight


def Checkpoints():
    return {
        "edel_expr": EdelExperimental(),
        "overworld_expr": OverworldToMeadow(),
        "meadow_expr": MeadowFight(),
    }

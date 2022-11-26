from evo1.seq.edel1 import EdelExperimental, OverworldToMeadow, MeadowFight


def Checkpoints():
    return {
        "edel_expr": EdelExperimental(),
        "overworld_expr": OverworldToMeadow(),
        "meadow_expr": MeadowFight(),
    }

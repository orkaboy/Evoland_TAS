from evo1.seq import OverworldToMeadow, MeadowFight


def Checkpoints():
    return {
        "overworld_expr": OverworldToMeadow(),
        "meadow_expr": MeadowFight(),
    }

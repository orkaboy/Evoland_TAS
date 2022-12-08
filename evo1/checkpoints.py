from evo1.seq import MeadowFight, OverworldToMeadow


def Checkpoints():
    return {
        "overworld_expr": OverworldToMeadow(),
        "meadow_expr": MeadowFight(),
    }

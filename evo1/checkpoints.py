from evo1.seq import MeadowFight, NoriaMines, OverworldToMeadow


def Checkpoints():
    return {
        "overworld_expr": OverworldToMeadow(),
        "meadow_expr": MeadowFight(),
        "noria_expr": NoriaMines(),
    }

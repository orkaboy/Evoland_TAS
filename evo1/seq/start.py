from control.menu_control import SeqLoadGame, SeqMenuConfirm, SeqMenuDown
from engine.seq import SeqBase, SeqDebug, SeqDelay, SeqList, SeqLog, SeqOptional
from term.log_init import reset_logging_time_reference


class Evoland1StartGame(SeqList):
    def __init__(self, saveslot: int):
        super().__init__(
            name="Start game",
            children=[
                SeqLog(name="SYSTEM", text="Starting Evoland1 from main menu..."),
                SeqDebug(name="SYSTEM", text="Press confirm to activate main menu."),
                SeqMenuConfirm(),
                SeqDelay(name="Menu", timeout_in_s=1.0),
                SeqOptional(
                    name="Game mode",
                    cases={
                        0: SeqList(
                            name="New game",
                            children=[
                                SeqDebug(
                                    name="SYSTEM",
                                    text="Press confirm to select new game.",
                                ),
                                SeqMenuConfirm(),
                                SeqLog(name="SYSTEM", text="Starting in..."),
                                SeqLog(name="SYSTEM", text="3"),
                                SeqDelay(name="Menu", timeout_in_s=1.0),
                                SeqLog(name="SYSTEM", text="2"),
                                SeqDelay(name="Menu", timeout_in_s=1.0),
                                SeqLog(name="SYSTEM", text="1"),
                                SeqDelay(name="Menu", timeout_in_s=1.0),
                                SeqDebug(
                                    name="SYSTEM",
                                    text="Press confirm to select Evoland1.",
                                ),
                            ],
                        ),
                    },
                    selector=saveslot,
                    fallback=SeqList(
                        name="Load game",
                        children=[
                            SeqMenuDown(name="Menu"),
                            SeqDelay(name="Menu", timeout_in_s=0.5),
                            SeqMenuConfirm(),
                            SeqDelay(name="Menu", timeout_in_s=1.0),
                            SeqLoadGame(name="Load game", saveslot=saveslot),
                            SeqLog(name="SYSTEM", text="Starting in..."),
                            SeqLog(name="SYSTEM", text="3"),
                            SeqDelay(name="Menu", timeout_in_s=1.0),
                            SeqLog(name="SYSTEM", text="2"),
                            SeqDelay(name="Menu", timeout_in_s=1.0),
                            SeqLog(name="SYSTEM", text="1"),
                            SeqDelay(name="Menu", timeout_in_s=1.0),
                        ],
                    ),
                ),
                SeqLog(name="SYSTEM", text="Starting timer!"),
                SeqBase(func=reset_logging_time_reference),
                SeqMenuConfirm(),
                # Loading the game needs a slightly longer delay than starting a new game, it seems
                SeqOptional(
                    name="Conditional delay",
                    shadow=True,
                    cases={
                        0: SeqDelay(name="Starting game", timeout_in_s=3.0),
                    },
                    selector=saveslot,
                    fallback=SeqDelay(name="Starting game", timeout_in_s=4.0),
                ),
                SeqLog(name="SYSTEM", text="In game!"),
            ],
        )

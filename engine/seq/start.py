from control import SeqLoadGame, SeqMenuConfirm, SeqMenuDown
from engine.blackboard import blackboard, clear_blackboard
from engine.seq.base import SeqBase, SeqList, SeqOptional
from engine.seq.log import SeqDebug, SeqLog
from engine.seq.time import SeqDelay
from term.log_init import reset_logging_time_reference


def start_timer():
    reset_logging_time_reference()
    blackboard().start()


class EvolandStartGame(SeqList):
    def __init__(self, saveslot: int, game: int = 1):
        super().__init__(
            name="Start game",
            children=[
                SeqBase(func=clear_blackboard),
                SeqLog(
                    name="SYSTEM", text=f"Starting Evoland {game} from main menu..."
                ),
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
                                SeqOptional(
                                    name="Game selection",
                                    selector=game,
                                    cases={
                                        2: SeqList(
                                            name="Evoland 2",
                                            children=[
                                                SeqMenuDown(name="Menu"),
                                                SeqDelay(name="Menu", timeout_in_s=0.5),
                                                # Move into difficulty menu
                                                SeqMenuConfirm(),
                                                # TODO: Difficulty?
                                            ],
                                        ),
                                    },
                                ),
                                SeqLog(name="SYSTEM", text="Starting in..."),
                                SeqLog(name="SYSTEM", text="3"),
                                SeqDelay(name="Menu", timeout_in_s=1.0),
                                SeqLog(name="SYSTEM", text="2"),
                                SeqDelay(name="Menu", timeout_in_s=1.0),
                                SeqLog(name="SYSTEM", text="1"),
                                SeqDelay(name="Menu", timeout_in_s=1.0),
                                SeqDebug(
                                    name="SYSTEM",
                                    text=f"Press confirm to select Evoland {game}.",
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
                SeqBase(func=start_timer),
                SeqLog(name="SYSTEM", text="Starting timer!"),
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

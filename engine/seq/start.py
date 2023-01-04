from control import SeqLoadGame, SeqMenuConfirm, SeqMenuDown
from engine.blackboard import blackboard, clear_blackboard
from engine.seq.base import SeqBase, SeqIf, SeqList
from engine.seq.log import SeqDebug, SeqLog
from engine.seq.time import SeqDelay
from term.log_init import reset_logging_time_reference


def start_timer():
    reset_logging_time_reference()
    blackboard().start()


class SeqIfNewGame(SeqIf):
    def __init__(
        self,
        name: str,
        when_true: SeqBase,
        when_false: SeqBase,
        default: bool = True,
        saveslot: int = 0,
    ):
        super().__init__(name, when_true, when_false, default)
        self.saveslot = saveslot

    def condition(self) -> bool:
        return self.saveslot == 0


class SeqIfEvoland2(SeqIf):
    def __init__(
        self,
        name: str,
        when_true: SeqBase,
        when_false: SeqBase,
        default: bool = False,
        game: int = 1,
    ):
        super().__init__(name, when_true, when_false, default)
        self.game = game

    def condition(self) -> bool:
        return self.game == 2


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
                SeqIfNewGame(
                    name="Game mode",
                    saveslot=saveslot,
                    when_true=SeqList(
                        name="New game",
                        children=[
                            SeqDebug(
                                name="SYSTEM",
                                text="Press confirm to select new game.",
                            ),
                            SeqMenuConfirm(),
                            SeqIfEvoland2(
                                name="Game selection",
                                game=game,
                                when_true=SeqList(
                                    name="Evoland 2",
                                    children=[
                                        SeqMenuDown(name="Menu"),
                                        SeqDelay(name="Menu", timeout_in_s=0.5),
                                        # Move into difficulty menu
                                        SeqMenuConfirm(),
                                        # TODO: Difficulty?
                                    ],
                                ),
                                when_false=None,
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
                    when_false=SeqList(
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
                SeqIfNewGame(
                    name="Conditional delay",
                    when_true=SeqDelay(name="Starting game", timeout_in_s=3.0),
                    when_false=SeqDelay(name="Starting game", timeout_in_s=4.0),
                    saveslot=saveslot,
                ),
                SeqLog(name="SYSTEM", text="In game!"),
            ],
        )

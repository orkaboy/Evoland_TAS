from control.menu_control import SeqMenuConfirm
from engine.seq import SeqDebug, SeqDelay, SeqFunc, SeqList, SeqLog
from term.log_init import reset_logging_time_reference


class Evoland1StartGame(SeqList):
    def __init__(self):
        super().__init__(
            name="Start game",
            children=[
                SeqLog(name="SYSTEM", text="Starting Evoland1 from main menu..."),
                SeqDebug(name="SYSTEM", text="Press confirm to activate main menu."),
                SeqMenuConfirm(),
                SeqDelay(name="Menu", time_in_s=1.0),
                SeqDebug(name="SYSTEM", text="Press confirm to select new game."),
                SeqMenuConfirm(),
                SeqDelay(name="Menu", time_in_s=1.0),
                SeqDebug(name="SYSTEM", text="Press confirm to select Evoland1."),
                SeqLog(name="SYSTEM", text="Starting timer!"),
                SeqFunc(reset_logging_time_reference),
                SeqMenuConfirm(),
                SeqDelay(name="Starting game", time_in_s=3.0),
                SeqLog(name="SYSTEM", text="In game!"),
            ],
        )

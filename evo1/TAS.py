# Libraries and Core Files
import curses

import memory.core as core
from engine.seq import SeqFunc, SeqList, SeqLog, SequencerEngine
from evo1.memory import load_memory
from evo1.seq import Edel1, Evoland1StartGame


def perform_TAS(main_win, stats_win, config_data: dict):
    engine = SequencerEngine(
        main_win=main_win,
        stats_win=stats_win,
        config_data=config_data,
        root=SeqList(
            name="Evoland1",
            children=[
                Evoland1StartGame(),
                SeqFunc(load_memory),  # Update all pointers
                Edel1(),
                SeqLog(name="SYSTEM", text="Evoland1 TAS Done!"),
            ],
        ),
    )

    main_win.clear()
    stats_win.clear()
    curses.doupdate()

    while engine.active():
        engine.run()

    core.wait_seconds(3)

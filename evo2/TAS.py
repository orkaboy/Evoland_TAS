# Libraries and Core Files
import contextlib
import logging

from control import evo_ctrl
from engine.mathlib import Vec2
from engine.seq import (
    EvolandStartGame,
    SeqList,
    SeqOptional,
    SequencerEngine,
    wait_seconds,
)
from evo2.checkpoints import Checkpoints
from evo2.memory import load_zelda_memory
from evo2.route import MagiStart
from term.window import WindowLayout

logger = logging.getLogger(__name__)
ctrl = evo_ctrl()


def setup_memory() -> None:
    with contextlib.suppress(ReferenceError):
        load_zelda_memory()


def perform_TAS(window: WindowLayout):

    # Print loading
    window.main.erase()
    window.stats.erase()

    text = "Preparing TAS"
    size = window.main.size
    text_len = len(text)
    x_off = int(size.x / 2 - text_len / 2)
    window.main.addstr(Vec2(x_off, int(size.y / 2)), text)
    window.update()

    logger.info("Evoland2 TAS selected")

    # Define sequence to run
    saveslot = window.config_data.get("saveslot", 0)
    checkpoint = window.config_data.get("checkpoint", "")

    # TODO: More run modes
    logger.info(
        f"Run mode is {'Any% from New Game' if saveslot == 0 else 'Any% from load'}"
    )
    logger.info("Preparing TAS... (may take a few seconds)")

    root = SeqList(
        name="Root node",
        shadow=True,
        func=setup_memory,
        children=[
            EvolandStartGame(saveslot, game=2),
            # TODO: This could be set up in a nicer way
            SeqOptional(
                shadow=True,
                name="New/Load",
                cases={
                    0: SeqList(
                        name="Evoland2 Any%",
                        children=[
                            MagiStart(),
                        ],
                    ),
                },
                selector=saveslot,
                fallback=SeqOptional(
                    name=f"Evoland2 Any% (checkpoint: {checkpoint})",
                    selector=checkpoint,
                    cases=Checkpoints(),
                ),
            ),
        ],
    )

    engine = SequencerEngine(
        window=window,
        root=root,
    )

    # Clear screen
    window.main.erase()
    window.stats.erase()
    window.update()

    # Run sequence
    while engine.active():
        engine.run()

    logger.info("Evoland2 TAS Done!"),

    wait_seconds(3)

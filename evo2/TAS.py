# Libraries and Core Files
import contextlib
import logging

from control import evo_ctrl
from engine.game import GameVersion, set_game_version
from engine.mathlib import Vec2
from engine.seq import EvolandStartGame, SeqList, SequencerEngine, wait_seconds
from evo2.route import MagiStart
from memory.evo2 import load_zelda_memory
from term.window import WindowLayout

logger = logging.getLogger(__name__)
ctrl = evo_ctrl()


def setup_memory() -> None:
    with contextlib.suppress(ReferenceError):
        load_zelda_memory()


def perform_TAS(window: WindowLayout):
    set_game_version(GameVersion.EVOLAND_2)

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

    start_game = EvolandStartGame(saveslot, game=2)

    root = SeqList(
        name="Evoland2 Any%",
        func=setup_memory,
        children=[
            MagiStart(),
        ],
    )

    engine = SequencerEngine(
        window=window,
        root=start_game,
    )
    # Run the initial start game sequence
    engine.run_engine()

    # Reset the root node
    engine = SequencerEngine(
        window=window,
        root=root,
    )
    if saveslot == 0:
        logger.info("Starting from the beginning")
    elif engine.advance_to_checkpoint(checkpoint=checkpoint):
        logger.info(f"Advanced TAS to checkpoint '{checkpoint}'")
    else:
        logger.error(f"Couldn't find checkpoint '{checkpoint}'")

    engine.run_engine()

    logger.info("Evoland2 TAS Done!"),

    wait_seconds(3)

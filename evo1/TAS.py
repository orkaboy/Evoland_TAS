# Libraries and Core Files
import contextlib
import logging

from engine.game import GameVersion, set_game_version
from engine.mathlib import Vec2
from engine.seq import (
    EvolandStartGame,
    SeqList,
    SeqOptional,
    SequencerEngine,
    wait_seconds,
)
from evo1.checkpoints import Checkpoints
from evo1.observer import SeqObserver2D
from evo1.route import (
    Aogai1,
    Aogai2,
    BlackCitadel,
    CrystalCavern,
    Edel1,
    Edel2,
    ManaTree,
    MeadowFight,
    NoriaMines,
    OverworldToAogai,
    OverworldToCavern,
    OverworldToMeadow,
    OverworldToNoria,
    PapurikaVillage,
    SacredGrove,
    Sarudnahk,
)
from evo1.route.mana_tree import SeqZephyrosObserver
from memory.evo1 import load_memory, load_zelda_memory
from term.window import WindowLayout

logger = logging.getLogger("SYSTEM")


def setup_memory() -> None:
    with contextlib.suppress(ReferenceError):
        load_memory()
        load_zelda_memory()


def observer(window: WindowLayout):
    set_game_version(GameVersion.EVOLAND_1)

    obs = SeqObserver2D("Observer", func=setup_memory)

    engine = SequencerEngine(
        window=window,
        root=obs,
    )

    window.main.erase()
    window.stats.erase()
    window.update()

    while engine.active():
        engine.run()

    wait_seconds(3)


def zephy_observer(window: WindowLayout):
    set_game_version(GameVersion.EVOLAND_1)

    obs = SeqZephyrosObserver()

    engine = SequencerEngine(
        window=window,
        root=obs,
    )

    window.main.erase()
    window.stats.erase()
    window.update()

    while engine.active():
        engine.run()

    wait_seconds(3)


def perform_TAS(window: WindowLayout):
    set_game_version(GameVersion.EVOLAND_1)

    # Print loading
    window.main.erase()
    window.stats.erase()

    text = "Preparing TAS"
    size = window.main.size
    text_len = len(text)
    x_off = int(size.x / 2 - text_len / 2)
    window.main.addstr(Vec2(x_off, int(size.y / 2)), text)
    window.update()

    logger.info("Evoland1 TAS selected")

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
            EvolandStartGame(saveslot, game=1),
            # TODO: This could be set up in a nicer way
            SeqOptional(
                shadow=True,
                name="New/Load",
                cases={
                    0: SeqList(
                        name="Evoland1 Any%",
                        children=[
                            Edel1(),
                            OverworldToMeadow(),
                            MeadowFight(),
                            PapurikaVillage(),
                            OverworldToCavern(),
                            CrystalCavern(),
                            Edel2(),
                            OverworldToNoria(),
                            NoriaMines(),
                            OverworldToAogai(),
                            Aogai1(),
                            # TODO: Navigate through the overworld to the sacred grove
                            SacredGrove(),
                            # TODO: Navigate to Aogai
                            Aogai2(),
                            # TODO: Navigate to Sarudnahk
                            Sarudnahk(),
                            # TODO: Navigate to the black citadel
                            BlackCitadel(),
                            # TODO: Get airship in Aogai
                            # TODO: Go to the Mana Tree
                            ManaTree(),
                            # TODO: End of game! Watch credits.
                        ],
                    ),
                },
                selector=saveslot,
                fallback=SeqOptional(
                    name=f"Evoland1 Any% (checkpoint: {checkpoint})",
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

    logger.info("Evoland1 TAS Done!"),

    wait_seconds(3)

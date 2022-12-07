# Libraries and Core Files
import contextlib
import curses
import logging

import memory.core as core
from engine.mathlib import Vec2
from engine.seq import SeqList, SeqOptional, SequencerEngine
from evo1.checkpoints import Checkpoints
from evo1.memory import load_memory, load_zelda_memory
from evo1.seq import Edel1, Evoland1StartGame, OverworldToMeadow, MeadowFight, PapurikaVillage, OverworldToCavern, CrystalCavern, Edel2, OverworldToNoria, NoriaMines, OverworldToAogai
from term.window import WindowLayout
from evo1.observer import SeqObserver2D


logger = logging.getLogger("SYSTEM")


def setup_memory() -> None:
    with contextlib.suppress(ReferenceError):
        load_memory()
        load_zelda_memory()


def observer(window: WindowLayout):
    observer = SeqObserver2D(
        "Observer", func=setup_memory
    )

    engine = SequencerEngine(
        window=window,
        root=observer,
    )

    window.main.erase()
    window.stats.erase()
    window.update()

    while engine.active():
        engine.run()

    core.wait_seconds(3)


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

    logger.info("Evoland1 TAS selected")

    # Define sequence to run
    saveslot = window.config_data.get("saveslot", 0)
    checkpoint = window.config_data.get("checkpoint", "")

    # TODO: More run modes
    logger.info(f"Run mode is {'Any% from New Game' if saveslot == 0 else 'Any% from load'}")
    logger.info("Preparing TAS... (may take a few seconds)")

    root = SeqList(
        name="Root node",
        shadow=True,
        func=setup_memory,
        children=[
            Evoland1StartGame(saveslot),
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
                            # TODO: Glitch around the 3D combat chest to avoid more overworld encounters (watch speedrun)
                            # TODO: Navigate to Aogai village
                            OverworldToAogai(),
                            # TODO: Have a long conversation with Sid
                            # TODO: Get the text glitch from card player in Aogai
                            # TODO: Get bombs by talking to everyone
                            # TODO: Navigate through the overworld to the sacred grove
                            # TODO: Solve puzzles in sacred grove (bow, lava mazes, dimension stones and time-warp crystals)
                            # TODO: Fight skeletons and mages
                            # TODO: Grab first part of amulet, then exit to the south
                            # TODO: Navigate to Aogai, get heal bug (card player, healer) Exit north
                            # TODO: Navigate to Sarudnahk, switch to Kaeris
                            # TODO: Navigate through the Diablo section (Boid behavior?)
                            # TODO: Fight the Undead King boss (abuse gravestone hitbox)
                            # TODO: Navigate past enemies in the Diablo section and grab the second part of the amulet
                            # TODO: Navigate to the black citadel and fight Zephyros. Need to track health until he does his super move
                            # TODO: Summon Babamut and chase away Zephyros
                            # TODO: Get airship in Aogai
                            # TODO: Go to the Mana Tree and fight Zephyros
                            # TODO: Fight final boss (Golem form)
                            # TODO: Fight final boss (Ganon form)
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

    core.wait_seconds(3)

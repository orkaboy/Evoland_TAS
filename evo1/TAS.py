# Libraries and Core Files
import contextlib
import logging

from engine.blackboard import blackboard
from engine.game import GameVersion, set_game_version
from engine.mathlib import Vec2
from engine.seq import (
    EvolandStartGame,
    SeqBase,
    SeqCheckpoint,
    SeqList,
    SequencerEngine,
    wait_seconds,
)
from evo1.combat import SeqDarkClinkObserver
from evo1.move_test import Evo1MoveTest
from evo1.observer import SeqObserver2D
from evo1.route import (
    Aogai1,
    Aogai2,
    Aogai3,
    Aogai4,
    AogaiToManaTree,
    BlackCitadel,
    BlackCitadelToAogai,
    CrystalCavern,
    Edel1,
    Edel2,
    ManaTree,
    MeadowFight,
    NoriaBoss,
    NoriaMines,
    OverworldToAogai,
    OverworldToBlackCitadel,
    OverworldToCavern,
    OverworldToMeadow,
    OverworldToNoria,
    OverworldToSacredGrove,
    OverworldToSarudnahk,
    PapurikaVillage,
    SacredGrove,
    SacredGroveToAogai,
    Sarudnahk,
)
from evo1.route.mana_tree import SeqZephyrosObserver
from memory.evo1 import load_diablo_memory, load_memory, load_zelda_memory
from term.window import WindowLayout

logger = logging.getLogger("SYSTEM")


def stop_timer() -> None:
    blackboard().stop()


def setup_memory() -> None:
    with contextlib.suppress(ReferenceError):
        load_memory()
        load_zelda_memory()
        # TODO: Optimize this, should only load when relevant
        load_diablo_memory()


def observer(window: WindowLayout):
    set_game_version(GameVersion.EVOLAND_1)

    obs = SeqObserver2D("Observer", func=setup_memory)

    engine = SequencerEngine(
        window=window,
        root=obs,
    )

    engine.run_engine()

    wait_seconds(3)


def zephy_observer(window: WindowLayout):
    set_game_version(GameVersion.EVOLAND_1)

    obs = SeqZephyrosObserver(func=load_zelda_memory)

    engine = SequencerEngine(
        window=window,
        root=obs,
    )

    engine.run_engine()

    wait_seconds(3)


def dark_clink_observer(window: WindowLayout):
    set_game_version(GameVersion.EVOLAND_1)

    obs = SeqDarkClinkObserver(func=setup_memory)

    engine = SequencerEngine(
        window=window,
        root=obs,
    )

    engine.run_engine()

    wait_seconds(3)


def move_speed_test(window: WindowLayout):
    set_game_version(GameVersion.EVOLAND_1)

    # Start on overworld save in slot 1
    start_game = EvolandStartGame(1, game=1)

    move_test_root = Evo1MoveTest(setup_memory)

    engine = SequencerEngine(
        window=window,
        root=start_game,
    )
    # Run the initial start game sequence
    engine.run_engine()

    engine = SequencerEngine(
        window=window,
        root=move_test_root,
    )

    engine.run_engine()

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

    start_game = EvolandStartGame(saveslot, game=1)

    root = SeqList(
        name="Evoland1 Any%",
        func=setup_memory,
        children=[
            Edel1(),
            SeqCheckpoint(checkpoint_name="overworld"),
            OverworldToMeadow(),
            SeqCheckpoint(checkpoint_name="meadow"),
            MeadowFight(),
            SeqCheckpoint(checkpoint_name="papurika"),
            PapurikaVillage(),
            SeqCheckpoint(checkpoint_name="cavern"),
            OverworldToCavern(),
            CrystalCavern(),
            SeqCheckpoint(checkpoint_name="edelvale"),
            Edel2(),
            OverworldToNoria(),
            SeqCheckpoint(checkpoint_name="noria"),
            NoriaMines(),
            SeqCheckpoint(checkpoint_name="noria_boss"),
            NoriaBoss(),
            SeqCheckpoint(checkpoint_name="noria_after"),
            OverworldToAogai(),
            SeqCheckpoint(checkpoint_name="aogai"),
            # TODO: Checkpoint after bomb skip?
            Aogai1(),
            SeqCheckpoint(
                checkpoint_name="sacred_grove"
            ),  # Checkpoint outside Aogai, overworld
            OverworldToSacredGrove(),
            SacredGrove(),
            SacredGroveToAogai(),
            SeqCheckpoint(checkpoint_name="aogai2"),  # Checkpoint in Aogai
            Aogai2(),
            OverworldToSarudnahk(),
            SeqCheckpoint(checkpoint_name="sarudnahk"),  # Checkpoint at start of area
            Sarudnahk(),
            # Checkpoint in Aogai square after town portal
            SeqCheckpoint(checkpoint_name="black_citadel"),
            Aogai3(),
            OverworldToBlackCitadel(),
            BlackCitadel(),
            # Get airship in Aogai (carry menu glitch to Aogai)
            BlackCitadelToAogai(),
            SeqCheckpoint(checkpoint_name="aogai3"),  # Checkpoint in Aogai
            Aogai4(),
            # Trigger conversation and leave, wait for airship to spawn
            AogaiToManaTree(),
            SeqCheckpoint(checkpoint_name="mana_tree"),  # Checkpoint outside tree
            ManaTree(),
            # TODO: End of game! Watch credits.
            SeqCheckpoint(checkpoint_name="ending"),  # End of game (for timekeeping)
            SeqBase(func=stop_timer),
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
    # Run the TAS
    engine.run_engine()

    logger.info("Evoland1 TAS Done!"),

    wait_seconds(3)

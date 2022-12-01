# Libraries and Core Files
import contextlib
import curses

import memory.core as core
from engine.seq import SeqList, SeqLog, SeqOptional, SequencerEngine
from evo1.checkpoints import Checkpoints
from evo1.memory import load_memory, load_zelda_memory
from evo1.seq import Edel1, Evoland1StartGame, OverworldToMeadow, MeadowFight, PapurikaVillage
from term.curses import WindowLayout


def setup_memory() -> None:
    with contextlib.suppress(ReferenceError):
        load_memory()
        load_zelda_memory()


def perform_TAS(window: WindowLayout):

    saveslot = window.config_data.get("saveslot", 0)
    checkpoint = window.config_data.get("checkpoint", "")

    root = SeqList(
        name="Evoland1",
        func=setup_memory,
        children=[
            Evoland1StartGame(saveslot),
            # TODO: This could be set up in a nicer way
            SeqOptional(
                name="New/Load",
                cases={
                    0: SeqList(
                        name="New game",
                        children=[
                            Edel1(),
                            OverworldToMeadow(),
                            MeadowFight(),
                            PapurikaVillage(), # TODO: Finish/Verify
                            # TODO: Grab the seed to grow up. Grab the item shop (+ cash inside) and buy gear (sword + armor)
                            # TODO: Leave the village to the east->north into the overworld
                            # TODO: Grab the forced combat chest and rescue/name Kaeris
                            # TODO: Go through the caves, grab the level up chest and fight a bit, leveling up
                            # TODO: Fight against Kefka's ghost (need to implement a smarter combat function to avoid the boss counter)
                            # TODO: Grab the crystal and become 3D
                            # TODO: Navigate Edel Vale in 3D, solving puzzles and escaping to the south
                            # TODO: Navigate through the Mines, solving puzzles
                            # TODO: The TAS should abuse the menu bug and potentially deathwarp here (see speedrun)
                            # TODO: Fight shadow Clink boss
                            # TODO: Glitch around the 3D combat chest to avoid more overworld encounters (watch speedrun)
                            # TODO: Navigate to Aogai village
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
                    name="Load game",
                    selector=checkpoint,
                    cases=Checkpoints(),
                ),
            ),
            SeqLog(name="SYSTEM", text="Evoland1 TAS Done!"),
        ],
    )

    engine = SequencerEngine(
        window=window,
        root=root,
    )

    window.main.clear()
    window.stats.clear()
    curses.doupdate()

    while engine.active():
        engine.run()

    core.wait_seconds(3)

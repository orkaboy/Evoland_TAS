from enum import Enum, auto
from typing import Optional

from engine.pathing import TileMap
from maps.evo1 import CurrentTilemap as evo1_tilemap
from memory.evo1 import get_zelda_memory as evo1_zelda_memory
from memory.evo2 import get_zelda_memory as evo2_zelda_memory
from memory.zelda_base import ZeldaMemory


# global for game version launched
class GameVersion(Enum):
    EVOLAND_1 = auto()
    EVOLAND_2 = auto()


GAME_VERSION = GameVersion.EVOLAND_1


def set_game_version(version: GameVersion):
    global GAME_VERSION
    GAME_VERSION = version


def get_zelda_memory() -> ZeldaMemory:
    match GAME_VERSION:
        case GameVersion.EVOLAND_1:
            return evo1_zelda_memory()
        case GameVersion.EVOLAND_2:
            return evo2_zelda_memory()


def get_current_tilemap() -> Optional[TileMap]:
    match GAME_VERSION:
        case GameVersion.EVOLAND_1:
            return evo1_tilemap()
        # TODO: Evoland2 maps
        case _:
            return None

from typing import Optional

from engine.pathing import AStar, TileMap
from memory.evo1 import MapID, get_memory


class NavMap:
    def __init__(self, filename: str) -> None:
        self.tilemap = TileMap(filename=filename)
        self.astar = AStar(self.tilemap.map)


_maps = {
    MapID.EDEL_VALE: NavMap("maps/evo1/edel_vale.yaml"),
    MapID.OVERWORLD: NavMap("maps/evo1/overworld.yaml"),
    MapID.MEADOW: NavMap("maps/evo1/meadow.yaml"),
    MapID.PAPURIKA: NavMap("maps/evo1/village.yaml"),
    MapID.PAPURIKA_WELL: NavMap("maps/evo1/village_well.yaml"),
    MapID.PAPURIKA_INTERIOR: NavMap("maps/evo1/village_interior.yaml"),
    MapID.CRYSTAL_CAVERN: NavMap("maps/evo1/crystal_cavern.yaml"),
    MapID.LIMBO: NavMap("maps/evo1/limbo.yaml"),
    MapID.NORIA_CLOSED: NavMap("maps/evo1/noria_start.yaml"),
    MapID.NORIA: NavMap("maps/evo1/noria_mines.yaml"),
    MapID.SACRED_GROVE_2D: NavMap("maps/evo1/sacred_grove.yaml"),
    # TODO: Add the 3d map too?
    MapID.SACRED_GROVE_3D: NavMap("maps/evo1/sacred_grove.yaml"),
    MapID.SACRED_GROVE_CAVE_1: NavMap("maps/evo1/sacred_grove_cave1.yaml"),
    MapID.SACRED_GROVE_CAVE_2: NavMap("maps/evo1/sacred_grove_cave2.yaml"),
    # TODO: Sarudnahk
    MapID.END: NavMap("maps/evo1/end.yaml"),
    # TODO: Side dungeons
}


def CurrentTilemap() -> Optional[TileMap]:
    mem = get_memory()
    current_map = mem.map_id
    return navmap.tilemap if (navmap := _maps.get(current_map)) else None


def GetAStar(map_id: MapID) -> AStar:
    return _maps.get(map_id).astar

from typing import Optional

from engine.pathing import AStar, TileMap
from evo1.memory import MapID, get_memory


class NavMap:
    def __init__(self, filename: str) -> None:
        self.tilemap = TileMap(filename=filename)
        self.astar = AStar(self.tilemap.map)


_maps = {
    MapID.EDEL_VALE: NavMap("evo1/maps/edel_vale.yaml"),
    MapID.OVERWORLD: NavMap("evo1/maps/overworld.yaml"),
    MapID.MEADOW: NavMap("evo1/maps/meadow.yaml"),
    MapID.PAPURIKA: NavMap("evo1/maps/village.yaml"),
    MapID.PAPURIKA_WELL: NavMap("evo1/maps/village_well.yaml"),
    MapID.PAPURIKA_INTERIOR: NavMap("evo1/maps/village_interior.yaml"),
    MapID.CRYSTAL_CAVERN: NavMap("evo1/maps/crystal_cavern.yaml"),
    MapID.LIMBO: NavMap("evo1/maps/limbo.yaml"),
    MapID.NORIA_CLOSED: NavMap("evo1/maps/noria_start.yaml"),
    MapID.NORIA: NavMap("evo1/maps/noria_mines.yaml"),
    MapID.SACRED_GROVE_2D: NavMap("evo1/maps/sacred_grove.yaml"),
    MapID.SACRED_GROVE_3D: NavMap(
        "evo1/maps/sacred_grove.yaml"
    ),  # TODO: Add the 3d map too?
    MapID.SACRED_GROVE_CAVE_1: NavMap("evo1/maps/sacred_grove_cave1.yaml"),
    MapID.SACRED_GROVE_CAVE_2: NavMap("evo1/maps/sacred_grove_cave2.yaml"),
    # TODO: Sarudnahk
    MapID.END: NavMap("evo1/maps/end.yaml"),
    # TODO: Side dungeons
}


def CurrentTilemap() -> Optional[TileMap]:
    mem = get_memory()
    current_map = mem.map_id
    return navmap.tilemap if (navmap := _maps.get(current_map)) else None


def GetAStar(map_id: MapID) -> AStar:
    return _maps.get(map_id).astar

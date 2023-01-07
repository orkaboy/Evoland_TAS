from typing import Dict, Optional

from engine.pathing import AStar, NavMesh, Pathing, TileMap
from memory.evo1 import MapID, get_memory


class NavMap:
    def __init__(self) -> None:
        self.tilemap: Optional[TileMap] = None
        self.nav: Optional[Pathing] = None


class AStarNavMap(NavMap):
    def __init__(self, filename: str) -> None:
        self.tilemap = TileMap(filename=filename)
        self.nav = AStar(self.tilemap.map)


class NavMeshNavMap(NavMap):
    def __init__(self, filename: str) -> None:
        self.tilemap = TileMap(filename=filename)
        self.nav = NavMesh(
            map_nodes=self.tilemap.nav_nodes, edges=self.tilemap.nav_edges
        )


_sacred_grove = AStarNavMap("maps/evo1/sacred_grove.yaml")

_maps: Dict[MapID, NavMap] = {
    MapID.EDEL_VALE: AStarNavMap("maps/evo1/edel_vale.yaml"),
    MapID.OVERWORLD: AStarNavMap("maps/evo1/overworld.yaml"),
    MapID.MEADOW: AStarNavMap("maps/evo1/meadow.yaml"),
    MapID.PAPURIKA: AStarNavMap("maps/evo1/village.yaml"),
    MapID.PAPURIKA_WELL: AStarNavMap("maps/evo1/village_well.yaml"),
    MapID.PAPURIKA_INTERIOR: AStarNavMap("maps/evo1/village_interior.yaml"),
    MapID.CRYSTAL_CAVERN: AStarNavMap("maps/evo1/crystal_cavern.yaml"),
    MapID.LIMBO: AStarNavMap("maps/evo1/limbo.yaml"),
    MapID.NORIA_CLOSED: AStarNavMap("maps/evo1/noria_start.yaml"),
    MapID.NORIA: AStarNavMap("maps/evo1/noria_mines.yaml"),
    MapID.AOGAI: NavMeshNavMap("maps/evo1/aogai.yaml"),
    MapID.SACRED_GROVE_2D: _sacred_grove,
    # TODO: Add the 3d map too?
    MapID.SACRED_GROVE_3D: _sacred_grove,
    MapID.SACRED_GROVE_CAVE_1: AStarNavMap("maps/evo1/sacred_grove_cave1.yaml"),
    MapID.SACRED_GROVE_CAVE_2: AStarNavMap("maps/evo1/sacred_grove_cave2.yaml"),
    MapID.SARUDNAHK: NavMeshNavMap("maps/evo1/sarudnahk.yaml"),
    MapID.END: AStarNavMap("maps/evo1/end.yaml"),
    # TODO: Side dungeons
}


def GetTilemap(map_id: MapID) -> Optional[TileMap]:
    return navmap.tilemap if (navmap := _maps.get(map_id)) else None


def CurrentTilemap() -> Optional[TileMap]:
    mem = get_memory()
    current_map = mem.map_id
    return navmap.tilemap if (navmap := _maps.get(current_map)) else None


def GetNavmap(map_id: MapID) -> Pathing:
    return _maps.get(map_id).nav

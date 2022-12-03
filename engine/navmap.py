from engine.mathlib import Vec2, dist
from typing import List
import os
from enum import Enum
import logging
from PIL import Image
import yaml
import tmx

try:
    from yaml import CDumper as Dumper
    from yaml import CLoader as Loader
except ImportError:
    from yaml import Dumper, Loader

logger = logging.getLogger(__name__)


class NavMap:
    def __init__(self, filename: str) -> None:
        map_data = self._open(filename=filename)
        self.name = map_data.get("name", "UNKNOWN")
        self.type = map_data.get("type", "ascii")
        origin_vec = map_data.get("origin", [0, 0])
        self.origin = Vec2(origin_vec[0], origin_vec[1])
        # Map consists of a list of traversible nodes. Nodes are connected NWSE
        self.map = [] # Map, as a set of Vec2 nodes
        match self.type:
            case "ascii":
                self._load_ascii(map_data=map_data)
            case "bitmap":
                png_filename = f"{os.path.splitext(filename)[0]}.png"
                self._load_bitmap(filename=png_filename, map_data=map_data)
            case "tmx":
                tmx_filename = f"{os.path.splitext(filename)[0]}.tmx"
                self._load_tmx(filename=tmx_filename, map_data=map_data)

    def _load_ascii(self, map_data: dict) -> None:
        self.tiles = map_data.get("tiles", []) # ascii representation of map, as array of strings
        for i, line in enumerate(self.tiles):
            y_pos = i + self.origin.y
            for j, tile in enumerate(line):
                if tile == '.':
                    x_pos = j + self.origin.x
                    self.map.append(Vec2(x_pos, y_pos))

    def _load_tmx(self, filename: str, map_data: dict) -> None:
        #self.map.append()
        tilemap: tmx.TileMap = tmx.TileMap.load(fname=filename)
        width, height = tilemap.width, tilemap.height
        self.tiles = ["" for _ in range(height)]
        logger.debug(f"Map bitmap {filename} dims: {width} x {height}")
        layer: tmx.Layer
        for layer in tilemap.layers_list:
            if layer.name != "collide":
                continue
            tile: tmx.LayerTile
            for i, tile in enumerate(layer.tiles):
                x, y = i % width, i // width
                wall = tile.gid != 0
                self.tiles[y] += '#' if wall else '.'
                if not wall:
                    self.map.append(Vec2(x, y))

    class BitmapTile(Enum):
        # Impassable terrain
        EMPTY = 0x000000
        EMPTY_DUNGEON = 0x0f0f0f
        TREE = 0x0f6d01 # Passable on overworld map
        DEAD_TREE = 0x3d2e01
        WATER = 0x65b4fb
        ROCKS = 0x9e9e9e
        DARK_ROCKS = 0xc08879
        CACTI = 0x6fda02
        BUSH = 0x1eda02
        POT = 0x4dfdfc
        WALLS = 0x5f5f5f
        WATER_DUNGEON = 0x4d7afd
        LAVA = 0xda5302
        LAVA_TRAP = 0xfeb286
        PITFALL = 0x3f3d17
        PITFALL2 = 0x1f1f1f
        STATUE = 0x376d01
        WIND_TRAP = 0xa8c3ff
        # Passable terrain
        PASSABLE = 0x010101
        GRASS = 0x64fd4d
        PATH = 0x91fe81
        SAND = 0xe8fd4d
        BRIDGE = 0xa26502
        SAVE_POINT = 0x2d7faf
        DIMENSION_STONE = 0x802828
        FLOOR = 0xe3e0b3
        FLOOR2 = 0xd2cd84
        WATER_BRIDGE = 0xb8cafe
        SPIKES = 0xbae5fe
        HIDDEN_PASSAGE = 0x8294c8
        PUZZLE_TILE = 0xf7f6e9
        VOID_GROUND = 0xe0e0e0
        # Actors
        SPAWN = 0xffffff
        CHEST = 0xffff00
        # Enemies
        OCTOROC = 0xff0000
        BAT = 0xec5eca
        KNIGHT = 0xff0001
        SKELETON = 0xc88283
        RED_MAGE = 0xad18c4

        @classmethod
        def _missing_(cls, value):
            return cls.PASSABLE

    TileToAscii = {
        BitmapTile.EMPTY: ' ',
        BitmapTile.EMPTY_DUNGEON: ' ',
        BitmapTile.TREE: '#',
        BitmapTile.DEAD_TREE: '[',
        BitmapTile.WATER: '~',
        BitmapTile.WATER_DUNGEON: '~',
        BitmapTile.ROCKS: 'o',
        BitmapTile.DARK_ROCKS: 'O',
        BitmapTile.CACTI: 'Y',
        BitmapTile.BUSH: 'w',
        BitmapTile.POT: 'u',
        BitmapTile.WALLS: '#',
        BitmapTile.LAVA: '%',
        BitmapTile.LAVA_TRAP: '%',
        BitmapTile.PITFALL: ' ',
        BitmapTile.PITFALL2: ' ',
        BitmapTile.STATUE: '&',
        BitmapTile.WIND_TRAP: 'W',
        # Passable
        BitmapTile.BRIDGE: '=',
        BitmapTile.WATER_BRIDGE: '=',
        BitmapTile.SAVE_POINT: 'S',
        BitmapTile.DIMENSION_STONE: 'D',
        BitmapTile.SPIKES: '^',
        BitmapTile.HIDDEN_PASSAGE: '*',
        BitmapTile.PUZZLE_TILE: 'P',
        # Default: '.'
    }

    def _get_rgb_hex(self, pixel: List[int]) -> int:
        red = int(pixel[0]) & 0xFF
        green = int(pixel[1]) & 0xFF
        blue = int(pixel[2]) & 0xFF
        return (red << 16) | (green << 8) | blue

    def _is_passable(self, tile: BitmapTile, trees_passable: bool) -> bool:
        match tile:
            case self.BitmapTile.EMPTY | self.BitmapTile.EMPTY_DUNGEON | self.BitmapTile.DEAD_TREE | self.BitmapTile.WALLS | self.BitmapTile.WATER | self.BitmapTile.WATER_DUNGEON | self.BitmapTile.ROCKS | self.BitmapTile.CACTI | self.BitmapTile.BUSH | self.BitmapTile.POT | self.BitmapTile.LAVA | self.BitmapTile.LAVA_TRAP | self.BitmapTile.PITFALL | self.BitmapTile.PITFALL2 | self.BitmapTile.STATUE | self.BitmapTile.WIND_TRAP:
                return False
            case self.BitmapTile.TREE:
                return trees_passable
        return True

    def _load_bitmap(self, filename: str, map_data: dict) -> None:
        self.tiles = []
        trees_passable = map_data.get("trees_passable", False)
        bitmap = Image.open(filename)
        W, H = bitmap.size[0], bitmap.size[1]
        logger.debug(f"Map bitmap {filename} dims: {W} x {H}")
        for y in range(H):
            self.tiles.append("") # Append new empty line
            for x in range(W):
                coord = x, y
                rgb = self._get_rgb_hex(bitmap.getpixel(coord))
                tile = self.BitmapTile(rgb)
                # Fill out ascii tile
                self.tiles[y] += self.TileToAscii.get(tile, '.')
                # Add passable nodes to AStar map
                if self._is_passable(tile, trees_passable):
                    self.map.append(Vec2(x, y))

        # self.map.append()


    def _open(self, filename: str) -> dict:
        # Open the map file and parse the yaml contents
        with open(filename) as map_file:
            return yaml.load(map_file, Loader=Loader)


# f(n) = g(n) + h(n)
class AStar:
    class Node:
        def __init__(self, pos: Vec2, goal: Vec2, cost: float = 0, parent = None) -> None:
            self.pos = pos
            self.cost = cost
            self.parent = parent

            self.f = cost + self._heuristic(pos, goal)

        def _heuristic(self, a: Vec2, b: Vec2) -> float:
            return dist(a, b)

        # Used for is-x-in
        def __eq__(self, other: object) -> bool:
            return self.pos == other.pos

        # Used for sorting (put the least f last)
        def __lt__(self, other: object) -> bool:
            return self.f > other.f

        # Trace path to root
        def trace_path(self) -> List[Vec2]:
            cur = self
            ret = []
            while cur.parent:
                ret.append(cur.pos)
                cur = cur.parent
            ret.reverse()
            return ret


    def __init__(self, map_nodes: List[Vec2]) -> None:
        self.map = map_nodes

    def calculate(self, start: Vec2, goal: Vec2, free_move: bool = True) -> List[Vec2]:
        open_list = [AStar.Node(start, goal)]
        closed_list: List[AStar.Node] = []
        while open_list:
            open_list.sort()
            node = open_list.pop()
            if node.pos == goal:
                return node.trace_path()
            # else (goal not reached), add to closed_list list and elaborate
            closed_list.append(node)
            for neighbor in self._neighbors(node, goal, free_move):
                if neighbor in closed_list:
                    self._update_node(node, neighbor, closed_list)
                elif neighbor in open_list:
                    self._update_node(node, neighbor, open_list)
                else:
                    open_list.append(neighbor)
        raise ValueError # No path could be found between start and goal

    def _update_node(self, cur_node: Node, neighbor: Node, node_list: List[Node]) -> None:
        n_idx = node_list.index(neighbor)
        if neighbor.cost < node_list[n_idx].cost:
            node_list[n_idx].cost = neighbor.cost
            node_list[n_idx].parent = cur_node

    def _neighbors(self, node: Node, goal: Vec2, free_move: bool) -> List[Node]:
        adjacent = []
        # directly adjacent
        node_n = AStar.Node(node.pos + Vec2(0, -1), goal=goal, cost=node.cost+1, parent=node)
        node_e = AStar.Node(node.pos + Vec2(1, 0), goal=goal, cost=node.cost+1, parent=node)
        node_s = AStar.Node(node.pos + Vec2(0, 1), goal=goal, cost=node.cost+1, parent=node)
        node_w = AStar.Node(node.pos + Vec2(-1, 0), goal=goal, cost=node.cost+1, parent=node)
        # Ignore nodes that are not traversible
        if node_n.pos in self.map:
            adjacent.append(node_n)
        if node_e.pos in self.map:
            adjacent.append(node_e)
        if node_s.pos in self.map:
            adjacent.append(node_s)
        if node_w.pos in self.map:
            adjacent.append(node_w)
        # diagonals
        if free_move:
            node_nw = AStar.Node(node.pos + Vec2(-1, -1), goal=goal, cost=node.cost+1.4, parent=node)
            node_ne = AStar.Node(node.pos + Vec2(1, -1), goal=goal, cost=node.cost+1.4, parent=node)
            node_se = AStar.Node(node.pos + Vec2(1, 1), goal=goal, cost=node.cost+1.4, parent=node)
            node_sw = AStar.Node(node.pos + Vec2(-1, 1), goal=goal, cost=node.cost+1.4, parent=node)
            # Ignore nodes that are not traversible
            # Only allow nodes we can easily walk to without hitting stuff in the way (disallow hugging walls)
            if node_nw.pos in self.map and node_n.pos in self.map and node_w.pos in self.map:
                adjacent.append(node_nw)
            if node_ne.pos in self.map and node_n.pos in self.map and node_e.pos in self.map:
                adjacent.append(node_ne)
            if node_se.pos in self.map and node_s.pos in self.map and node_e.pos in self.map:
                adjacent.append(node_se)
            if node_sw.pos in self.map and node_s.pos in self.map and node_w.pos in self.map:
                adjacent.append(node_sw)
        return adjacent

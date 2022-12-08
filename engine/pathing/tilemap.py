import logging
import os
from enum import Enum
from typing import List

import tmx
import yaml
from PIL import Image

from engine.mathlib import Vec2

try:
    from yaml import CLoader as Loader
except ImportError:
    from yaml import Loader

logger = logging.getLogger(__name__)


class TileMap:
    def __init__(self, filename: str) -> None:
        map_data = self._open(filename=filename)
        self.name = map_data.get("name", "UNKNOWN")
        self.type = map_data.get("type", "ascii")
        origin_vec = map_data.get("origin", [0, 0])
        self.origin = Vec2(origin_vec[0], origin_vec[1])
        # Map consists of a list of traversible nodes. Nodes are connected NWSE
        self.map = []  # Map, as a set of Vec2 nodes
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
        # ascii representation of map, as array of strings
        self.tiles = map_data.get("tiles", [])
        for i, line in enumerate(self.tiles):
            y_pos = i + self.origin.y
            for j, tile in enumerate(line):
                if tile == ".":
                    x_pos = j + self.origin.x
                    self.map.append(Vec2(x_pos, y_pos))

    def _load_tmx(self, filename: str, map_data: dict) -> None:
        # self.map.append()
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
                self.tiles[y] += "#" if wall else "."
                if not wall:
                    self.map.append(Vec2(x, y))

    class BitmapTile(Enum):
        # Impassable terrain
        EMPTY = 0x000000
        EMPTY_DUNGEON = 0x0F0F0F
        TREE = 0x0F6D01  # Passable on overworld map
        DEAD_TREE = 0x3D2E01
        WATER = 0x65B4FB
        ROCKS = 0x9E9E9E
        DARK_ROCKS = 0xC08879
        CACTI = 0x6FDA02
        BUSH = 0x1EDA02
        POT = 0x4DFDFC
        WALLS = 0x5F5F5F
        WATER_DUNGEON = 0x4D7AFD
        LAVA = 0xDA5302
        LAVA_TRAP = 0xFEB286
        PITFALL = 0x3F3D17
        PITFALL2 = 0x1F1F1F
        STATUE = 0x376D01
        WIND_TRAP = 0xA8C3FF
        # Passable terrain
        PASSABLE = 0x010101
        GRASS = 0x64FD4D
        PATH = 0x91FE81
        SAND = 0xE8FD4D
        BRIDGE = 0xA26502
        SAVE_POINT = 0x2D7FAF
        DIMENSION_STONE = 0x802828
        FLOOR = 0xE3E0B3
        FLOOR2 = 0xD2CD84
        WATER_BRIDGE = 0xB8CAFE
        SPIKES = 0xBAE5FE
        HIDDEN_PASSAGE = 0x8294C8
        PUZZLE_TILE = 0xF7F6E9
        VOID_GROUND = 0xE0E0E0
        # Actors
        SPAWN = 0xFFFFFF
        CHEST = 0xFFFF00
        # Enemies
        OCTOROC = 0xFF0000
        BAT = 0xEC5ECA
        KNIGHT = 0xFF0001
        SKELETON = 0xC88283
        RED_MAGE = 0xAD18C4

        @classmethod
        def _missing_(cls, value):
            return cls.PASSABLE

    TileToAscii = {
        BitmapTile.EMPTY: " ",
        BitmapTile.EMPTY_DUNGEON: " ",
        BitmapTile.TREE: "#",
        BitmapTile.DEAD_TREE: "[",
        BitmapTile.WATER: "~",
        BitmapTile.WATER_DUNGEON: "~",
        BitmapTile.ROCKS: "o",
        BitmapTile.DARK_ROCKS: "O",
        BitmapTile.CACTI: "Y",
        BitmapTile.BUSH: "w",
        BitmapTile.POT: "u",
        BitmapTile.WALLS: "#",
        BitmapTile.LAVA: "%",
        BitmapTile.LAVA_TRAP: "%",
        BitmapTile.PITFALL: " ",
        BitmapTile.PITFALL2: " ",
        BitmapTile.STATUE: "&",
        BitmapTile.WIND_TRAP: "W",
        # Passable
        BitmapTile.BRIDGE: "=",
        BitmapTile.WATER_BRIDGE: "=",
        BitmapTile.SAVE_POINT: "S",
        BitmapTile.DIMENSION_STONE: "D",
        BitmapTile.SPIKES: "^",
        BitmapTile.HIDDEN_PASSAGE: "*",
        BitmapTile.PUZZLE_TILE: "P",
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
            self.tiles.append("")  # Append new empty line
            for x in range(W):
                coord = x, y
                rgb = self._get_rgb_hex(bitmap.getpixel(coord))
                tile = self.BitmapTile(rgb)
                # Fill out ascii tile
                self.tiles[y] += self.TileToAscii.get(tile, ".")
                # Add passable nodes to AStar map
                if self._is_passable(tile, trees_passable):
                    self.map.append(Vec2(x, y))

        # self.map.append()

    def _open(self, filename: str) -> dict:
        # Open the map file and parse the yaml contents
        with open(filename) as map_file:
            return yaml.load(map_file, Loader=Loader)

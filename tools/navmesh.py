import os
import sys

import arcade
import yaml
from pyglet.math import Vec2

try:
    from yaml import CLoader as Loader
except ImportError:
    from yaml import Loader


class TileMap:
    """Simple loader class that parses the navmesh yaml file."""

    def __init__(self, filename: str) -> None:
        map_data = self._open(filename=filename)
        self.name = map_data.get("name", "UNKNOWN")
        self.type = map_data.get("type", "bitmap")
        origin_vec = map_data.get("origin", [0, 0])
        self.origin = Vec2(origin_vec[0], origin_vec[1])
        match self.type:
            case "bitmap":
                self.png_filename = f"{os.path.splitext(filename)[0]}.png"
        # NavMesh graph nodes
        nodes = map_data.get("nodes", [])
        self.nav_nodes = [Vec2(x=node[0], y=node[1]) for node in nodes]
        self.nav_edges = map_data.get("edges", [])

    def _open(self, filename: str) -> dict:
        # Open the map file and parse the yaml contents
        with open(filename, mode="r") as map_file:
            return yaml.load(map_file, Loader=Loader)


SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 1000
SCREEN_TITLE = "Navmesh viewer"


class NavmeshViewer(arcade.Window):
    _CAMERA_SPEED = 500

    def __init__(self, tilemap: TileMap):
        super().__init__(width=SCREEN_WIDTH, height=SCREEN_HEIGHT, title=SCREEN_TITLE)
        arcade.set_background_color(arcade.csscolor.WHITE)
        self.tilemap = tilemap
        self.image = None
        self.camera = None
        self.camera_pos = Vec2(0, 0)
        self.camera_vel = Vec2(0, 0)
        # TODO: Make this a bit more automated
        self.scale = 25.0

    def setup(self):
        # If there is an image connected to the map, load it
        if hasattr(self.tilemap, "png_filename"):
            self.image = arcade.Sprite(self.tilemap.png_filename)
            self.image.center_x = self.width / 2
            self.image.center_y = self.height / 2
            self.image.scale = self.width / self.image.width
            # Set scale for rendering nodes/edges
            self.scale = self.image.scale
        # Move the camera to the origin point, which will offset all drawing
        self.camera = arcade.Camera(self.width, self.height)

    # Drawing properties
    _NODE_SIZE = 4
    _NODE_COLOR = arcade.csscolor.RED

    _TEXT_COLOR = arcade.csscolor.BLACK

    _EDGE_WIDTH = 1
    _EDGE_COLOR = arcade.csscolor.BLACK

    def _transform_node(self, node: Vec2) -> Vec2:
        return Vec2(
            x=node.x * self.scale,
            y=self.height - (node.y * self.scale),
        )

    def on_key_press(self, symbol: int, modifiers: int):
        if symbol in [arcade.key.UP, arcade.key.W]:
            self.camera_vel.y += 1.0
        if symbol in [arcade.key.DOWN, arcade.key.S]:
            self.camera_vel.y -= 1.0
        if symbol in [arcade.key.LEFT, arcade.key.A]:
            self.camera_vel.x -= 1.0
        if symbol in [arcade.key.RIGHT, arcade.key.D]:
            self.camera_vel.x += 1.0

    def on_key_release(self, symbol: int, modifiers: int):
        if symbol in [arcade.key.UP, arcade.key.W]:
            self.camera_vel.y -= 1.0
        if symbol in [arcade.key.DOWN, arcade.key.S]:
            self.camera_vel.y += 1.0
        if symbol in [arcade.key.LEFT, arcade.key.A]:
            self.camera_vel.x += 1.0
        if symbol in [arcade.key.RIGHT, arcade.key.D]:
            self.camera_vel.x -= 1.0

    def on_update(self, delta_time: float):
        self.camera_pos = Vec2(
            self.camera_pos.x + self.camera_vel.x * self._CAMERA_SPEED * delta_time,
            self.camera_pos.y + self.camera_vel.y * self._CAMERA_SPEED * delta_time,
        )

        self.camera.move(self.camera_pos)

    def on_draw(self):
        self.clear()

        self.camera.use()

        # Draw the background image if one is loaded
        if self.image:
            self.image.draw()

        # Iterate over all nodes in the graph
        for i, (node, edges) in enumerate(
            zip(self.tilemap.nav_nodes, self.tilemap.nav_edges)
        ):
            nt = self._transform_node(node)
            arcade.draw_circle_filled(
                center_x=nt.x,
                center_y=nt.y,
                radius=self._NODE_SIZE,
                color=self._NODE_COLOR,
            )
            arcade.draw_text(
                text=f"{i}", start_x=nt.x, start_y=nt.y, color=self._TEXT_COLOR
            )
            # Iterate over all connecting edges
            for edge in edges:
                # Find the target node
                target_node = self._transform_node(self.tilemap.nav_nodes[edge])
                # Find the midpoint (edges are one-directional, so ensure both edges are connected)
                midpoint = Vec2((nt.x + target_node.x) / 2, (nt.y + target_node.y) / 2)
                arcade.draw_line(
                    start_x=nt.x,
                    start_y=nt.y,
                    end_x=midpoint.x,
                    end_y=midpoint.y,
                    color=self._EDGE_COLOR,
                    line_width=self._EDGE_WIDTH,
                )


def main():
    if len(sys.argv) < 2:
        print("Missing argument: filename.yaml")
        sys.exit(1)
    filename = sys.argv[1]

    # Load a .yaml file which contains nodes and edges
    tilemap = TileMap(filename=filename)

    # Initialize the viewer with the tilemap
    viewer = NavmeshViewer(tilemap=tilemap)
    # Show viewer
    viewer.setup()
    arcade.run()


if __name__ == "__main__":
    main()

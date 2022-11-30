from engine.mathlib import Vec2, dist
from typing import List
import logging
import yaml

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
        origin_vec = map_data.get("origin", [0, 0])
        self.origin = Vec2(origin_vec[0], origin_vec[1])
        # Map consists of a list of traversible nodes. Nodes are connected NWSE
        self.map = []
        for i, line in enumerate(map_data.get("map", [])):
            y_pos = i + self.origin.y
            for j, tile in enumerate(line):
                if tile == '.':
                    x_pos = j + self.origin.x
                    self.map.append(Vec2(x_pos, y_pos))


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

    def calculate(self, start: Vec2, goal: Vec2) -> List[Vec2]:
        open_list = [AStar.Node(start, goal)]
        closed_list: List[AStar.Node] = []
        while open_list:
            open_list.sort()
            node = open_list.pop()
            if node.pos == goal:
                return node.trace_path()
            # else (goal not reached), add to closed_list list and elaborate
            closed_list.append(node)
            for neighbor in self._neighbors(node, goal):
                # Ignore nodes that are not traversible
                if neighbor.pos not in self.map:
                    continue
                if neighbor in closed_list:
                    self._update_node(node, neighbor, closed_list)
                elif neighbor in open_list:
                    self._update_node(node, neighbor, open_list)
                else:
                    open_list.append(neighbor)
        return [] # No path could be found between start and goal

    def _update_node(self, cur_node: Node, neighbor: Node, node_list: List[Node]) -> None:
        n_idx = node_list.index(neighbor)
        if neighbor.cost < node_list[n_idx].cost:
            node_list[n_idx].cost = neighbor.cost
            node_list[n_idx].parent = cur_node

    def _neighbors(self, node: Node, goal: Vec2) -> List[Node]:
        return [
            # directly adjacent
            AStar.Node(node.pos + Vec2(-1, 0), goal=goal, cost=node.cost+1, parent=node),
            AStar.Node(node.pos + Vec2(1, 0), goal=goal, cost=node.cost+1, parent=node),
            AStar.Node(node.pos + Vec2(0, -1), goal=goal, cost=node.cost+1, parent=node),
            AStar.Node(node.pos + Vec2(0, 1), goal=goal, cost=node.cost+1, parent=node),
            # diagonals
            #AStar.Node(node.pos + Vec2(-1, -1), goal=goal, cost=node.cost+1.4, parent=node),
            #AStar.Node(node.pos + Vec2(1, 1), goal=goal, cost=node.cost+1.4, parent=node),
            #AStar.Node(node.pos + Vec2(-1, 1), goal=goal, cost=node.cost+1.4, parent=node),
            #AStar.Node(node.pos + Vec2(1, -1), goal=goal, cost=node.cost+1.4, parent=node),
        ]


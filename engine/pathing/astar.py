import logging
from typing import List

from engine.mathlib import Vec2, dist

logger = logging.getLogger(__name__)


# f(n) = g(n) + h(n)
class AStar:
    class Node:
        def __init__(self, pos: Vec2, goal: Vec2, cost: float = 0, parent=None) -> None:
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
        raise ValueError  # No path could be found between start and goal

    def _update_node(
        self, cur_node: Node, neighbor: Node, node_list: List[Node]
    ) -> None:
        n_idx = node_list.index(neighbor)
        if neighbor.cost < node_list[n_idx].cost:
            node_list[n_idx].cost = neighbor.cost
            node_list[n_idx].parent = cur_node

    def _neighbors(self, node: Node, goal: Vec2, free_move: bool) -> List[Node]:
        adjacent = []
        # directly adjacent
        node_n = AStar.Node(
            node.pos + Vec2(0, -1), goal=goal, cost=node.cost + 1, parent=node
        )
        node_e = AStar.Node(
            node.pos + Vec2(1, 0), goal=goal, cost=node.cost + 1, parent=node
        )
        node_s = AStar.Node(
            node.pos + Vec2(0, 1), goal=goal, cost=node.cost + 1, parent=node
        )
        node_w = AStar.Node(
            node.pos + Vec2(-1, 0), goal=goal, cost=node.cost + 1, parent=node
        )
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
            node_nw = AStar.Node(
                node.pos + Vec2(-1, -1), goal=goal, cost=node.cost + 1.4, parent=node
            )
            node_ne = AStar.Node(
                node.pos + Vec2(1, -1), goal=goal, cost=node.cost + 1.4, parent=node
            )
            node_se = AStar.Node(
                node.pos + Vec2(1, 1), goal=goal, cost=node.cost + 1.4, parent=node
            )
            node_sw = AStar.Node(
                node.pos + Vec2(-1, 1), goal=goal, cost=node.cost + 1.4, parent=node
            )
            # Ignore nodes that are not traversible
            # Only allow nodes we can easily walk to without hitting stuff in the way (disallow hugging walls)
            if (
                node_nw.pos in self.map
                and node_n.pos in self.map
                and node_w.pos in self.map
            ):
                adjacent.append(node_nw)
            if (
                node_ne.pos in self.map
                and node_n.pos in self.map
                and node_e.pos in self.map
            ):
                adjacent.append(node_ne)
            if (
                node_se.pos in self.map
                and node_s.pos in self.map
                and node_e.pos in self.map
            ):
                adjacent.append(node_se)
            if (
                node_sw.pos in self.map
                and node_s.pos in self.map
                and node_w.pos in self.map
            ):
                adjacent.append(node_sw)
        return adjacent

import logging

from engine.mathlib import Vec2
from engine.pathing.base import Pathing

logger = logging.getLogger(__name__)


# f(n) = g(n) + h(n)
class AStar(Pathing):
    def _neighbors(
        self, node: Pathing.Node, goal: Vec2, free_move: bool
    ) -> list[Pathing.Node]:
        # directly adjacent
        node_n = Pathing.Node(
            node.pos + Vec2(0, -1), goal=goal, cost=node.cost + 1, parent=node
        )
        node_e = Pathing.Node(
            node.pos + Vec2(1, 0), goal=goal, cost=node.cost + 1, parent=node
        )
        node_s = Pathing.Node(
            node.pos + Vec2(0, 1), goal=goal, cost=node.cost + 1, parent=node
        )
        node_w = Pathing.Node(
            node.pos + Vec2(-1, 0), goal=goal, cost=node.cost + 1, parent=node
        )
        # Ignore nodes that are not traversible
        adjacent = [
            node for node in [node_n, node_e, node_s, node_w] if node.pos in self.map
        ]
        # diagonals
        if free_move:
            node_nw = Pathing.Node(
                node.pos + Vec2(-1, -1), goal=goal, cost=node.cost + 1.4, parent=node
            )
            node_ne = Pathing.Node(
                node.pos + Vec2(1, -1), goal=goal, cost=node.cost + 1.4, parent=node
            )
            node_se = Pathing.Node(
                node.pos + Vec2(1, 1), goal=goal, cost=node.cost + 1.4, parent=node
            )
            node_sw = Pathing.Node(
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

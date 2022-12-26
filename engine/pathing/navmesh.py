from engine.mathlib import Vec2, dist
from engine.pathing.base import Pathing

Edges = list[int]


# f(n) = g(n) + h(n)
class NavMesh(Pathing):
    def __init__(self, map_nodes: list[Vec2], edges: list[Edges]) -> None:
        super().__init__(map_nodes=map_nodes)
        self.edges = edges
        assert len(map_nodes) == len(edges)

    def _neighbors(
        self, node: Pathing.Node, goal: Vec2, free_move: bool = False
    ) -> list[Pathing.Node]:
        index = self.map.index(node.pos)
        ret = []
        for node_idx in self.edges[index]:
            target = self.map[node_idx]
            cost = node.cost + dist(node.pos, target)
            ret.append(Pathing.Node(pos=target, goal=goal, cost=cost, parent=node))
        return ret

from typing import Optional

from engine.mathlib import Vec2, dist


# f(n) = g(n) + h(n)
class Pathing:
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
        def trace_path(self, final_pos: Optional[Vec2] = None) -> list[Vec2]:
            cur = self
            ret = []
            while cur.parent:
                ret.append(cur.pos)
                cur = cur.parent
            ret.reverse()
            if final_pos:
                ret.append(final_pos)
            return ret

        def __repr__(self) -> str:
            return f"Node(pos: {self.pos}, cost: {self.cost}, f: {self.f}, parent: {self.parent.pos if self.parent else 'None'})"

    def __init__(self, map_nodes: list[Vec2]) -> None:
        self.map = map_nodes

    def calculate(
        self,
        start: Vec2,
        goal: Vec2,
        final_pos: Optional[Vec2] = None,
        free_move: bool = True,
    ) -> list[Vec2]:
        open_list = [Pathing.Node(start, goal)]
        closed_list: list[Pathing.Node] = []
        while open_list:
            open_list.sort()
            node = open_list.pop()
            if node.pos == goal:
                return node.trace_path(final_pos)
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

    # OVERRIDE
    def _neighbors(self, node: Node, goal: Vec2, free_move: bool) -> list[Node]:
        return []

    def _update_node(
        self, cur_node: Node, neighbor: Node, node_list: list[Node]
    ) -> None:
        n_idx = node_list.index(neighbor)
        if neighbor.cost < node_list[n_idx].cost:
            node_list[n_idx].cost = neighbor.cost
            node_list[n_idx].parent = cur_node

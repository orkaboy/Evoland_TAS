from engine.mathlib import Vec2


class GameEntity2D:
    @property
    def pos(self) -> Vec2:
        return Vec2(0, 0)

    @property
    def rotation(self) -> float:
        return 0.0

    @property
    def in_control(self) -> bool:
        return False


class ZeldaMemory:
    def __init__(self) -> None:
        self.player = GameEntity2D()
        self.actors: list[GameEntity2D] = []

import math
from enum import IntEnum
from typing import NamedTuple

class Vec2(NamedTuple):
    x: float
    y: float

    def __add__(self, other):
        return Vec2(self.x + other.x, self.y + other.y)
    def __sub__(self, other):
        return Vec2(self.x - other.x, self.y - other.y)

    def __repr__(self) -> str:
        return f"Vec2({self.x:0.3f}, {self.y:0.3f})"


def dist(a: Vec2, b: Vec2) -> float:
    dx = b.x - a.x
    dy = b.y - a.y
    return math.sqrt(dx * dx + dy * dy)


def is_close(a: Vec2, b: Vec2, precision: float) -> bool:
    return dist(a, b) <= precision

class Box2(NamedTuple):
    pos: Vec2
    w: float
    h: float

    def __repr__(self) -> str:
        return f"Box[{self.pos}, w: {self.w}, h: {self.h}]"

    def contains(self, pos: Vec2):
        left, top = self.pos.x, self.pos.y
        right, bottom = self.pos.x + self.w, self.pos.y + self.h
        return pos.x >= left and pos.x <= right and pos.y >= top and pos.y <= bottom

    # Top-left, Top-right, Bot-left, Bot-right
    def tl(self) -> Vec2:
        return self.pos
    def tr(self) -> Vec2:
        return Vec2(self.pos.x + self.w, self.pos.y)
    def bl(self) -> Vec2:
        return Vec2(self.pos.x, self.pos.y + self.h)
    def br(self) -> Vec2:
        return Vec2(self.pos.x + self.w, self.pos.y + self.h)

# expand the box by a set amount in all directions
def grow_box(box: Box2, amount: int = 1) -> Box2:
    return Box2(
        pos=Vec2(box.pos.x - amount, box.pos.y - amount),
        w=box.w + 2*amount,
        h=box.h + 2*amount
    )

class Facing(IntEnum):
    LEFT = 0
    RIGHT = 1
    UP = 2
    DOWN = 3

def facing_str(facing: Facing) -> str:
    match facing:
        case Facing.LEFT:
            return "left"
        case Facing.RIGHT:
            return "right"
        case Facing.UP:
            return "up"
        case Facing.DOWN:
            return "down"

def facing_ch(facing: Facing) -> str:
    match facing:
        case Facing.LEFT:
            return "<"
        case Facing.RIGHT:
            return ">"
        case Facing.UP:
            return "^"
        case Facing.DOWN:
            return "v"

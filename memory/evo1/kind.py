from enum import IntEnum


class EKind(IntEnum):
    HERO = 0
    GIRL = 1
    MONSTER = 2
    CHEST = 3
    ITEM = 4
    NPC = 5
    FX = 6  # When breaking pots, closing bars?
    INTERACT = 7
    FIGHTER = 8
    MODEL = 9
    UNKNOWN = 999


# Interactable
class IKind(IntEnum):
    PLATE = 0
    BLOCK = 1
    CRYSTAL = 2
    DOOR = 3
    HOLE = 4
    HOLE2 = 5
    GENERATOR = 6
    FIRE = 7
    WIND = 8
    LIFE = 9
    SEED = 10
    FOUNTAIN = 11
    HEAL = 12
    PUZZLE = 13
    FLAT_CHEST = 14
    PLATE_HOLE = 15
    SWITCH_CRYSTAL = 16
    STATIC_FIRE = 17
    GOLD = 18
    LIFE_GLOBE = 19
    HACK_ITEM = 20
    GATE_CHAINS = 21
    ARROW = 22
    FIRE_ARROW = 23
    PORTAL = 24
    ENTRANCE_GIRL = 25
    BOMB = 26
    BOSS_DOOR = 27
    MANA_TREE = 28
    SAVE_POINT = 29
    AIR_SHIP = 30
    UNKNOWN = 999


# TODO: Could maybe be a dict instead
def IKindToChar(ikind: IKind) -> str:
    match ikind:
        case IKind.PLATE:
            return "P"
        case IKind.BLOCK:
            return "B"
        case IKind.CRYSTAL:
            return "C"
        case IKind.DOOR:
            return "D"
        case IKind.HOLE:
            return "0"
        case IKind.HOLE2:
            return "0"
        case IKind.GENERATOR:
            return "G"
        case IKind.FIRE:  # Fireballs
            return "*"
        case IKind.WIND:
            return "W"
        case IKind.LIFE:
            return "L"
        case IKind.SEED:
            return "S"
        case IKind.FOUNTAIN:
            return "F"
        case IKind.HEAL:
            return "H"
        case IKind.PUZZLE:
            return "?"
        case IKind.FLAT_CHEST:
            return "C"
        case IKind.PLATE_HOLE:
            return "P"
        case IKind.SWITCH_CRYSTAL:
            return "C"
        case IKind.STATIC_FIRE:
            return "F"
        case IKind.GOLD:
            return "$"
        case IKind.LIFE_GLOBE:
            return "L"
        case IKind.HACK_ITEM:
            return "€"
        case IKind.GATE_CHAINS:
            return "~"
        case IKind.ARROW:
            return "-"
        case IKind.FIRE_ARROW:
            return "+"
        case IKind.PORTAL:
            return "P"
        case IKind.ENTRANCE_GIRL:
            return "&"
        case IKind.BOMB:
            return "B"
        case IKind.BOSS_DOOR:
            return "D"
        case IKind.MANA_TREE:
            return "M"
        case IKind.SAVE_POINT:
            return "S"
        case IKind.AIR_SHIP:
            return "A"


# Monster
class MKind(IntEnum):
    OCTOROC = 0
    ARMOS = 1
    BAT = 2
    OCTOROC_ARMOR = 3
    SKELETON = 4
    RED_MAGE = 5
    DARK_CLINK = 6
    WASP = 7
    CHAMPI = 8
    SPIDER = 9
    WORM = 10
    LICH = 11
    UNKNOWN = -1


# TODO: Could maybe be a dict instead
def MKindToChar(mkind: MKind) -> str:
    match mkind:
        case MKind.OCTOROC:
            return "¤"
        case MKind.ARMOS:
            return "A"
        case MKind.BAT:
            return "B"
        case MKind.OCTOROC_ARMOR:
            return "¤"
        case MKind.SKELETON:
            return "S"
        case MKind.RED_MAGE:
            return "M"
        case MKind.DARK_CLINK:
            return "D"
        case MKind.WASP:
            return "W"
        case MKind.CHAMPI:
            return "c"
        case MKind.SPIDER:
            return "s"
        case MKind.WORM:
            return "w"
        case MKind.LICH:
            return "L"
        case _:
            return "!"

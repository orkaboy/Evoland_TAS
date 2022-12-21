from engine.combat import SeqMove2DClunkyCombat
from engine.mathlib import Facing, Vec2
from engine.move2d import SeqGrabChestKeyItem, SeqMove2D
from engine.seq import SeqAttack, SeqDelay, SeqList, SeqMenu
from evo1.combat.weapons import SeqPlaceBomb, SeqSwapWeapon
from evo1.move2d import SeqZoneTransition
from maps.evo1 import GetAStar
from memory.evo1 import Evo1Weapon, MapID

_sg_astar = GetAStar(MapID.SACRED_GROVE_2D)


class SacredGrove(SeqList):
    def __init__(self):
        super().__init__(
            name="Sacred Grove",
            children=[
                # Start at the entrance of Sacred Grove
                SeqSwapWeapon("Bombs", new_weapon=Evo1Weapon.BOMB),
                SeqPlaceBomb(
                    "Rocks",
                    target=Vec2(14.2, 38),
                    use_menu_glitch=True,
                    swap_to_sword=True,
                ),
                SeqMove2DClunkyCombat(
                    "Move to crystal",
                    coords=_sg_astar.calculate(start=Vec2(14, 38), goal=Vec2(30, 41)),
                ),
                SeqSwapWeapon("Bombs", new_weapon=Evo1Weapon.BOMB),
                SeqPlaceBomb("Crystal", target=Vec2(30, 41)),
                SeqSwapWeapon("Sword", new_weapon=Evo1Weapon.SWORD),
                SeqMove2DClunkyCombat(
                    "Move to crystal",
                    coords=_sg_astar.calculate(start=Vec2(30, 41), goal=Vec2(15, 27)),
                ),
                SeqAttack("Bush"),
                SeqMove2D("Move to crystal", coords=[Vec2(13, 27)]),
                SeqAttack("Crystal"),
                SeqMove2DClunkyCombat(
                    "Move to dungeon",
                    coords=_sg_astar.calculate(start=Vec2(15, 27), goal=Vec2(14, 18)),
                ),
                SeqZoneTransition(
                    "Bow dungeon",
                    direction=Facing.UP,
                    target_zone=MapID.SACRED_GROVE_CAVE_1,
                ),
                # Do the bow cave
                BowCave(),
                SeqMove2DClunkyCombat(
                    "Move to crystal",
                    coords=_sg_astar.calculate(start=Vec2(14, 18), goal=Vec2(17, 27)),
                ),
                # Turn left
                SeqMove2D("Move to crystal", coords=[Vec2(16.8, 27)], precision=0.1),
                # TODO: Slightly more efficient to swap when warping earlier
                SeqSwapWeapon("Bow", new_weapon=Evo1Weapon.BOW),
                SeqAttack("Shoot crystal"),
                # TODO: Menu glitch to skip past dimension stone (verify)
                SeqMenu("Menu skip"),
                SeqDelay("Menu skip", timeout_in_s=0.8),
                SeqMenu("Menu skip"),
                SeqMove2D("Skip dimension stone", coords=[Vec2(17, 22)]),
                # TODO: Solve puzzles in sacred grove
                # TODO: Fight skeletons and mages
                # TODO: Grab first part of amulet, then exit to the south
            ],
        )


class BowCave(SeqList):
    def __init__(self):
        super().__init__(
            name="Bow dungeon",
            children=[
                SeqMove2DClunkyCombat(
                    "Maze",
                    coords=_sg_astar.calculate(
                        start=Vec2(12, 26), goal=Vec2(12, 17), final_pos=Vec2(12, 17.4)
                    ),
                ),
                SeqGrabChestKeyItem("Bow", direction=Facing.DOWN),
                # TODO: Need to move, and detect the teleport to entrance
                # SeqMove2D("Warp"), # TODO: Slightly faster to move left/right
                SeqZoneTransition(
                    "Sacred Grove",
                    direction=Facing.DOWN,
                    target_zone=MapID.SACRED_GROVE_3D,
                ),
            ],
        )

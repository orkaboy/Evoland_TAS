import contextlib
from enum import Enum, auto
from typing import Optional

from control import evo_ctrl
from engine.combat import SeqMove2DClunkyCombat
from engine.mathlib import Facing, Vec2, dist, is_close
from engine.move2d import (
    SeqGrabChestKeyItem,
    SeqMove2D,
    SeqMove2DConfirm,
    SeqSection2D,
    move_to,
)
from engine.seq import (
    SeqAttack,
    SeqCheckpoint,
    SeqDelay,
    SeqList,
    SeqMenu,
    wait_seconds,
)
from evo1.combat.weapons import SeqPlaceBomb, SeqSwapWeapon
from evo1.move2d import SeqZoneTransition
from maps.evo1 import GetNavmap
from memory.evo1 import (
    EKind,
    Evo1GameEntity2D,
    Evo1Weapon,
    IKind,
    MapID,
    MKind,
    get_zelda_memory,
)

_sg_astar = GetNavmap(MapID.SACRED_GROVE_2D)
_bow_astar = GetNavmap(MapID.SACRED_GROVE_CAVE_1)
_amulet_astar = GetNavmap(MapID.SACRED_GROVE_CAVE_2)


class SacredGrove(SeqList):
    def __init__(self):
        super().__init__(
            name="Sacred Grove",
            children=[
                # Start at the entrance of Sacred Grove
                SacredGroveToBowCave(),
                # Acquire bow
                BowCave(),
                SacredGroveToAmuletCave(),
                # Grab first part of amulet, then exit to the south
                AmuletCave(),
                SacredGroveToExit(),
            ],
        )


class SacredGroveToBowCave(SeqList):
    def __init__(self):
        super().__init__(
            name="Navigate to bow dungeon",
            children=[
                # Start at the entrance of Sacred Grove
                SeqMove2D("Move to rocks", coords=[Vec2(13, 38)]),
                SeqSwapWeapon("Bombs", new_weapon=Evo1Weapon.BOMB),
                SeqPlaceBomb(
                    "Rocks",
                    target=Vec2(14.2, 38),
                    use_menu_glitch=True,
                    swap_to_sword=True,
                    precision=0.1,
                ),
                SeqMove2DClunkyCombat(
                    "Move to crystal",
                    coords=_sg_astar.calculate(start=Vec2(14, 38), goal=Vec2(30, 41)),
                ),
                SeqAttack("Crystal"),
                # TODO: Slightly suboptimal movement here
                # SeqSwapWeapon("Bombs", new_weapon=Evo1Weapon.BOMB),
                # SeqPlaceBomb("Crystal", target=Vec2(30, 41), precision=0.1),
                # SeqSwapWeapon("Sword", new_weapon=Evo1Weapon.SWORD),
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
            ],
        )


class BowCave(SeqList):
    def __init__(self):
        super().__init__(
            name="Bow dungeon",
            children=[
                SeqMove2DClunkyCombat(
                    "Maze",
                    coords=_bow_astar.calculate(
                        start=Vec2(12, 26), goal=Vec2(12, 17), final_pos=Vec2(12, 17.4)
                    ),
                ),
                SeqGrabChestKeyItem("Bow", direction=Facing.DOWN),
                # SeqMove2D("Warp"), # TODO: Slightly faster to move left/right
                SeqZoneTransition(
                    "Sacred Grove",
                    direction=Facing.DOWN,
                    target_zone=MapID.SACRED_GROVE_3D,
                ),
            ],
        )


class SacredGroveToAmuletCave(SeqList):
    def __init__(self):
        super().__init__(
            name="Navigate to amulet dungeon",
            children=[
                # TODO: Can fail here if the bats force us back into the bow cave
                SeqMove2DClunkyCombat(
                    "Move to crystal",
                    coords=_sg_astar.calculate(start=Vec2(14, 18), goal=Vec2(17, 27)),
                ),
                # Turn left
                SeqMove2D("Move to crystal", coords=[Vec2(16.7, 27)], precision=0.1),
                # TODO: Slightly more efficient to swap when warping earlier
                SeqSwapWeapon("Bow", new_weapon=Evo1Weapon.BOW),
                SeqAttack("Shoot crystal"),
                SeqMenu("Menu skip"),
                SeqDelay("Menu skip", timeout_in_s=0.8),
                SeqMenu("Menu skip"),
                SeqMove2D("Skip dimension stone", coords=[Vec2(17, 22)]),
                # TODO: Suboptimal, if we just swap to bombs and navigate this is quicker
                SeqSwapWeapon("Sword", new_weapon=Evo1Weapon.SWORD),
                SeqMove2DClunkyCombat(
                    "Move to crystal",
                    coords=_sg_astar.calculate(start=Vec2(17, 22), goal=Vec2(24, 18)),
                ),
                SeqSwapWeapon("Bomb", new_weapon=Evo1Weapon.BOMB),
                SeqPlaceBomb("Crystal", target=Vec2(24, 18)),
                # TODO: This can fail if we get hit by the bat
                # SeqAttack("Crystal"),
                SeqMove2D(
                    "Skip dimension tree",
                    coords=_sg_astar.calculate(start=Vec2(24, 18), goal=Vec2(27, 21)),
                ),
                # TODO: Suboptimal, if we just swap to bow this is quicker
                SeqSwapWeapon("Sword", new_weapon=Evo1Weapon.SWORD),
                SeqMove2DClunkyCombat(
                    "Move to crystal",
                    coords=_sg_astar.calculate(
                        start=Vec2(27, 21), goal=Vec2(49, 27), final_pos=Vec2(48.6, 27)
                    ),
                ),
                SeqSwapWeapon("Bow", new_weapon=Evo1Weapon.BOW),
                SeqAttack("Crystal"),
                # TODO: Suboptimal, if we just keep bow this is quicker?
                SeqSwapWeapon("Sword", new_weapon=Evo1Weapon.SWORD),
                SeqMove2DClunkyCombat(
                    "Move to bush",
                    coords=_sg_astar.calculate(start=Vec2(49, 27), goal=Vec2(60, 32)),
                ),
                SeqAttack("Bush"),
                SeqMove2D("Move to bush", coords=[Vec2(60, 33)]),
                SeqAttack("Bush"),
                SeqMove2D("Move to bush", coords=[Vec2(60, 34)]),
                SeqAttack("Bush"),
                SeqMove2DClunkyCombat(
                    "Move to bush",
                    coords=_sg_astar.calculate(
                        start=Vec2(60, 35), goal=Vec2(61, 38), final_pos=Vec2(61, 39)
                    ),
                ),
                SeqAttack("Bush"),
                SeqMove2DClunkyCombat(
                    "Move to bush",
                    coords=_sg_astar.calculate(
                        start=Vec2(61, 39), goal=Vec2(70, 37), final_pos=Vec2(70, 37.3)
                    ),
                ),
                SeqAttack("Bush"),
                SeqMove2D("Move to bush", coords=[Vec2(70, 38)]),
                SeqAttack("Bush"),
                SeqMove2D("Move to bush", coords=[Vec2(70, 39)]),
                SeqAttack("Bush"),
                SeqMove2D("Move to bush", coords=[Vec2(70, 40)]),
                SeqMove2D(
                    "Move to bush",
                    coords=_sg_astar.calculate(start=Vec2(70, 40), goal=Vec2(67, 42)),
                ),
                SeqAttack("Bush"),
                SeqMove2D(
                    "Move to bush",
                    coords=_sg_astar.calculate(
                        start=Vec2(66, 42), goal=Vec2(65, 40), final_pos=Vec2(64.7, 40)
                    ),
                ),
                SeqAttack("Bush"),
                SeqSwapWeapon("Bow", new_weapon=Evo1Weapon.BOW),
                # TODO: Need verification that we hit in this section. Check if any enemies died instead
                SeqAttack("Light fire"),
                SeqSwapWeapon("Sword", new_weapon=Evo1Weapon.SWORD),
                SeqMove2D(
                    "Move to bush",
                    coords=_sg_astar.calculate(
                        start=Vec2(65, 40), goal=Vec2(63, 42), final_pos=Vec2(63, 41.7)
                    ),
                ),
                SeqAttack("Bush"),
                SeqSwapWeapon("Bow", new_weapon=Evo1Weapon.BOW),
                # TODO: Need verification that we hit in this section. Check if any enemies died instead
                SeqAttack("Light fire"),
                SeqSwapWeapon("Sword", new_weapon=Evo1Weapon.SWORD),
                SeqMove2D(
                    "Move to bush",
                    coords=_sg_astar.calculate(
                        start=Vec2(63, 42), goal=Vec2(60, 42), final_pos=Vec2(60.4, 42)
                    ),
                ),
                SeqMove2D("Move to bush", coords=[Vec2(60.3, 41.7)], precision=0.05),
                SeqAttack("Bush"),
                SeqSwapWeapon("Bow", new_weapon=Evo1Weapon.BOW),
                # TODO: Need verification that we hit in this section. Check if any enemies died instead
                SeqAttack("Light fire"),
                SeqMove2D(
                    "Line up shot",
                    coords=[Vec2(60.4, 42), Vec2(60.4, 41.7)],
                    precision=0.05,
                ),
                # TODO: Need verification that we hit in this section. Check if any enemies died instead
                SeqAttack("Light fire"),
                SeqMove2D(
                    "Move to crystal",
                    coords=_sg_astar.calculate(
                        start=Vec2(60, 42), goal=Vec2(65, 42), final_pos=Vec2(65, 41.7)
                    ),
                ),
                SeqAttack("Crystal"),
                SeqMenu("Menu glitch"),
                SeqDelay("Menu glitch", timeout_in_s=0.5),
                SeqMenu("Menu glitch"),
                SeqMove2D(
                    "Move past bushes",
                    coords=[Vec2(68, 42), Vec2(68, 40), Vec2(70, 40), Vec2(70, 37)],
                ),
                # TODO: Suboptimal, keep bow
                SeqSwapWeapon("Sword", new_weapon=Evo1Weapon.SWORD),
                SeqMove2DClunkyCombat(
                    "Move to cave",
                    coords=_sg_astar.calculate(start=Vec2(70, 37), goal=Vec2(60, 36)),
                ),
                SeqMove2DClunkyCombat(
                    "Move to cave",
                    coords=_sg_astar.calculate(start=Vec2(60, 33), goal=Vec2(59, 27)),
                ),
                SeqMove2D(
                    "Move to cave",
                    coords=[Vec2(62, 27)],
                ),
                SeqZoneTransition(
                    "Amulet cave",
                    direction=Facing.UP,
                    target_zone=MapID.SACRED_GROVE_CAVE_2,
                ),
            ],
        )


class KillMages(SeqSection2D):
    class _FightFSM(Enum):
        HUNT = auto()
        BOMB = auto()

    def __init__(self):
        super().__init__("Kill mages")
        self.state = self._FightFSM.HUNT

    def reset(self):
        self.state = self._FightFSM.HUNT

    def execute(self, delta: float) -> bool:
        # Track mages
        with contextlib.suppress(ReferenceError):
            target = self._get_next_target()
            # Check if we are done
            if not target:
                self._equip_sword()
                return True

            ctrl = evo_ctrl()
            mem = get_zelda_memory()
            player_pos = mem.player.pos
            target_pos = target.pos

            # TODO: Does not account for spikes
            match self.state:
                case self._FightFSM.HUNT:
                    # Move to mage
                    move_to(player=player_pos, target=target_pos, precision=0.2)
                    # If we are close to mage, place a bomb
                    if is_close(player_pos, target_pos, precision=1.2):
                        ctrl.attack(tapping=True)
                        ctrl.menu(tapping=True)
                        # Allow time for bomb to spawn
                        self.state = self._FightFSM.BOMB
                case self._FightFSM.BOMB:
                    # Wait for bomb to explode
                    for actor in mem.actors:
                        if actor.kind == EKind.INTERACT and actor.ikind == IKind.BOMB:
                            return False
                    # Did not find a bomb, go back to hunting mages
                    self.state = self._FightFSM.HUNT
                    # Close menu
                    ctrl.menu()

        # Continue when there are no more mages
        return False

    def _equip_sword(self) -> None:
        ctrl = evo_ctrl()
        # Assume menu is open
        ctrl.dpad.none()
        # Select sword from bombs
        ctrl.dpad.tap_left()
        ctrl.dpad.tap_left()
        # Confirm selection
        ctrl.confirm(tapping=True)
        # Open menu again to keep sword and menu glitch
        ctrl.menu()

    # TODO: Can fail to correctly detect mages (investigate if they are always in memory)
    def _get_next_target(self) -> Optional[Evo1GameEntity2D]:
        mem = get_zelda_memory()
        player_pos = mem.player.pos
        # Using key sorting, order actors by closest to player, filtering out mages
        key_list = [
            (dist(player_pos, actor.pos), actor)
            for actor in mem.actors
            if actor.kind == EKind.MONSTER and actor.mkind == MKind.RED_MAGE
        ]
        return sorted_list[0][1] if (sorted_list := sorted(key_list)) else None

    def __repr__(self) -> str:
        return f"{self.name} ({self.state.name})"


class AmuletCaveFight(SeqList):
    def __init__(self):
        super().__init__(
            name="Skeleton and Mage fight",
            children=[
                # TODO: Sequence will fail if did not manage to get skip
                # TODO: Sequence can fail if mages are mean
                SeqMove2D(
                    "Move to first skeleton",
                    coords=[Vec2(25, 21), Vec2(24, 21)],
                ),
                SeqAttack("Skeleton"),
                SeqMove2D(
                    "Move to second skeleton",
                    coords=[Vec2(23, 20), Vec2(23, 18)],
                ),
                SeqAttack("Skeleton"),
                SeqMove2D(
                    "Move to third skeleton",
                    coords=[Vec2(23, 17.5), Vec2(22.5, 17), Vec2(20.5, 17)],
                ),
                SeqAttack("Skeleton"),
                SeqMove2D(
                    "Move to last skeleton",
                    coords=[Vec2(19.5, 17), Vec2(19, 17.5), Vec2(19, 20)],
                ),
                SeqAttack("Skeleton"),
                SeqSwapWeapon("Bombs", Evo1Weapon.BOMB),
                KillMages(),
                # TODO: Should end this section with sword equipped and menu open
                SeqMove2D(
                    "Leave cave",
                    coords=_amulet_astar.calculate(
                        start=Vec2(19, 20), goal=Vec2(14, 20)
                    ),
                ),
            ],
        )


class AmuletCave(SeqList):
    def __init__(self):
        super().__init__(
            name="Amulet dungeon",
            children=[
                # Checkpoint at start of amulet cave
                SeqCheckpoint(checkpoint_name="amulet_cave"),
                # Push blocks (room with bats)
                SeqMove2DClunkyCombat(
                    "Move to push block(N)",
                    coords=_amulet_astar.calculate(
                        start=Vec2(4, 20), goal=Vec2(11, 18), final_pos=Vec2(11, 17.3)
                    ),
                ),
                SeqMove2DClunkyCombat(
                    "Move to push block(S)",
                    coords=_amulet_astar.calculate(
                        start=Vec2(11, 17), goal=Vec2(11, 22)
                    ),
                ),
                SeqSwapWeapon("Bow", Evo1Weapon.BOW),
                SeqMove2D(
                    "Move to push block(S)",
                    coords=[Vec2(11, 22.5)],
                ),
                SeqMove2D(
                    "Move to door",
                    coords=_amulet_astar.calculate(
                        start=Vec2(11, 22),
                        goal=Vec2(12, 21),
                        final_pos=Vec2(12.5, 20.5),
                    ),
                ),
                SeqMenu("Menu glitch"),
                SeqDelay("Menu glitch", timeout_in_s=0.5),
                SeqMenu("Menu glitch"),
                SeqMove2D(
                    "Move to chest",
                    coords=_amulet_astar.calculate(
                        start=Vec2(12, 21), goal=Vec2(16, 20)
                    ),
                ),
                SeqMenu("Menu glitch"),
                SeqMove2D(
                    "Move to chest",
                    coords=_amulet_astar.calculate(
                        start=Vec2(16, 20), goal=Vec2(18, 20)
                    ),
                ),
                SeqMenu("Menu glitch"),
                # Grab amulet
                SeqMove2D(
                    "Move to chest",
                    coords=_amulet_astar.calculate(
                        start=Vec2(18, 20), goal=Vec2(26, 20)
                    ),
                ),
                SeqGrabChestKeyItem("Amulet", direction=Facing.RIGHT, manip=True),
                AmuletCaveFight(),
                # Leave cave
                SeqMove2DClunkyCombat(
                    "Move to exit",
                    coords=_amulet_astar.calculate(
                        start=Vec2(14, 20), goal=Vec2(4, 20)
                    ),
                ),
                # Leaving with menu open
                SeqZoneTransition(
                    "Sacred Grove",
                    direction=Facing.LEFT,
                    target_zone=MapID.SACRED_GROVE_3D,
                ),
            ],
        )


class SacredGroveBombSelect(SeqSection2D):
    def __init__(self):
        super().__init__(name="Bomb select")

    def execute(self, delta: float) -> bool:
        ctrl = evo_ctrl()
        ctrl.dpad.none()
        ctrl.dpad.tap_right()
        ctrl.confirm()
        # Wait for transition to complete before trying to place bomb
        wait_seconds(2.5)
        return True


class SacredGroveToExit(SeqList):
    def __init__(self):
        super().__init__(
            name="Leave area",
            children=[
                SeqMove2DClunkyCombat(
                    "Move to crystal",
                    coords=_sg_astar.calculate(start=Vec2(62, 27), goal=Vec2(53, 32)),
                ),
                # Activate crystal with sword
                SeqAttack("Crystal"),
                # In order for this timing to work, need to carry menu skip and close
                SacredGroveBombSelect(),
                # Use bomb to skip puzzle
                SeqPlaceBomb("Crystal", target=Vec2(53, 32.3), precision=0.1),
                SeqMove2D(
                    "Move to exit",
                    coords=_sg_astar.calculate(start=Vec2(53, 32), goal=Vec2(51, 34)),
                ),
                SeqSwapWeapon("Sword", Evo1Weapon.SWORD),
                # Move to south exit
                SeqMove2DClunkyCombat(
                    "Move to exit",
                    coords=_sg_astar.calculate(start=Vec2(51, 34), goal=Vec2(47, 40)),
                ),
                # Skip past dialog and leave for world map
                SeqMove2DConfirm(
                    "Move to exit",
                    coords=_sg_astar.calculate(start=Vec2(47, 40), goal=Vec2(47, 43)),
                ),
                SeqZoneTransition(
                    "Overworld",
                    direction=Facing.DOWN,
                    target_zone=MapID.OVERWORLD,
                ),
            ],
        )

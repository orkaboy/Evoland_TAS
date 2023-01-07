import contextlib
import logging
from enum import Enum, auto
from typing import Optional

from control import evo_ctrl
from engine.mathlib import Facing, Vec2, dist, is_close
from engine.move2d import SeqGrabChest, SeqMove2D, SeqMove2DCancel, move_to
from engine.seq import SeqBase, SeqDelay, SeqInteract, SeqList
from evo1.atb import (
    Encounter,
    EncounterID,
    FarmingGoal,
    SeqATBmove2D,
    calc_next_encounter,
)
from evo1.move2d import SeqZoneTransition
from evo1.route.aogai import AogaiWrongWarp
from maps.evo1 import GetNavmap
from memory.evo1 import EKind, IKind, MapID, get_memory, get_zelda_memory
from memory.rng import EvolandRNG
from term.window import WindowLayout

_overworld_astar = GetNavmap(MapID.OVERWORLD)

logger = logging.getLogger(__name__)


class OverworldGliFarm(SeqATBmove2D):
    def __init__(
        self,
        name: str,
        coords: list[Vec2],
        goal: FarmingGoal = None,
        precision: float = 0.2,
    ):
        super().__init__(name=name, coords=coords, goal=goal, precision=precision)
        self.manip_state = self._MANIP_FSM.CAN_MANIP
        self.manipulated_enc: Optional[Encounter] = None

    def reset(self) -> None:
        self.manip_state = self._MANIP_FSM.CAN_MANIP
        self.manipulated_enc = None
        super().reset()

    _CHEST_LOCATION = Vec2(84, 46)
    _CHEST_RNG_ADVANCE = 66  # Ticks the rng forward 66 steps
    _GLI_PER_ENEMY = 50

    def _should_manip(self) -> bool:
        # self.next_enc already calculated
        next_nr_enemies = len(self.next_enc.enemies)
        manip_nr_enemies = len(self.manipulated_enc.enemies)

        next_gli = next_nr_enemies * self._GLI_PER_ENEMY
        manip_gli = manip_nr_enemies * self._GLI_PER_ENEMY

        gli_remaining = self.goal.gli_goal - get_memory().gli
        # TODO: Check if this logic is sound
        # The idea is that if both encounters are able to get us to the goal, prefer the easier one
        # Fewer enemies are generally easier
        # Doing the manip is generally worse
        if gli_remaining <= 0:
            # Don't manip if we're already done farming
            return False
        elif (
            self.next_enc.enc_id == EncounterID.EMUK
            and self.manipulated_enc.enc_id == EncounterID.SLIME
        ):
            # Slime is generally faster than emuk
            return True
        elif next_gli >= gli_remaining and manip_gli >= gli_remaining:
            # If both encounters fill up the gli, prefer the fewer enemies
            return manip_gli < next_gli
        else:
            # Else, go for the encounter that gives the most gli
            return manip_gli > next_gli

    class _MANIP_FSM(Enum):
        CAN_MANIP = auto()
        STARTED_MANIP = auto()
        MANIP_DONE = auto()

    # Returning true means we seize control instead of moving on
    def do_encounter_manip(self) -> bool:
        # Update the next expected encounter
        self.calc_next_encounter(small_sword=True)
        # Check if we are done farming
        if self._farm_done():
            return False

        player = get_zelda_memory().player
        # Check if we can/should manipulate
        match self.manip_state:
            case self._MANIP_FSM.CAN_MANIP:
                # Check if we are outside range of the chest for next enc
                dist_to_chest = dist(player.pos, self._CHEST_LOCATION)
                if not dist_to_chest < player.encounter_timer:
                    return False

                # Calculate the manipulated encounter
                rng = EvolandRNG().get_rng()
                rng.advance_rng(self._CHEST_RNG_ADVANCE)
                self.manipulated_enc = calc_next_encounter(rng, clink_level=0)

                if not self._should_manip():
                    return False
                # Initiate the manip
                logger.info(
                    f"Picking up chest to forward rng. {self.manipulated_enc} is better than {self.next_enc}"
                )
                self.manip_state = self._MANIP_FSM.STARTED_MANIP
            case self._MANIP_FSM.STARTED_MANIP:
                # Move towards chest to manip
                move_to(
                    player=player.pos,
                    target=self._CHEST_LOCATION,
                    precision=self.precision,
                )
                # Check if we've picked up chest, manip done
                if self.manipulated_enc == self.next_enc or is_close(
                    player.pos, self._CHEST_LOCATION, precision=self.precision
                ):
                    logger.info(f"Manip finished. Next encounter is {self.next_enc}")
                    self.manip_state = self._MANIP_FSM.MANIP_DONE
                    return False
            # Check if we've already picked up the chest
            case self._MANIP_FSM.MANIP_DONE:
                return False

        return True

    def render(self, window: WindowLayout) -> None:
        super().render(window=window)
        if (
            not self.battle_handler.active
            and self.manip_state != self._MANIP_FSM.MANIP_DONE
            and self.manipulated_enc
        ):
            window.stats.addstr(Vec2(1, 14), f" Manip: {self.manipulated_enc}")


class OverworldToMeadow(SeqList):
    def __init__(self):
        super().__init__(
            name="Overworld",
            children=[
                SeqMove2D(
                    "Pick up encounters",
                    coords=[
                        Vec2(79.1, 55.5),
                        # Nudge chest (encounters) at (79, 54)
                        # TODO: Improve nudge to avoid stopping
                        Vec2(80, 55),
                    ],
                ),
                # Battle handler for random battles, mashing confirm is fine for now
                OverworldGliFarm(
                    "Navigating overworld",
                    coords=[
                        Vec2(85, 47),
                        Vec2(87, 43),
                    ],
                    # Need to farm gli before progressing. We need 250 to buy gear, and we can get 50 in the village
                    goal=FarmingGoal(
                        farm_coords=[Vec2(87, 44), Vec2(87, 43)],
                        precision=0.2,
                        gli_goal=200,
                    ),
                ),
                SeqZoneTransition(
                    "Meadow", direction=Facing.UP, target_zone=MapID.MEADOW
                ),
            ],
        )


class OverworldToCavern(SeqList):
    def __init__(self):
        super().__init__(
            name="Overworld",
            children=[
                # Grab the forced combat chest and rescue/name Kaeris
                SeqATBmove2D(
                    "Picking up Kaeris",
                    coords=_overworld_astar.calculate(
                        start=Vec2(87, 40), goal=Vec2(79, 35)
                    ),
                    forced=True,
                ),
                # Move into the caverns
                SeqZoneTransition(
                    "Crystal Cavern",
                    direction=Facing.UP,
                    target_zone=MapID.CRYSTAL_CAVERN,
                ),
            ],
        )


class OverworldToNoria(SeqList):
    def __init__(self):
        super().__init__(
            name="Overworld",
            children=[
                SeqMove2D(
                    "Move to chest",
                    coords=_overworld_astar.calculate(
                        start=Vec2(79, 73), goal=Vec2(78, 76)
                    ),
                ),
                SeqGrabChest("Perspective", direction=Facing.LEFT),
                SeqMove2D(
                    "Move to mines",
                    coords=_overworld_astar.calculate(
                        start=Vec2(78, 76), goal=Vec2(75, 79)
                    ),
                ),
                SeqZoneTransition(
                    "Noria Mines", direction=Facing.LEFT, target_zone=MapID.NORIA_CLOSED
                ),
            ],
        )


class OverworldToAogai(SeqList):
    def __init__(self):
        super().__init__(
            name="Overworld",
            children=[
                SeqMove2D(
                    "Performing skip",
                    coords=[Vec2(75, 84.97), Vec2(78, 84.97)],
                    precision=0.03,
                ),
                # Navigate to Aogai village
                SeqMove2D(
                    "Moving to Aogai",
                    coords=_overworld_astar.calculate(
                        start=Vec2(78, 85), goal=Vec2(95, 93)
                    ),
                ),
                SeqZoneTransition(
                    "Aogai village", direction=Facing.UP, target_zone=MapID.AOGAI
                ),
            ],
        )


class OverworldToSacredGrove(SeqList):
    def __init__(self):
        super().__init__(
            name="Overworld",
            children=[
                SeqMove2D(
                    "Moving to Sacred Grove",
                    coords=_overworld_astar.calculate(
                        start=Vec2(95, 93), goal=Vec2(96, 100)
                    ),
                ),
                SeqZoneTransition(
                    "Sacred Grove",
                    direction=Facing.RIGHT,
                    target_zone=MapID.SACRED_GROVE_3D,
                ),
            ],
        )


class SacredGroveToAogai(SeqList):
    def __init__(self):
        super().__init__(
            name="Overworld",
            children=[
                SeqMove2D(
                    "Moving to Aogai",
                    coords=_overworld_astar.calculate(
                        start=Vec2(96, 100), goal=Vec2(95, 93)
                    ),
                ),
                SeqZoneTransition(
                    "Aogai village", direction=Facing.UP, target_zone=MapID.AOGAI
                ),
            ],
        )


class OverworldToSarudnahk(SeqList):
    def __init__(self):
        super().__init__(
            name="Overworld",
            children=[
                SeqMove2D(
                    "Moving to Sarudnahk",
                    coords=_overworld_astar.calculate(
                        start=Vec2(95, 91), goal=Vec2(100, 77)
                    ),
                ),
                SeqZoneTransition(
                    "Sarudnahk",
                    direction=Facing.UP,
                    target_zone=MapID.SARUDNAHK,
                ),
            ],
        )


class BlackCitadelMenuGlitch(SeqBase):
    def __init__(self) -> None:
        super().__init__("Menu glitch")

    def execute(self, delta: float) -> bool:
        ctrl = evo_ctrl()
        ctrl.menu(tapping=True)
        ctrl.confirm()
        ctrl.dpad.right()
        return True


class OverworldToBlackCitadel(SeqList):
    def __init__(self):
        super().__init__(
            name="Overworld",
            children=[
                SeqMove2D(
                    "Moving to Black Citadel",
                    coords=_overworld_astar.calculate(
                        start=Vec2(95, 91), goal=Vec2(117, 88)
                    ),
                ),
                # Menu glitch and trigger Zephyros fight
                BlackCitadelMenuGlitch(),
                SeqDelay("Going into tower", timeout_in_s=1.0),
            ],
        )


class BlackCitadelToAogai(SeqList):
    def __init__(self):
        super().__init__(
            name="Overworld",
            children=[
                SeqMove2D(
                    "Moving to Aogai",
                    coords=_overworld_astar.calculate(
                        start=Vec2(116, 88), goal=Vec2(95, 91)
                    ),
                ),
                SeqMove2D(  # Adjusting to be slightly faster
                    "Adjust position",
                    coords=[Vec2(95, 91.4)],
                ),
                AogaiWrongWarp("Aogai"),
            ],
        )


class WaitForAirshipToSpawn(SeqBase):
    _TOGGLE_TIMEOUT = 0.2

    def __init__(self):
        super().__init__(name="Wait for airship to spawn")
        self.toggle_state = False
        self.toggle_time = 0

    def reset(self) -> None:
        self.toggle_state = False
        self.toggle_time = 0

    def execute(self, delta: float) -> bool:
        ctrl = evo_ctrl()
        ctrl.set_neutral()
        mem = get_zelda_memory()
        # Wait for airship to spawn (check for entity type)
        with contextlib.suppress(ReferenceError):
            for actor in mem.actors:
                if actor.kind == EKind.INTERACT and actor.ikind == IKind.AIR_SHIP:
                    ctrl.toggle_confirm(False)
                    return True

        # Spam past any dialog
        self.toggle_time += delta
        if self.toggle_time >= self._TOGGLE_TIMEOUT:
            self.toggle_time = 0
            self.toggle_state = not self.toggle_state
            ctrl.toggle_confirm(self.toggle_state)

        return False


_AIRSHIP_SPAWN_POINT = Vec2(92.5, 93)


class AogaiToManaTree(SeqList):
    _MANA_TREE = Vec2(114, 76)

    def __init__(self):
        super().__init__(
            name="",
            children=[
                SeqMove2DCancel(
                    "Moving to Airship",
                    coords=_overworld_astar.calculate(
                        start=Vec2(95, 93), goal=Vec2(92, 93)
                    ),
                ),
                # Wait for airship to spawn
                WaitForAirshipToSpawn(),
                SeqMove2D(
                    "Board airship",
                    coords=[_AIRSHIP_SPAWN_POINT],
                ),
                # Go to the Mana Tree on airship (can't use AStar here)
                SeqMove2D(
                    "Flying to Mana Tree",
                    coords=[Vec2(101, 90), self._MANA_TREE],
                ),
                # Get out of airship
                # TODO: Does some slightly weird movement due to sleeps
                SeqInteract("Disembark"),
            ],
        )

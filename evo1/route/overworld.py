import logging
from enum import Enum, auto
from typing import Optional

from engine.mathlib import Facing, Vec2, dist, is_close
from engine.move2d import SeqGrabChest, SeqMove2D, move_to
from engine.seq import SeqList
from evo1.atb import (
    Encounter,
    EncounterID,
    FarmingGoal,
    SeqATBmove2D,
    calc_next_encounter,
)
from evo1.move2d import SeqZoneTransition
from maps.evo1 import GetAStar
from memory.evo1 import MapID, get_memory, get_zelda_memory
from memory.rng import EvolandRNG
from term.window import WindowLayout

_overworld_astar = GetAStar(MapID.OVERWORLD)

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
                        Vec2(79.7, 54.8),
                        # Nudge chest (encounters) at (79, 54)
                        # TODO: Improve nudge to avoid stopping
                        Vec2(79.5, 53),
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
                # TODO: Chest skip can sometimes fail
                SeqMove2D(
                    "Performing skip",
                    coords=[Vec2(75, 84.95), Vec2(78, 84.95)],
                    precision=0.05,
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
                # TODO: Menu glitch
                # TODO: Trigger Zephyros fight
            ],
        )

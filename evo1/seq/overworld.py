from memory.rng import EvolandRNG
from engine.seq import SeqList
from engine.mathlib import Facing, Vec2, dist
from evo1.atb import SeqATBmove2D, EncounterID, FarmingGoal, calc_next_encounter
from evo1.move2d import SeqZoneTransition, SeqGrabChest, SeqMove2D, move_to
from evo1.memory import MapID, get_zelda_memory, get_memory
from evo1.maps import GetAStar
from typing import List, Optional
from term.window import WindowLayout
import logging

_overworld_astar = GetAStar(MapID.OVERWORLD)

logger = logging.getLogger(__name__)

class OverworldGliFarm(SeqATBmove2D):
    def __init__(self, name: str, coords: List[Vec2], goal: FarmingGoal = None, precision: float = 0.2):
        super().__init__(
            name=name,
            coords=coords,
            goal=goal,
            precision=precision
        )
        self.can_manip = True
        self.started_manip = False
        self.manipulated_enc: Optional[EncounterID] = None

    def reset(self) -> None:
        self.can_manip = True
        self.started_manip = False
        self.manipulated_enc = None
        super().reset()

    _CHEST_LOCATION = Vec2(84, 46)
    _CHEST_RNG_ADVANCE = 66 # Ticks the rng forward 66 steps
    _GLI_PER_ENEMY = 50

    def _get_number_of_combatants(self, encounter: EncounterID) -> int:
        match encounter:
            case EncounterID.SLIME: return 1
            case EncounterID.SLIME_2: return 2
            case EncounterID.SLIME_3: return 3
            case EncounterID.SLIME_EMUK: return 2
            case EncounterID.EMUK: return 1
            case _: return 0 # Should never happen

    def _should_manip(self) -> bool:
        # self.next_enc already calculated
        next_nr_enemies = self._get_number_of_combatants(self.next_enc)
        manip_nr_enemies = self._get_number_of_combatants(self.manipulated_enc)

        next_gli = next_nr_enemies * self._GLI_PER_ENEMY
        manip_gli = manip_nr_enemies * self._GLI_PER_ENEMY

        gli_remaining = self.goal.gli_goal - get_memory().gli
        # TODO: Check if this logic is sound
        # The idea is that if both encounters are able to get us to the goal, prefer the easier one
        # Fewer enemies are generally easier
        # Slime is generally easier than emuk
        # Doing the manip is generally worse
        if next_gli >= gli_remaining and manip_gli >= gli_remaining:
            # If both encounters fill up the gli, prefer the fewer enemies
            return manip_gli < next_gli
        else:
            # Else, go for the encounter that gives the most gli
            return manip_gli > next_gli

    # Returning true means we seize control instead of moving on
    def do_encounter_manip(self) -> bool:
        # Check if we've already picked up the chest
        if not self.can_manip:
            return False
        # Check if we are done farming
        if self._farm_done():
            return False
        player = get_zelda_memory().player
        dist_to_chest = dist(player.pos, self._CHEST_LOCATION)

        # Check if we are outside range of the chest for next enc
        if not dist_to_chest < player.encounter_timer:
            return False


        if self.started_manip:
            # Check if we've picked up chest, manip done
            if self.manipulated_enc == self.next_enc:
                self.started_manip = False
                self.can_manip = False
                return False
        else:
            # Calculate the manipulated encounter
            rng = EvolandRNG().get_rng()
            rng.advance_rng(self._CHEST_RNG_ADVANCE)
            self.manipulated_enc = calc_next_encounter(rng)

            if not self._should_manip():
                return False

        if not self.started_manip:
            logger.info(f"Picking up chest to forward rng. {self.manipulated_enc} is better than {self.next_enc}")
            self.started_manip = True

        # Move towards chest to manip
        move_to(player=player.pos, target=self._CHEST_LOCATION, precision=self.precision)

        return True

    def render(self, window: WindowLayout) -> None:
        super().render(window=window)
        if self.can_manip and self.manipulated_enc:
            window.stats.addstr(Vec2(1, 15), f"  Manip: {self.manipulated_enc.name}")

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
                        Vec2(79.5, 53),
                    ]
                ),
                # Battle handler for random battles, mashing confirm is fine for now
                OverworldGliFarm(
                    "Navigating overworld",
                    coords=[
                        Vec2(85, 47),
                        Vec2(87, 43),
                    ],
                    # Need to farm gli before progressing. We need 250 to buy gear, and we can get 50 in the village
                    goal=FarmingGoal(farm_coords=[Vec2(87, 44), Vec2(87, 43)], precision=0.2, gli_goal=200)
                ),
                SeqZoneTransition("Meadow", direction=Facing.UP, target_zone=MapID.MEADOW),
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
                    coords=_overworld_astar.calculate(start=Vec2(87, 40), goal=Vec2(79, 35))
                ),
                # Move into the caverns
                SeqZoneTransition("Crystal Cavern", direction=Facing.UP, target_zone=MapID.CRYSTAL_CAVERN)
            ]
        )


class OverworldToNoria(SeqList):
    def __init__(self):
        super().__init__(
            name="Overworld",
            children=[
                SeqMove2D("Move to chest", coords=_overworld_astar.calculate(start=Vec2(79, 73), goal=Vec2(78, 76))),
                SeqGrabChest("Perspective", direction=Facing.LEFT),
                SeqMove2D("Move to mines", coords=_overworld_astar.calculate(start=Vec2(78, 76), goal=Vec2(75, 79))),
                SeqZoneTransition("Noria Mines", direction=Facing.LEFT, target_zone=MapID.NORIA_CLOSED),
            ]
        )

class OverworldToAogai(SeqList):
    def __init__(self):
        super().__init__(
            name="Overworld",
            children=[
                SeqMove2D("Performing skip", coords=[Vec2(75, 84.95), Vec2(78, 84.95)], precision=0.05),
                SeqMove2D("Moving to Aogai", coords=_overworld_astar.calculate(start=Vec2(78, 85), goal=Vec2(95, 93))),
                SeqZoneTransition("Aogai village", direction=Facing.UP, target_zone=MapID.AOGAI),
            ]
        )

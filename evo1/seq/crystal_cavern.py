import logging

import evo1.control
from engine.mathlib import Facing, Vec2, is_close
from engine.seq import SeqList
from evo1.atb import EncounterID, SeqATBCombat, SeqATBmove2D, calc_next_encounter
from evo1.maps import GetAStar
from evo1.memory import MapID, get_memory, get_zelda_memory
from evo1.move2d import SeqGrabChest, SeqHoldInPlace, SeqMove2D, SeqZoneTransition
from memory.rng import EvolandRNG
from term.window import WindowLayout

logger = logging.getLogger(__name__)


_cavern_astar = GetAStar(MapID.CRYSTAL_CAVERN)
_limbo_astar = GetAStar(MapID.LIMBO)


class CrystalCavernEncManip(SeqATBmove2D):
    def __init__(
        self,
        name: str,
        coords: list[Vec2],
        pref_enc: list[EncounterID],
        precision: float = 0.2,
    ):
        self.pref_enc = pref_enc
        super().__init__(name=name, coords=coords, goal=None, precision=precision)

    def _should_manip(self) -> bool:
        # Check how close we are to getting an encounter
        mem = get_zelda_memory()
        enc_timer = mem.player.encounter_timer

        # If we are about to get an encounter, potentially manip (stop and wait)
        if enc_timer < 0.2:
            if self.next_enc.enc_id in self.pref_enc:
                # If favorable and it's a Kobra, wait if we're going to miss
                return (
                    not self.next_enc.first_turn.hit
                    if self.next_enc.enc_id == EncounterID.KOBRA
                    else False
                )
            else:
                # Not favorable, wait
                return True
        return False

    # Returning true means we seize control instead of moving on
    def do_encounter_manip(self) -> bool:
        mem = get_memory()
        rng = EvolandRNG().get_rng()
        self.next_enc = calc_next_encounter(
            rng=rng, has_3d_monsters=False, clink_level=mem.lvl
        )

        if not self._should_manip():
            return False

        # Wait until a better encounter
        ctrl = evo1.control.handle()
        ctrl.dpad.none()

        return True

    def render(self, window: WindowLayout) -> None:
        super().render(window=window)


# Dummy class for ATB combat testing; requires manual control
class SeqKefkasGhost(SeqATBCombat):
    def __init__(self, target: Vec2) -> None:
        super().__init__(name="Kefka's Ghost")
        self.target = target
        self.precision = 0.2

    # Kefka's Ghost has a strange property; when the boss turns invincible,
    # its turn gauge will be set to -999999999999. We should avoid attacking
    # it in this phase.
    def _is_invincible(self) -> bool:
        return self.mem.enemies[0].turn_gauge < -1

    def handle_combat(self):
        # Do nothing if the boss is in the counter phase
        if self._is_invincible():
            return
        # TODO: Very, very dumb combat. Should maybe check for healing
        ctrl = evo1.control.handle()
        ctrl.dpad.none()
        ctrl.confirm(tapping=True)

    def execute(self, delta: float) -> bool:
        super().execute(delta)
        # Check if we have reached the goal
        mem = get_zelda_memory()
        player_pos = mem.player.pos
        return is_close(player_pos, self.target, precision=self.precision)


class CrystalCavern(SeqList):
    def __init__(self):
        super().__init__(
            name="Crystal Cavern",
            children=[
                CrystalCavernEncManip(
                    name="Move to chest",
                    coords=_cavern_astar.calculate(
                        start=Vec2(24, 77), goal=Vec2(18, 39)
                    ),
                    pref_enc=[EncounterID.KOBRA],
                ),
                SeqGrabChest("Experience", Facing.UP),
                CrystalCavernEncManip(
                    name="Move to trigger",
                    coords=_cavern_astar.calculate(
                        start=Vec2(18, 38), goal=Vec2(54, 36)
                    ),
                    pref_enc=[EncounterID.TORK],
                ),
                # TODO should menu manip here
                SeqHoldInPlace(
                    name="Trigger plate", target=Vec2(54, 36.5), timeout_in_s=0.5
                ),
                CrystalCavernEncManip(
                    name="Move to boss",
                    coords=_cavern_astar.calculate(
                        start=Vec2(54, 36), goal=Vec2(49, 9)
                    ),
                    pref_enc=[EncounterID.KOBRA],
                ),
                # Trigger fight against Kefka's ghost (interact with crystal)
                SeqKefkasGhost(target=Vec2(7, 10)),
                # Limbo realm
                SeqMove2D(
                    name="Move to portal",
                    coords=_limbo_astar.calculate(start=Vec2(7, 10), goal=Vec2(7, 6)),
                ),
                SeqZoneTransition(
                    "Enter the third dimension", Facing.UP, target_zone=MapID.EDEL_VALE
                ),
            ],
        )

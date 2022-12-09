import logging

import evo1.control
from engine.mathlib import Facing, Vec2
from engine.seq import SeqList
from evo1.atb import EncounterID, SeqATBmove2D, calc_next_encounter
from evo1.maps import GetAStar
from evo1.memory import MapID, get_memory, get_zelda_memory
from evo1.move2d import (
    SeqGrabChest,
    SeqHoldInPlace,
    SeqManualUntilClose,
    SeqMove2D,
    SeqZoneTransition,
)
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
                # TODO: Doesn't fully work (doesn't detect start of battle correctly)
                # SeqATBCombatManual(name="Kefka's Ghost", wait_for_battle=True),
                # TODO: Fight against Kefka's ghost (need to implement a smarter combat function to avoid the boss counter)
                SeqManualUntilClose(name="Kefka's Ghost", target=Vec2(7, 10)),
                # TODO: Grab the crystal and become 3D
                # Limbo realm
                # SeqInteract(name="Story stuff", timeout_in_s=0.5),
                SeqMove2D(
                    name="Move to portal",
                    coords=_limbo_astar.calculate(start=Vec2(7, 10), goal=Vec2(7, 6)),
                ),
                SeqZoneTransition(
                    "Enter the third dimension", Facing.UP, target_zone=MapID.EDEL_VALE
                ),
            ],
        )

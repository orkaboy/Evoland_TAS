import logging

from control import evo_ctrl
from engine.mathlib import Facing, Vec2
from engine.move2d import SeqGrabChest, SeqMove2D, SeqMove2DConfirm
from engine.seq import SeqDelay, SeqList, SeqMashDelay, SeqMenu
from evo1.atb import EncounterID, FarmingGoal, SeqATBCombat, SeqATBmove2D
from evo1.move2d import SeqZoneTransition
from maps.evo1 import GetNavmap
from memory.evo1 import MapID, get_zelda_memory
from term.window import WindowLayout

logger = logging.getLogger(__name__)


_cavern_astar = GetNavmap(MapID.CRYSTAL_CAVERN)
_limbo_astar = GetNavmap(MapID.LIMBO)


class CrystalCavernEncManip(SeqATBmove2D):
    def __init__(
        self,
        name: str,
        coords: list[Vec2],
        pref_enc: list[EncounterID],
        goal: FarmingGoal = None,
        precision: float = 0.2,
    ):
        self.pref_enc = pref_enc
        super().__init__(name=name, coords=coords, goal=goal, precision=precision)

    # TODO: Leveling requirement should account for exp (if the first manip fails)
    def _should_manip(self) -> bool:
        # Check how close we are to getting an encounter
        mem = get_zelda_memory()
        enc_timer = mem.player.encounter_timer

        # If we are about to get an encounter, potentially manip (stop and wait)
        if enc_timer < 0.1:
            if self.next_enc.enc_id in self.pref_enc:
                # If favorable and it's a Kobra, wait if we're going to miss
                # TODO: Worth it?
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
        self.calc_next_encounter()
        if not self._should_manip():
            return False

        # Wait until a better encounter
        ctrl = evo_ctrl()
        ctrl.set_neutral()

        return True

    def render(self, window: WindowLayout) -> None:
        super().render(window=window)


class SeqKefkasGhost(SeqATBCombat):
    def __init__(self) -> None:
        super().__init__(name="Kefka's Ghost")

    # Kefka's Ghost has a strange property; when the boss turns invincible,
    # its turn gauge will be set to -999999999999. We should avoid attacking
    # it in this phase.
    def _is_invincible(self) -> bool:
        return self.mem.enemies[0].turn_gauge < -1

    def handle_combat(self, should_run: bool = False):
        # Do nothing if battle has ended
        if self.mem.ended:
            return
        # Do nothing if the boss is in the counter phase
        if self._is_invincible():
            return
        # TODO: Very, very dumb combat. Should maybe check for healing
        ctrl = evo_ctrl()
        ctrl.set_neutral()
        ctrl.confirm(tapping=True)

    def execute(self, delta: float) -> bool:
        super().execute(delta)
        return self.state == self._BattleFSM.POST_BATTLE


class CrystalCavern(SeqList):
    def __init__(self):
        super().__init__(
            name="Crystal Cavern",
            children=[
                SeqMove2DConfirm(
                    name="Move to chest",
                    coords=_cavern_astar.calculate(
                        start=Vec2(24, 77), goal=Vec2(20, 66), final_pos=Vec2(20, 65.6)
                    ),
                ),
                SeqGrabChest("Cave monsters", Facing.UP),
                # Should run from these battles
                CrystalCavernEncManip(
                    name="Move to chest",
                    coords=_cavern_astar.calculate(
                        start=Vec2(20, 65), goal=Vec2(18, 39)
                    ),
                    pref_enc=[
                        EncounterID.KOBRA,
                        EncounterID.SCAVEN_2,
                        EncounterID.KOBRA_2,
                    ],
                ),
                SeqGrabChest("Experience", Facing.UP),
                CrystalCavernEncManip(
                    name="Move to trigger",
                    coords=_cavern_astar.calculate(
                        start=Vec2(18, 38), goal=Vec2(54, 36), final_pos=Vec2(54, 36.7)
                    ),
                    goal=FarmingGoal(lvl_goal=2),
                    pref_enc=[EncounterID.TORK, EncounterID.KOBRA_2],
                ),
                # Menu manip here (carries over to first chest in 3D Edel Vale)
                SeqMenu("Menu manip"),
                SeqDelay(name="Trigger plate", timeout_in_s=0.5),
                SeqMenu("Menu manip"),
                SeqMove2D(name="Menu manip", coords=[Vec2(54, 34)]),
                SeqMenu("Menu manip"),
                # Should run from battle if we have level 2
                CrystalCavernEncManip(
                    name="Move to boss",
                    coords=_cavern_astar.calculate(
                        # (54, 36)
                        start=Vec2(54, 30),
                        goal=Vec2(49, 9),
                    ),
                    goal=FarmingGoal(lvl_goal=2),
                    pref_enc=[
                        EncounterID.KOBRA,
                        EncounterID.SCAVEN_2,
                        EncounterID.KOBRA_2,
                    ],
                ),
                # Trigger fight against Kefka's ghost (interact with crystal)
                SeqKefkasGhost(),
                # Mash past end of battle, activate the crystal but don't talk to Kaeris
                SeqMashDelay("Activate crystal", timeout_in_s=3.0),
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

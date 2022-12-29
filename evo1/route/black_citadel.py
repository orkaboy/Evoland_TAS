import logging

from control import evo_ctrl
from engine.mathlib import Vec2
from engine.move2d import SeqMove2D
from engine.seq import SeqDelay, SeqList
from evo1.atb import ATBAction, ATBActor, ATBPlan, SeqATBCombat

logger = logging.getLogger(__name__)


class SeqZephyrosATB(SeqATBCombat):
    def __init__(self, name="Zephyros") -> None:
        super().__init__(name=name)

    _PHASE_2_HP = 800

    def create_plan(self, actor: ATBActor) -> ATBPlan:
        zephyros_hp = self.mem.enemies[0].cur_hp

        # If we are in the second phase, just attack until we die!
        if zephyros_hp < self._PHASE_2_HP:
            return ATBPlan(actor, ATBAction.ATTACK, target=0)

        # Check if we need healing
        clink_hp = self.mem.allies[0].cur_hp
        kaeris_hp = self.mem.allies[1].cur_hp
        clink_critical = clink_hp < 30 and clink_hp != 0
        kaeris_critical = kaeris_hp < 30 and kaeris_hp != 0

        if kaeris_critical:
            return ATBPlan(actor, ATBAction.POTION, target=ATBActor.KAERIS)
        if clink_critical:
            return ATBPlan(actor, ATBAction.POTION, target=ATBActor.CLINK)

        # Check if we are low
        # TODO: Do we want this?
        clink_low = clink_hp < 50
        kaeris_low = kaeris_hp < 45
        should_heal = clink_low and kaeris_low

        # Attack the boss
        match actor:
            case ATBActor.CLINK:
                return ATBPlan(actor, ATBAction.ATTACK, target=0)
            case ATBActor.KAERIS:
                if should_heal:
                    return ATBPlan(actor, ATBAction.HEAL, target=None)
                return ATBPlan(actor, ATBAction.X_CRYSTAL, target=0)

    def handle_combat(self, should_run: bool = False):
        # TODO: Handle double turn

        if self.cur_plan is None:
            actor = self._cur_actor()
            if actor is not None:
                self.cur_plan = self.create_plan(actor)
                logger.debug(f"Crafting plan: {self.cur_plan}")

        if self.cur_plan is not None:
            # Check if plan is done
            if self._execute_plan(self.cur_plan):
                logger.debug(f"Done with plan: {self.cur_plan}")
                self.cur_plan = None
        else:
            # Handle non-turn stuff
            ctrl = evo_ctrl()
            ctrl.confirm(tapping=True)

    def execute(self, delta: float, should_run: bool = False) -> bool:
        super().execute(delta, should_run)
        return self.state == self._BattleFSM.POST_BATTLE


class SeqZephyrosBabamut(SeqZephyrosATB):
    def __init__(self) -> None:
        super().__init__(name="I'ma firin mah lazer")

    def create_plan(self, actor: ATBActor) -> ATBPlan:
        return ATBPlan(actor, ATBAction.BABAMUT, target=None)


class SeqLeaveBlackCitadel(SeqMove2D):
    """Some custom logic to handle getting out of Black Citadel."""

    _TARGET = [Vec2(116, 88)]
    _TOGGLE_TIME = 0.2

    def __init__(self):
        super().__init__(
            name="Leaving Black Citadel",
            coords=self._TARGET,
            precision=0.2,
        )
        self.timer = 0
        self.toggle = False

    def reset(self) -> None:
        self.timer = 0
        self.toggle = False
        return super().reset()

    def execute(self, delta: float) -> bool:
        ctrl = evo_ctrl()

        self.timer += delta
        if self.timer >= self._TOGGLE_TIME:
            self.timer = 0
            self.toggle = not self.toggle
            ctrl.toggle_confirm(self.toggle)

        done = super().execute(delta)
        if done:
            ctrl.toggle_confirm(False)
        return done


class BlackCitadel(SeqList):
    def __init__(self):
        super().__init__(
            name="Black Citadel",
            children=[
                # Fight Zephyros. Need to track health until he does his super move
                SeqZephyrosATB(),
                SeqDelay("End of battle", timeout_in_s=1.0),
                # Summon Babamut and chase away Zephyros
                SeqZephyrosBabamut(),
                SeqLeaveBlackCitadel(),
            ],
        )

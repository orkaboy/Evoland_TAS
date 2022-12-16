import logging
from enum import Enum, auto
from typing import Optional

from engine.mathlib import Vec2
from engine.seq import SeqBase, SeqList
from memory.evo1 import get_zelda_memory, load_zelda_memory
from memory.evo1.zephy import ZephyrosGanonMemory, ZephyrosGolemMemory
from term.window import WindowLayout

logger = logging.getLogger(__name__)


class ManaTree(SeqList):
    def __init__(self):
        super().__init__(
            name="Mana Tree",
            children=[
                # TODO: Fight final boss (Golem form)
                # TODO: Fight final boss (Ganon form)
            ],
        )


# Left arm HP:
# [0x7C8, 0x8, 0x3C, 0x88, 0x24, 0x48, 0x8, 0x10, 0x18]
# Right arm HP:
# [0x7C8, 0x8, 0x3C, 0x88, 0x24, 0x48, 0x8, 0x14, 0x18]
# Core HP:
# [0x7C8, 0x8, 0x3C, 0x88, 0x24, 0x48, 0x8, 0x1C, 0x18]

# PC polar coord (double, angle)
#


class ZephyrosGolemEntity:
    def __init__(self, mem: ZephyrosGolemMemory) -> None:
        self.rotation = mem.rotation
        self.hp_left_arm = mem.hp_left_arm
        self.hp_right_arm = mem.hp_right_arm
        self.hp_armor = mem.hp_armor
        self.hp_core = mem.hp_core

    @property
    def armless(self) -> bool:
        return self.hp_left_arm == 0 and self.hp_right_arm == 0

    @property
    def done(self) -> bool:
        return self.armless and self.hp_core == 0


class ZephyrosGanonEntity:
    def __init__(self, mem: ZephyrosGanonMemory) -> None:
        self.pos = mem.pos
        self.hp = mem.hp

    @property
    def done(self) -> bool:
        return self.hp == 0


class SeqZephyrosObserver(SeqBase):
    class FightState(Enum):
        NOT_STARTED = auto()
        STARTED = auto()
        GOLEM_SPAWNED = auto()
        GOLEM_FIGHT = auto()
        GOLEM_ARMLESS_FIGHT = auto()
        GANON_SPAWNED = auto()
        GANON_FIGHT = auto()
        ENDING = auto()

    def __init__(self):
        super().__init__(
            name="Zephyros Observer",
            func=load_zelda_memory,
        )
        self.state = self.FightState.NOT_STARTED
        self.golem: Optional[ZephyrosGolemEntity] = None
        self.ganon: Optional[ZephyrosGanonEntity] = None

    def reset(self) -> None:
        self.state = self.FightState.NOT_STARTED
        self.golem: Optional[ZephyrosGolemEntity] = None
        self.ganon: Optional[ZephyrosGanonEntity] = None

    def _start_state(self) -> bool:
        return self.state in [
            self.FightState.NOT_STARTED,
            self.FightState.STARTED,
        ]

    def _golem_state(self) -> bool:
        return self.state in [
            self.FightState.GOLEM_SPAWNED,
            self.FightState.GOLEM_FIGHT,
            self.FightState.GOLEM_ARMLESS_FIGHT,
        ]

    def _ganon_state(self) -> bool:
        return self.state in [
            self.FightState.GANON_SPAWNED,
            self.FightState.GANON_FIGHT,
        ]

    def _update_state(self) -> None:
        mem = get_zelda_memory()
        # Handle initial cutscene part of the fight
        if self._start_state():
            match self.state:
                case self.FightState.NOT_STARTED:
                    if mem.in_zephy_fight:
                        self.state = self.FightState.STARTED
                        logger.info("Mana Tree entered.")

                case self.FightState.STARTED:
                    zephy = mem.zephy_golem
                    if zephy is not None:
                        self.state = self.FightState.GOLEM_SPAWNED
                        logger.info("Zephyros Golem spawned.")

        # Handle Golem fight state
        if self._golem_state():
            self.golem = ZephyrosGolemEntity(mem.zephy_golem)
            match self.state:
                case self.FightState.GOLEM_SPAWNED:
                    # TODO: Doesn't work, is always 1
                    if mem.player.in_control:
                        logger.info("Zephyros Golem fight started.")
                        self.state = self.FightState.GOLEM_FIGHT
                case self.FightState.GOLEM_FIGHT:
                    if self.golem.armless:
                        logger.info("Zephyros Golem arms defeated.")
                        self.state = self.FightState.GOLEM_ARMLESS_FIGHT
                case self.FightState.GOLEM_ARMLESS_FIGHT:
                    if self.golem.done:
                        self.state = self.FightState.GANON_SPAWNED
                        logger.info("Zephyros Golem defeated.")

        # Handle Ganon fight state
        if self._ganon_state():
            self.ganon = ZephyrosGanonEntity(mem.zephy_ganon)
            match self.state:
                case self.FightState.GANON_SPAWNED:
                    # TODO: Doesn't work, is always 1
                    if mem.player.in_control:
                        self.state = self.FightState.GANON_FIGHT
                        logger.info("Zephyros Ganon fight started.")
                case self.FightState.GANON_FIGHT:
                    if self.ganon.done:
                        self.state = self.FightState.ENDING
                        logger.info("Zephyros Ganon defeated.")

    def execute(self, delta: float) -> bool:
        super().execute(delta=delta)
        self._update_state()

        return False  # Never finishes

    def render(self, window: WindowLayout) -> None:
        window.stats.erase()
        window.map.erase()

        window.stats.write_centered(line=1, text="Evoland TAS")
        window.stats.write_centered(line=2, text="Zephyros Battle")

        if self._golem_state():
            # TODO: Render player pos, render golem pose
            window.stats.addstr(pos=Vec2(1, 4), text=f"Rotation: {self.golem.rotation}")

            window.stats.addstr(
                pos=Vec2(1, 6), text=f"Left arm: {self.golem.hp_left_arm}"
            )
            window.stats.addstr(
                pos=Vec2(1, 7), text=f"Right arm: {self.golem.hp_right_arm}"
            )
            window.stats.addstr(pos=Vec2(1, 8), text=f"Core: {self.golem.hp_core}")
        elif self._ganon_state():
            # TODO: Render player pos, render zephy pos, render zephy hp
            zephy_pos = self.ganon.pos
            window.stats.addstr(pos=Vec2(1, 4), text=f"Zephy pos: {zephy_pos}")
            window.stats.addstr(pos=Vec2(1, 6), text=f"HP: {self.ganon.hp}")
        elif self.state == self.FightState.ENDING:
            window.stats.write_centered(line=5, text="Good Game!")

    def __repr__(self) -> str:
        return f"Zephyros: {self.state.name}"

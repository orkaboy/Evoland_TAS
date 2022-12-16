import contextlib
import itertools
import logging
import math
from enum import Enum, auto
from typing import Optional

from control import evo_ctrl
from engine.mathlib import Vec2
from engine.seq import SeqBase, SeqList
from memory.evo1 import get_zelda_memory
from memory.evo1.zephy import (
    ZephyrosGanonMemory,
    ZephyrosGolemMemory,
    ZephyrosPlayerMemory,
)
from term.window import SubWindow, WindowLayout

logger = logging.getLogger(__name__)


class ManaTree(SeqList):
    def __init__(self):
        super().__init__(
            name="Mana Tree",
            children=[
                SeqZephyrosFight(),
            ],
        )


class ZephyrosGolemEntity:
    def __init__(self, mem: ZephyrosGolemMemory) -> None:
        self.rotation = mem.rotation
        self.left_arm = mem.left
        self.right_arm = mem.right
        self.armor = mem.armor
        self.core = mem.core
        self.anim_timer = mem.anim_timer

    @property
    def armless(self) -> bool:
        return self.hp_left == 0 and self.hp_right == 0

    @property
    def hp_left(self) -> int:
        return 0 if self.left_arm is None else self.left_arm.hp

    @property
    def hp_right(self) -> int:
        return 0 if self.right_arm is None else self.right_arm.hp

    @property
    def done(self) -> bool:
        return self.armless and self.core.hp == 0


class ZephyrosGanonEntity:
    def __init__(self, mem: ZephyrosGanonMemory) -> None:
        self.pos = mem.pos
        self.hp = mem.hp
        self.red_counter = mem.red_counter
        self.projectiles = mem.projectiles

    @property
    def done(self) -> bool:
        return self.hp == 0


class SeqZephyrosObserver(SeqBase):
    class FightState(Enum):
        NOT_STARTED = auto()
        STARTED = auto()
        GOLEM_SPAWNED = auto()
        GOLEM_FIGHT = auto()
        GOLEM_ARMLESS_SETUP = auto()
        GOLEM_ARMLESS_FIGHT = auto()
        GANON_WAIT = auto()
        GANON_FIGHT = auto()
        GANON_DEATH = auto()
        ENDING = auto()

    def __init__(self, name="Zephyros Observer", func=None):
        super().__init__(
            name=name,
            func=func,
        )
        self.state = self.FightState.NOT_STARTED
        self.golem: Optional[ZephyrosGolemEntity] = None
        self.ganon: Optional[ZephyrosGanonEntity] = None
        self.player: Optional[ZephyrosPlayerMemory] = None
        self.dialog: int = 0
        self.dialog_cnt: int = 0

    def reset(self) -> None:
        self.state = self.FightState.NOT_STARTED
        self.golem: Optional[ZephyrosGolemEntity] = None
        self.ganon: Optional[ZephyrosGanonEntity] = None
        self.player: Optional[ZephyrosPlayerMemory] = None
        self.dialog: int = 0
        self.dialog_cnt: int = 0

    def _start_state(self) -> bool:
        return self.state in [
            self.FightState.NOT_STARTED,
            self.FightState.STARTED,
        ]

    def _golem_state(self) -> bool:
        return self.state in [
            self.FightState.GOLEM_SPAWNED,
            self.FightState.GOLEM_FIGHT,
            self.FightState.GOLEM_ARMLESS_SETUP,
            self.FightState.GOLEM_ARMLESS_FIGHT,
        ]

    def _ganon_state(self) -> bool:
        return self.state in [
            self.FightState.GANON_WAIT,
            self.FightState.GANON_FIGHT,
        ]

    _GOLEM_NUM_DIALOGS = 8
    _GANON_NUM_DIALOGS = 3
    _ENDING_NUM_DIALOGS = 4
    _GOLEM_CORE_HP = 4
    _GANON_HP = 4

    def _update_state(self) -> None:
        mem = get_zelda_memory()

        match self.state:
            case self.FightState.NOT_STARTED | self.FightState.GANON_DEATH | self.FightState.ENDING:
                self.player = None
            case _:
                self.player = mem.zephy_player

        # Handle initial cutscene part of the fight
        if self._start_state():
            match self.state:
                case self.FightState.NOT_STARTED:
                    if mem.in_zephy_fight:
                        self.state = self.FightState.STARTED
                        logger.info("Mana Tree entered.")

                case self.FightState.STARTED:
                    zephy = mem.zephy_golem(armless=False)
                    if zephy is not None:
                        self.state = self.FightState.GOLEM_SPAWNED
                        logger.info("Zephyros Golem spawned.")

        # Handle Golem fight state
        if self._golem_state():
            if self.state in [
                self.FightState.GOLEM_ARMLESS_SETUP,
                self.FightState.GOLEM_ARMLESS_FIGHT,
            ]:
                self.golem = ZephyrosGolemEntity(mem.zephy_golem(armless=True))
            else:
                self.golem = ZephyrosGolemEntity(mem.zephy_golem(armless=False))

            match self.state:
                case self.FightState.GOLEM_SPAWNED:
                    dialog = mem.zephy_dialog
                    # Count the dialog boxes
                    if dialog != self.dialog:
                        self.dialog = dialog
                        if dialog != 0:
                            self.dialog_cnt += 1
                        # If we have gotten enough text and dialog is 0, the fight is on
                        if self.dialog_cnt >= self._GOLEM_NUM_DIALOGS and dialog == 0:
                            logger.info("Zephyros Golem fight started.")
                            self.state = self.FightState.GOLEM_FIGHT
                case self.FightState.GOLEM_FIGHT:
                    if self.golem.armless:
                        logger.info("Zephyros Golem arms defeated.")
                        self.state = self.FightState.GOLEM_ARMLESS_SETUP
                case self.FightState.GOLEM_ARMLESS_SETUP:
                    if self.golem.core.hp == self._GOLEM_CORE_HP:
                        self.state = self.FightState.GOLEM_ARMLESS_FIGHT
                        logger.info("Zephyros Golem armless phase.")
                case self.FightState.GOLEM_ARMLESS_FIGHT:
                    if self.golem.done:
                        self.state = self.FightState.GANON_WAIT
                        self.dialog_cnt = 0
                        logger.info("Zephyros Golem defeated.")

        # Handle Ganon fight state
        if self._ganon_state():
            match self.state:
                case self.FightState.GANON_WAIT:
                    dialog = mem.zephy_dialog
                    if dialog != self.dialog:
                        self.dialog = dialog
                        if dialog != 0:
                            self.dialog_cnt += 1
                        # If we have gotten enough text and dialog is 0, the fight is on
                        if self.dialog_cnt >= self._GANON_NUM_DIALOGS and dialog == 0:
                            self.ganon = ZephyrosGanonEntity(mem.zephy_ganon)
                            self.state = self.FightState.GANON_FIGHT
                            logger.info("Zephyros Ganon fight started.")
                case self.FightState.GANON_FIGHT:
                    self.ganon = ZephyrosGanonEntity(mem.zephy_ganon)
                    if self.ganon.done:
                        self.state = self.FightState.GANON_DEATH
                        self.dialog_cnt = 0
                        logger.info("Zephyros Ganon defeated.")

        if self.state == self.FightState.GANON_DEATH:
            dialog = mem.zephy_dialog
            if dialog != self.dialog:
                self.dialog = dialog
                if dialog != 0:
                    self.dialog_cnt += 1
                # If we have gotten enough text and dialog is 0, the fight is on
                if self.dialog_cnt >= self._ENDING_NUM_DIALOGS and dialog == 0:
                    self.state = self.FightState.ENDING
                    logger.info("Final input.")

    # Override for TAS logic
    def execute(self, delta: float) -> bool:
        super().execute(delta=delta)
        self._update_state()
        return self.done()

    # Map starts at line 2 and fills the rest of the map window
    _map_start_y = 2
    _Y_SCALE = 2

    _ARENA_OUTER_RADIUS = 15
    _ARENA_INNER_RADIUS = 13
    _GOLEM_SIZE = 7

    # (0,0) is at center of map. Y-axis increases going down the screen.
    def _print_ch_in_map(self, map_win: SubWindow, pos: Vec2, ch: str):
        size = map_win.size
        centerx, centery = (
            size.x / 2,
            self._map_start_y + (size.y - self._map_start_y) / 2,
        )
        draw_x, draw_y = int(centerx + pos.x), int(centery + (pos.y / self._Y_SCALE))
        with contextlib.suppress(Exception):
            if draw_x in range(size.x) and draw_y in range(self._map_start_y, size.y):
                map_win.addch(Vec2(draw_x, draw_y), ch)

    def _render_map(self, map_win: SubWindow) -> None:
        map_win.write_centered(0, "Mana Tree")
        for y, x in itertools.product(
            range(
                self._Y_SCALE * -self._ARENA_OUTER_RADIUS,
                self._Y_SCALE * self._ARENA_OUTER_RADIUS,
                self._Y_SCALE,
            ),
            range(-self._ARENA_OUTER_RADIUS, self._ARENA_OUTER_RADIUS),
        ):
            draw_pos = Vec2(x, y)
            norm = draw_pos.norm
            if norm >= self._ARENA_INNER_RADIUS and norm <= self._ARENA_OUTER_RADIUS:
                self._print_ch_in_map(map_win=map_win, pos=draw_pos, ch=".")

    def _render_player(self, window: WindowLayout) -> None:
        window.stats.addstr(pos=Vec2(1, 4), text=f"Player HP: {self.player.hp}")
        window.stats.addstr(
            pos=Vec2(2, 5),
            text=f"{self.player.polar}",
        )
        self._print_ch_in_map(map_win=window.map, pos=self.player.pos, ch="@")

    def _render_golem(self, window: WindowLayout) -> None:
        window.stats.addstr(
            pos=Vec2(1, 7), text=f"Golem theta={self.golem.rotation:.3f}"
        )
        window.stats.addstr(pos=Vec2(1, 8), text=f"Left arm: {self.golem.hp_left}")
        window.stats.addstr(pos=Vec2(1, 9), text=f"Right arm: {self.golem.hp_right}")
        window.stats.addstr(pos=Vec2(1, 10), text=f"Armor: {self.golem.armor.hp}")
        window.stats.addstr(pos=Vec2(1, 11), text=f"Core: {self.golem.core.hp}")

        for y, x in itertools.product(
            range(
                self._Y_SCALE * -self._GOLEM_SIZE,
                self._Y_SCALE * self._GOLEM_SIZE,
                self._Y_SCALE,
            ),
            range(-self._GOLEM_SIZE, self._GOLEM_SIZE),
        ):
            boss_fragment = Vec2(x, y)
            if boss_fragment.norm <= self._GOLEM_SIZE:
                self._print_ch_in_map(map_win=window.map, pos=boss_fragment, ch="!")

        direction_indicator = Vec2(
            math.cos(self.golem.rotation) * (self._GOLEM_SIZE + 2),
            math.sin(self.golem.rotation) * (self._GOLEM_SIZE + 2),
        )
        self._print_ch_in_map(map_win=window.map, pos=direction_indicator, ch="+")
        # Draw core weak point
        self._print_ch_in_map(map_win=window.map, pos=self.golem.core.pos, ch="O")

    def _render_ganon(self, window: WindowLayout) -> None:
        zephy_pos = self.ganon.pos
        self._print_ch_in_map(map_win=window.map, pos=zephy_pos, ch="!")
        window.stats.addstr(pos=Vec2(1, 7), text=f"Zephy pos: {zephy_pos}")
        window.stats.addstr(pos=Vec2(1, 8), text=f"Zephy HP: {self.ganon.hp}")
        window.stats.addstr(pos=Vec2(1, 10), text="Projectiles:")
        with contextlib.suppress(ReferenceError):
            projectiles = [proj for proj in self.ganon.projectiles if proj.is_active]
            for i, proj in enumerate(projectiles):
                y = i + 11
                if y >= 15:
                    break
                blue = proj.is_blue
                blue_str = "blue" if blue else "red"
                countered = ", counter!" if proj.is_countered else ""
                window.stats.addstr(
                    pos=Vec2(2, y), text=f"{proj.pos}, {blue_str}{countered}"
                )
                self._print_ch_in_map(
                    map_win=window.map, pos=proj.pos, ch="O" if blue else "*"
                )

    def render(self, window: WindowLayout) -> None:
        window.stats.erase()
        window.map.erase()

        window.stats.write_centered(line=1, text="Evoland TAS")
        window.stats.write_centered(line=2, text="Zephyros Battle")
        self._render_map(map_win=window.map)

        if self.player is not None:
            self._render_player(window=window)

        if self._golem_state():
            self._render_golem(window=window)
        elif self.state == self.FightState.GANON_FIGHT:
            self._render_ganon(window=window)
        elif self.state == self.FightState.ENDING:
            window.stats.write_centered(line=5, text="Good Game!")

    def done(self) -> bool:
        return self.state == self.FightState.ENDING

    def __repr__(self) -> str:
        return f"Zephyros final battle: {self.state.name}"


class SeqZephyrosFight(SeqZephyrosObserver):
    def __init__(self):
        super().__init__(
            name="Zephyros Final Battle",
            func=None,
        )

    def execute(self, delta: float) -> bool:
        # Updates the state of the battle
        super().execute(delta)
        ctrl = evo_ctrl()

        match self.state:
            case self.FightState.GOLEM_FIGHT:
                self.golem_fight()
            case self.FightState.GOLEM_ARMLESS_FIGHT:
                self.golem_armless_fight()
            case self.FightState.GANON_FIGHT:
                self.ganon_fight()
            case _:
                # Tap to skip cutcenes
                ctrl.confirm(tapping=True)
        return self.done()

    def golem_fight(self) -> None:
        # TODO: Track boss attack/wait state
        # TODO: Juke boss to move to correct side
        # TODO: Close in and attack the arm as it comes down
        # TODO: Swap to attacking other side until both arms are done
        pass

    def golem_armless_fight(self) -> None:
        # TODO: At start of phase, move behind golem to avoid getting hit
        # TODO: Calculate where the golem will end its rotation
        # TODO: Avoid getting hit while the golem attacks
        # TODO: Attack the armor (verify hit by checking armor hp)
        # TODO: Identify the core position/trajectory
        # TODO: Attack the core
        pass

    def ganon_fight(self) -> None:
        # TODO: Align against closest position opposite to Zephyros
        # TODO: Face towards Zephyros
        # TODO: Detect when projectiles spawn and track them
        # TODO: If red, dodge? Or don't bother?
        # TODO: If blue, counter when the projectile is in range.
        pass

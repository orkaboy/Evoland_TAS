from typing import Optional
import memory.core as core
from memory.rng import EvolandRNG
from engine.seq import SeqBase, SequencerEngine
from term.curses import WindowLayout
import curses
import logging

logger = logging.getLogger("RNG")

# Passive class used to verify the RNG calculations
class SeqRngObserver(SeqBase):
    COLUMNS = 5
    ROWS = EvolandRNG.RNG_VALS // COLUMNS
    VAL_WIDTH = 12

    def __init__(self, name: str):
        self.mem = EvolandRNG()
        self.captured_rng = self.mem.get_rng()
        self.last_values = []
        self.modulo = None
        self.mask = 0xffffffff
        self.setting_modulo = 0
        self.tracking = False
        self.tracking_offset = 0
        super().__init__(name)

    def _get_digit(self, input: str) -> Optional[int]:
        if input == ord("0"):
            return 0
        elif input == ord("1"):
            return 1
        elif input == ord("2"):
            return 2
        elif input == ord("3"):
            return 3
        elif input == ord("4"):
            return 4
        elif input == ord("5"):
            return 5
        elif input == ord("6"):
            return 6
        elif input == ord("7"):
            return 7
        elif input == ord("8"):
            return 8
        elif input == ord("9"):
            return 9
        else:
            return None

    def _handle_input_modulo(self) -> None:
        if self.modulo:
            self.modulo = None
        elif self.setting_modulo != 0:
            self.modulo = self.setting_modulo
            self.setting_modulo = 0
        else:
            self.setting_modulo = 0


    def handle_input(self, input: str) -> None:
        # Capture the rng buffer
        if input == ord("c"):
            self.captured_rng = self.mem.get_rng()
            logger.info(f"Captured current rng values. Cursor is at {self.captured_rng.cursor}")
        elif input == ord("t"):
            if self.tracking:
                logger.info(f"Stopped tracking. Offset from start: {self.tracking_offset}")
            else:
                self.captured_rng = self.mem.get_rng()
                self.tracking_offset = 0
                logger.info(f"Tracking rng. Cursor is at {self.captured_rng.cursor}")
            self.tracking = not self.tracking
        # Capture next int from capture buffer
        elif input == ord("i"):
            value = self.captured_rng.rand_int()
            logger.info(f"Next int is: {value}")
            self.last_values.append(value)
        elif input == ord("f"):
            value = self.captured_rng.rand_float()
            logger.info(f"Next float is: {value}")
            self.last_values.append(value)
        elif input == ord("m"):
            self._handle_input_modulo()
        elif input == ord("M"):
            self.mask = 0x3fffffff if self.mask == 0xffffffff else 0xffffffff
        elif not self.modulo:
            digit = self._get_digit(input)
            if isinstance(digit, int):
                self._add_modulo_digit(digit)

    def _add_modulo_digit(self, digit: int) -> None:
        if self.setting_modulo == 0:
            self.setting_modulo = digit
        else:
            self.setting_modulo = 10 * self.setting_modulo + digit

    def execute(self, delta: float, blackboard: dict) -> bool:
        self.rng = self.mem.get_rng()
        if self.tracking:
            # Frame-restricted to prevent softlocks if we lose the cursor
            for _ in range(128):
                if self.captured_rng.cursor == self.rng.cursor:
                    break
                self.captured_rng.advance_rng()
                self.tracking_offset += 1
        return False # Never completes

    def _render_rng_table(self, window: WindowLayout, title: str, rng: EvolandRNG.RNGStruct, y_offset) -> None:
        window.main.addstr(y_offset, 0, f"{title} buffer. Cursor: {rng.cursor}")
        for i in range(EvolandRNG.RNG_VALS):
            y = y_offset + 1 + i // self.COLUMNS
            x = 2 + (i % self.COLUMNS) * self.VAL_WIDTH
            if i == (rng.cursor % EvolandRNG.RNG_VALS):
                window.main.addstr(y, x-1, f"<{rng.values[i]:#010x}>")
            else:
                window.main.addstr(y, x, f"{rng.values[i]:#010x}")

    def _render_modulo_text(self, window: WindowLayout) -> None:
        y, _ = window.stats.getmaxyx()
        if self.modulo:
            window.stats.addstr(y-1, 0, f"Modulo: {self.modulo}")
        else:
            window.stats.addstr(y-1, 0, f"Setting modulo: {self.setting_modulo}")
        window.stats.addstr(y-2, 0, f"Mask: {self.mask:#10x}")
        self.max_cap_values = y-3
        while len(self.last_values) > self.max_cap_values:
            self.last_values.pop(0)

    def _render_calculated_values(self, window: WindowLayout) -> None:
        window.stats.addstr(0, 0, "Last values:")
        for i, value in enumerate(self.last_values):
            y = i + 1
            value = value & self.mask
            if isinstance(value, int):
                if self.modulo:
                    window.stats.addstr(y, 2, f"{value % self.modulo}")
                else:
                    window.stats.addstr(y, 2, f"{value}")
            elif isinstance(value, float):
                window.stats.addstr(y, 2, f"{value:.9f}")

    def render(self,  window: WindowLayout, blackboard: dict) -> None:
        window.main.clear()
        window.stats.clear()
        self._render_rng_table(window, title="Current", rng=self.rng, y_offset=0)
        self._render_rng_table(window, title="Captured", rng=self.captured_rng, y_offset=self.ROWS + 2)
        self._render_modulo_text(window=window)
        self._render_calculated_values(window=window)

        if self.tracking:
            maxy, _ = window.main.getmaxyx()
            window.main.addstr(maxy-1, 1, f"Tracking rng changes. Cursor has advanced by: {self.tracking_offset}")


def rng_observer(window: WindowLayout):
    observer = SeqRngObserver(
        "RNG Observer"
    )

    engine = SequencerEngine(
        window=window,
        root=observer,
    )

    window.main.clear()
    window.stats.clear()
    curses.doupdate()

    while engine.active():
        engine.run()

    core.wait_seconds(3)

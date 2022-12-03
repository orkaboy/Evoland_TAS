import memory.core as core
from memory.rng import EvolandRNG
from engine.seq import SeqBase, SequencerEngine
from term.curses import WindowLayout
import curses


# Passive class used to verify the RNG calculations
class SeqRngObserver(SeqBase):
    COLUMNS = 5
    ROWS = EvolandRNG.RNG_VALS // COLUMNS
    VAL_WIDTH = 12

    def __init__(self, name: str):
        self.mem = EvolandRNG()
        super().__init__(name)

    def execute(self, delta: float, blackboard: dict) -> bool:
        self.rng = self.mem.get_rng()
        self.rng_next = self.mem.get_rng()
        for i in range(EvolandRNG.RNG_VALS):
            self.rng_next._advance_rng()
        return False # Never completes

    def render(self,  window: WindowLayout, blackboard: dict) -> None:
        window.main.clear()
        window.main.addstr(0, 0, f"Cursor: {self.rng.cursor}")
        for i in range(EvolandRNG.RNG_VALS):
            y = 1 + i // self.COLUMNS
            x = 2 + (i % self.COLUMNS) * self.VAL_WIDTH
            window.main.addstr(y, x, f"{self.rng.values[i]:#010x}")

        y_offset = self.ROWS + 2
        window.main.addstr(y_offset, 0, f"Next values:")
        for i in range(EvolandRNG.RNG_VALS):
            y = y_offset + 1 + i // self.COLUMNS
            x = 2 + (i % self.COLUMNS) * self.VAL_WIDTH
            window.main.addstr(y, x, f"{self.rng_next.values[i]:#010x}")

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

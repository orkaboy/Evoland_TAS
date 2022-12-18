# Libraries and Core Files
import contextlib
import datetime
import logging
import time

from control import evo_ctrl
from engine.mathlib import Vec2
from engine.seq.base import SeqBase
from memory.rng import EvolandRNG
from term.window import WindowLayout

logger = logging.getLogger(__name__)


class SequencerEngine(object):
    """
    Engine for executing sequences of generic TAS events.
    Each event sequence can be nested using SeqList.
    """

    def __init__(self, window: WindowLayout, root: SeqBase):
        self.window = window
        self.root = root
        self.done = False
        self.config = window.config_data
        self.paused = False
        self.timestamp = time.time()

    def reset(self) -> None:
        self.paused = False
        self.done = False
        self.root.reset()

    def pause(self) -> None:
        # Restore controls to neutral state
        evo_ctrl().dpad.none()
        self.paused = True
        logger.info("------------------------")
        logger.info("  TAS EXECUTION PAUSED  ")
        logger.info("------------------------")

    def unpause(self) -> None:
        self.paused = False
        self.timestamp = time.time()
        logger.info("------------------------")
        logger.info(" TAS EXECUTION RESUMING ")
        logger.info("------------------------")

    def _handle_input(self) -> None:
        c = self.window.main.getch()
        # Keybinds: Pause TAS
        if c == ord("p"):
            paused = not self.paused
            if paused:
                self.pause()
            else:
                self.unpause()
        else:
            self.root.handle_input(c)

    def _get_deltatime(self) -> float:
        now = time.time()
        delta = now - self.timestamp
        self.timestamp = now
        return delta

    def _update(self) -> None:
        # Execute current gamestate logic
        if not self.paused and not self.done:
            delta = self._get_deltatime()
            self.done = self.root.execute(delta=delta)

    def _print_timer(self) -> None:
        # Timestamp
        start_time = logging._startTime
        now = time.time()
        elapsed = now - start_time
        duration = datetime.datetime.utcfromtimestamp(elapsed)
        timestamp = f"{duration.strftime('%H:%M:%S')}.{int(duration.strftime('%f')) // 1000:03d}"
        pause_str = " == PAUSED ==" if self.paused else ""
        self.window.main.addstr(Vec2(0, 0), f"[{timestamp}]{pause_str}")

    def _print_rng(self) -> None:
        with contextlib.suppress(ReferenceError):
            rng = EvolandRNG().get_rng()
            rng_str = f"RNG: {rng.cursor:2}"
            self.window.main.addstr(
                Vec2(self.window.main.size.x - len(rng_str) - 1, 0), rng_str
            )

    def _render(self) -> None:
        # Clear display windows
        self.window.main.erase()

        # Render timer and gamestate tree
        self._print_timer()
        self.window.main.addstr(Vec2(0, 1), f"Gamestate:\n  {self.root}")
        # Render RNG cursor
        self._print_rng()
        # Render the current gamestate
        self.root.render(window=self.window)

        self.window.update()

    # Execute and render TAS progress
    def run(self) -> None:
        self._handle_input()
        self._update()
        self._render()

    def active(self) -> bool:
        # Return current state of sequence engine (False when the game finishes)
        return not self.done

# Libraries and Core Files
import curses
import logging
import time
from typing import List

logger = logging.getLogger(__name__)


class SeqBase(object):
    def __init__(self, name: str):
        self.name = name

    def reset(self) -> None:
        pass

    # Return true if the sequence is done with, or False if we should remain in this state
    def execute(self, delta: float, blackboard: dict) -> bool:
        return True

    def render(self, main_win, stats_win, blackboard: dict) -> None:
        pass

    # Should be overloaded
    def __repr__(self) -> str:
        return self.name


class SeqLog(SeqBase):
    def __init__(self, name: str, text: str):
        self.text = text
        super().__init__(name)

    def execute(self, delta: float, blackboard: dict) -> bool:
        logging.getLogger(self.name).info(self.text)
        return True


class SeqDebug(SeqBase):
    def __init__(self, name: str, text: str):
        self.text = text
        super().__init__(name)

    def execute(self, delta: float, blackboard: dict) -> bool:
        logging.getLogger(self.name).debug(self.text)
        return True


class SeqDelay(SeqBase):
    def __init__(self, name: str, time_in_s: float):
        self.timer = 0.0
        self.timeout = time_in_s
        super().__init__(name)

    def reset(self) -> None:
        self.timer = 0.0
        return super().reset()

    def execute(self, delta: float, blackboard: dict) -> bool:
        self.timer = self.timer + delta
        if self.timer >= self.timeout:
            self.timer = self.timeout
            return True
        return False

    def __repr__(self) -> str:
        return f"Waiting({self.name})... {self.timer:.2f}/{self.timeout:.2f}"


class SeqList(SeqBase):
    def __init__(self, name: str, children: List[SeqBase]):
        self.step = 0
        self.children = children
        super().__init__(name)

    def reset(self) -> None:
        self.step = 0
        return super().reset()

    # Return true if the sequence is done with, or False if we should remain in this state
    def execute(self, delta: float, blackboard: dict) -> bool:
        cur_child = self.children[self.step]
        num_children = len(self.children)
        # Peform logic of current child step
        ret = cur_child.execute(delta=delta, blackboard=blackboard)
        if ret == True:  # If current child is done
            self.step = self.step + 1
            if self.step >= num_children:
                return True
        return False

    def render(self, main_win, stats_win, blackboard: dict) -> None:
        cur_child = self.children[self.step]
        cur_child.render(main_win=main_win, stats_win=stats_win, blackboard=blackboard)

    # Should be overloaded
    def __repr__(self) -> str:
        cur_child = self.children[self.step]
        num_children = len(self.children)
        cur_step = self.step + 1
        return f"{self.name}[{cur_step}/{num_children}]: {cur_child}"


class SequencerEngine(object):
    """
    Engine for executing sequences of generic TAS events.
    Each event sequence can be nested using SeqList.
    """

    def __init__(self, main_win, stats_win, root: SeqBase, config_data: dict):
        self.main_win = main_win
        self.stats_win = stats_win
        self.root = root
        self.config = config_data
        self.paused = False
        self.timestamp = time.time()
        self.blackboard = {"config": config_data}

    def reset(self) -> None:
        self.paused = False
        self.blackboard = {"config": self.config}
        self.root.reset()

    def pause(self) -> None:
        self.paused = True
        self.main_win.addstr(0, 3, "== PAUSED ==")
        logger.info("------------------------")
        logger.info("  TAS EXECUTION PAUSED  ")

    def unpause(self) -> None:
        self.paused = False
        self.timestamp = time.time()
        logger.info("------------------------")
        logger.info(" TAS EXECUTION RESUMING ")
        logger.info("------------------------")

    def _handle_input(self) -> None:
        c = self.main_win.getch()
        # Keybinds: Pause TAS
        if c == ord("p"):
            paused = not self.paused
            if paused:
                self.pause()
            else:
                self.unpause()

    def _get_deltatime(self) -> float:
        now = time.time()
        delta = now - self.timestamp
        self.timestamp = now
        return delta

    # Execute and render TAS progress
    def run(self) -> bool:
        # Clear display windows
        self.main_win.clear()
        self.stats_win.clear()

        self._handle_input()

        # Execute current gamestate logic
        ret = False
        if not self.paused:
            delta = self._get_deltatime()
            ret = self.root.execute(delta=delta, blackboard=self.blackboard)

        # Render the current gamestate
        self.root.render(
            main_win=self.main_win, stats_win=self.stats_win, blackboard=self.blackboard
        )
        self.main_win.addstr(1, 1, f"Gamestate: {self.root}")

        # Update display windows
        self.main_win.noutrefresh()
        self.stats_win.noutrefresh()
        curses.doupdate()
        # Return current state of sequence engine (True when the game finishes)
        return ret

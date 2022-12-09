# Libraries and Core Files
import logging
from typing import Any, Callable

from term.window import WindowLayout

logger = logging.getLogger(__name__)


class SeqBase(object):
    def __init__(self, name: str = "", func=None):
        self.name = name
        self.func = func

    def reset(self) -> None:
        pass

    def handle_input(self, input: str) -> None:
        pass

    # Return true if the sequence is done with, or False if we should remain in this state
    def execute(self, delta: float) -> bool:
        if self.func:
            self.func()
        return True

    def render(self, window: WindowLayout) -> None:
        pass

    # Should be overloaded
    def __repr__(self) -> str:
        return self.name


class SeqList(SeqBase):
    def __init__(
        self, name: str, children: list[SeqBase], func=None, shadow: str = False
    ):
        self.step = 0
        self.children = children
        self.shadow = shadow
        super().__init__(name, func=func)

    def reset(self) -> None:
        self.step = 0
        return super().reset()

    # Return true if the sequence is done with, or False if we should remain in this state
    def execute(self, delta: float) -> bool:
        super().execute(delta)
        num_children = len(self.children)
        if self.step >= num_children:
            return True
        cur_child = self.children[self.step]
        # Peform logic of current child step
        ret = cur_child.execute(delta=delta)
        if ret is True:  # If current child is done
            self.step = self.step + 1
        return False

    def render(self, window: WindowLayout) -> None:
        num_children = len(self.children)
        if self.step >= num_children:
            return
        cur_child = self.children[self.step]
        cur_child.render(window=window)

    def __repr__(self) -> str:
        num_children = len(self.children)
        if self.step >= num_children:
            return f"{self.name}[{num_children}/{num_children}]"
        cur_child = self.children[self.step]
        if self.shadow:
            return f"{cur_child}"
        cur_step = self.step + 1
        return f"{self.name}[{cur_step}/{num_children}] =>\n  {cur_child}"


class SeqOptional(SeqBase):
    def __init__(
        self,
        name: str,
        cases: dict[Any, SeqBase],
        selector: Callable | int,
        fallback: SeqBase = SeqBase(),
        shadow: bool = False,
    ):
        self.fallback = fallback
        self.selector = selector
        self.selector_repr = selector
        self.selected = False
        self.selection = None
        self.cases = cases
        self.shadow = shadow
        super().__init__(name)

    def reset(self) -> None:
        self.selected = False
        self.selection = None

    def execute(self, delta: float) -> bool:
        if not self.selected:
            self.selector_repr = (
                self.selector() if callable(self.selector) else self.selector
            )
            self.selection = self.cases.get(self.selector_repr)
            self.selected = True

        if self.selection:
            return self.selection.execute(delta=delta)
        if self.fallback:
            return self.fallback.execute(delta=delta)
        logging.getLogger(self.name).warning(
            f"Missing case {self.selector_repr} and no fallback, skipping!"
        )
        return True

    def render(self, window: WindowLayout) -> None:
        if self.selection:
            self.selection.render(window=window)
        elif self.fallback:
            self.fallback.render(window=window)

    def __repr__(self) -> str:
        if self.selection:
            if self.shadow:
                return f"{self.selection}"
            return f"<{self.name}:{self.selector_repr}> => {self.selection}"
        if self.selected and self.fallback:
            if self.shadow:
                return f"{self.fallback}"
            return f"<{self.name}:fallback> => {self.fallback}"
        return f"<{self.name}>"

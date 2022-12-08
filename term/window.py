from engine.mathlib import Vec2


class SubWindow:
    def __init__(self) -> None:
        pass

    @property
    def size(self) -> Vec2:
        return Vec2(0, 0)

    def getch(self) -> str:
        return ""

    def hline(self, pos: Vec2, character: str, length: int) -> None:
        pass

    def addch(self, pos: Vec2, text: str) -> None:
        pass

    def addstr(self, pos: Vec2, text: str) -> None:
        pass

    def write_centered(self, line: int, text: str) -> None:
        pass

    def nodelay(self, on: bool) -> None:
        pass

    def erase(self) -> None:
        pass

    def update(self) -> None:
        pass


class WindowLayout:
    def __init__(self, config_data: dict) -> None:
        self.config_data = config_data
        self.main = SubWindow()
        self.stats = SubWindow()
        self.map = SubWindow()
        self.logger = SubWindow()

    def update(self) -> None:
        pass

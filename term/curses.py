import curses
from curses import wrapper as curses_wrapper

from engine.mathlib import Box2, Vec2
from term.log_init import initialize_logging
from term.window import SubWindow, WindowLayout


def entry_point(config_data: dict, func):
    curses_wrapper(setup_curses, config_data, func)


class CursesWindow(SubWindow):
    def __init__(self, bounds: Box2, auto_scroll: bool = False) -> None:
        self.window = curses.newwin(bounds.h, bounds.w, bounds.pos.y, bounds.pos.x)
        self.window.refresh()
        if auto_scroll:
            self.window.scrollok(True)
            self.window.idlok(True)
            self.window.leaveok(True)
        super().__init__()

    @property
    def size(self) -> Vec2:
        y, x = self.window.getmaxyx()
        return Vec2(x, y)

    def getch(self) -> str:
        return self.window.getch()

    def addch(self, pos: Vec2, text: str) -> None:
        self.window.addch(pos.y, pos.x, text)

    def addstr(self, pos: Vec2, text: str) -> None:
        self.window.addstr(pos.y, pos.x, text)

    def hline(self, pos: Vec2, character: str, length: int) -> None:
        self.window.hline(pos.y, pos.x, character, length)

    def write_centered(self, line: int, text: str) -> None:
        _, maxx = self.window.getmaxyx()
        text_len = len(text)
        x_off = int(maxx / 2 - text_len / 2)
        self.window.addstr(line, x_off, text)

    def erase(self) -> None:
        self.window.erase()

    def nodelay(self, on: bool) -> None:
        self.window.nodelay(1 if on else 0)

    def update(self) -> None:
        self.window.noutrefresh()


class CursesLayout(WindowLayout):
    LOGGER_H = 20
    STATS_W = 40
    MAP_W = 30

    def __init__(self, screen, config_data: dict) -> None:
        super().__init__(config_data=config_data)

        screen.nodelay(1)
        self.screen = screen

        self.logger = self._create_logger_window(screen=screen)
        # This sets up console and file logging
        initialize_logging(
            game_name="Evoland", config_data=config_data, curses_win=self.logger.window
        )
        self.main = self._create_main_window(screen=screen)
        self.stats = self._create_stats_window(screen=screen)
        self.map = self._create_map_window(screen=screen)

        self._create_borders(screen=screen)
        screen.refresh()

    def _create_logger_window(self, screen) -> CursesWindow:
        # Determine the dimensions of the logger window
        maxy, maxx = screen.getmaxyx()
        begin_y, begin_x = maxy - self.LOGGER_H + 1, 1
        height, width = self.LOGGER_H - 2, maxx - 2
        return CursesWindow(
            Box2(pos=Vec2(begin_x, begin_y), w=width, h=height), auto_scroll=True
        )

    def _create_main_window(self, screen):
        # Determine the dimensions of the logger window
        maxy, maxx = screen.getmaxyx()
        begin_y, begin_x = 1, 1
        height, width = maxy - self.LOGGER_H - 1, maxx - self.STATS_W - self.MAP_W - 4
        # Create curses window to hold the main data
        return CursesWindow(Box2(pos=Vec2(begin_x, begin_y), w=width, h=height))

    def _create_stats_window(self, screen):
        # Determine the dimensions of the stats window
        maxy, maxx = screen.getmaxyx()
        begin_y, begin_x = 1, maxx - self.STATS_W - self.MAP_W - 2
        height, width = maxy - self.LOGGER_H - 1, self.STATS_W
        # Create curses window to hold the gamestate data
        return CursesWindow(Box2(pos=Vec2(begin_x, begin_y), w=width, h=height))

    def _create_map_window(self, screen):
        # Determine the dimensions of the stats window
        maxy, maxx = screen.getmaxyx()
        begin_y, begin_x = 1, maxx - self.MAP_W - 1
        height, width = maxy - self.LOGGER_H - 1, self.MAP_W
        # Create curses window to hold the gamestate data
        return CursesWindow(Box2(pos=Vec2(begin_x, begin_y), w=width, h=height))

    def _create_borders(self, screen):
        maxy, maxx = screen.getmaxyx()
        # ls, rs, ts, bs, tl, tr, bl, br
        # Leaving everything as 0 will use the default borders
        screen.border(0, 0, 0, 0, 0, 0, 0, 0)
        screen.move(maxy - self.LOGGER_H, 1)
        screen.hline(curses.ACS_HLINE, maxx - 2)
        screen.move(1, maxx - self.STATS_W - self.MAP_W - 3)
        screen.vline(curses.ACS_VLINE, maxy - self.LOGGER_H - 1)
        screen.move(1, maxx - self.MAP_W - 2)
        screen.vline(curses.ACS_VLINE, maxy - self.LOGGER_H - 1)

    def update(self):
        # Update display windows
        self.main.update()
        self.stats.update()
        self.map.update()
        curses.doupdate()


def setup_curses(screen, config_data: dict, func):
    window = CursesLayout(screen, config_data=config_data)
    func(window=window)

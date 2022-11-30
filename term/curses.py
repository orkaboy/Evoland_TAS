import curses
from curses import wrapper as curses_wrapper

from term.log_init import initialize_logging


def entry_point(config_data: dict, func):
    curses_wrapper(setup_curses, config_data, func)


class WindowLayout:
    LOGGER_H = 25
    STATS_W = 25
    MAP_W = 30

    def __init__(self, screen, config_data: dict) -> None:
        screen.nodelay(1)
        self.config_data = config_data
        self.screen = screen

        self.logger = self._create_logger_window(screen=screen)
        # This sets up console and file logging
        initialize_logging(
            game_name="Evoland", config_data=config_data, curses_win=self.logger
        )
        self.main = self._create_main_window(screen=screen)
        self.stats = self._create_stats_window(screen=screen)
        self.map = self._create_map_window(screen=screen)

        self._create_borders(screen=screen)
        screen.refresh()

    def _create_logger_window(self, screen):
        # Determine the dimensions of the logger window
        maxy, maxx = screen.getmaxyx()
        begin_y, begin_x = maxy - self.LOGGER_H + 1, 1
        height, width = self.LOGGER_H - 2, maxx - 2
        # Create curses window to hold the logger
        logger_win = curses.newwin(height, width, begin_y, begin_x)
        # Set parameters on window so that it scrolls automatically
        logger_win.refresh()
        logger_win.scrollok(True)
        logger_win.idlok(True)
        logger_win.leaveok(True)
        return logger_win

    def _create_main_window(self, screen):
        # Determine the dimensions of the logger window
        maxy, maxx = screen.getmaxyx()
        begin_y, begin_x = 1, 1
        height, width = maxy - self.LOGGER_H - 1, maxx - self.STATS_W - self.MAP_W - 4
        # Create curses window to hold the main data
        main_win = curses.newwin(height, width, begin_y, begin_x)
        main_win.refresh()
        return main_win

    def _create_stats_window(self, screen):
        # Determine the dimensions of the stats window
        maxy, maxx = screen.getmaxyx()
        begin_y, begin_x = 1, maxx - self.STATS_W - self.MAP_W - 2
        height, width = maxy - self.LOGGER_H - 1, self.STATS_W
        # Create curses window to hold the gamestate data
        stats_win = curses.newwin(height, width, begin_y, begin_x)
        stats_win.refresh()
        return stats_win

    def _create_map_window(self, screen):
        # Determine the dimensions of the stats window
        maxy, maxx = screen.getmaxyx()
        begin_y, begin_x = 1, maxx - self.MAP_W - 1
        height, width = maxy - self.LOGGER_H - 1, self.MAP_W
        # Create curses window to hold the gamestate data
        map_win = curses.newwin(height, width, begin_y, begin_x)
        map_win.refresh()
        return map_win

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

    def write_stats_centered(self, line: int, text: str):
        _, maxx = self.stats.getmaxyx()
        text_len = len(text)
        x_off = int(maxx / 2 - text_len / 2)
        self.stats.addstr(line, x_off, text)

    def write_map_centered(self, line: int, text: str):
        _, maxx = self.map.getmaxyx()
        text_len = len(text)
        x_off = int(maxx / 2 - text_len / 2)
        self.map.addstr(line, x_off, text)

    def update(self):
        # Update display windows
        self.main.noutrefresh()
        self.stats.noutrefresh()
        self.map.noutrefresh()
        curses.doupdate()


def setup_curses(screen, config_data: dict, func):
    window = WindowLayout(screen, config_data=config_data)

    func(window=window)

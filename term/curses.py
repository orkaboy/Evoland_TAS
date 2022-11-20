import curses
from curses import wrapper as curses_wrapper

from term.log_init import initialize_logging


def entry_point(config_data: dict, func):
    curses_wrapper(setup_curses, config_data, func)


logger_height = 15
stats_width = 20


def create_logger_window(screen):
    # Determine the dimensions of the logger window
    maxy, maxx = screen.getmaxyx()
    begin_y, begin_x = maxy - logger_height + 1, 1
    height, width = logger_height - 2, maxx - 2
    # Create curses window to hold the logger
    logger_win = curses.newwin(height, width, begin_y, begin_x)
    # Set parameters on window so that it scrolls automatically
    logger_win.refresh()
    logger_win.scrollok(True)
    logger_win.idlok(True)
    logger_win.leaveok(True)
    return logger_win


def create_main_window(screen):
    # Determine the dimensions of the logger window
    maxy, maxx = screen.getmaxyx()
    begin_y, begin_x = 1, 1
    height, width = maxy - logger_height - 1, maxx - stats_width - 3
    # Create curses window to hold the main data
    main_win = curses.newwin(height, width, begin_y, begin_x)
    # Set parameters on window so that it scrolls automatically
    main_win.refresh()
    return main_win


def create_stats_window(screen):
    # Determine the dimensions of the stats window
    maxy, maxx = screen.getmaxyx()
    begin_y, begin_x = 1, maxx - stats_width - 1
    height, width = maxy - logger_height - 1, stats_width
    # Create curses window to hold the gamestate data
    stats_win = curses.newwin(height, width, begin_y, begin_x)
    # Set parameters on window so that it scrolls automatically
    stats_win.refresh()
    return stats_win


def write_stats_centered(stats_win, line: int, text: str):
    _, maxx = stats_win.getmaxyx()
    text_len = len(text)
    x_off = int(maxx / 2 - text_len / 2)
    stats_win.addstr(line, x_off, text)


def create_borders(screen):
    maxy, maxx = screen.getmaxyx()
    # ls, rs, ts, bs, tl, tr, bl, br
    # Leaving everything as 0 will use the default borders
    screen.border(0, 0, 0, 0, 0, 0, 0, 0)
    screen.move(maxy - logger_height, 1)
    screen.hline(curses.ACS_HLINE, maxx - 2)
    screen.move(1, maxx - stats_width - 2)
    screen.vline(curses.ACS_VLINE, maxy - logger_height - 1)


def setup_curses(screen, config_data: dict, func):
    screen.nodelay(1)

    logger_win = create_logger_window(screen=screen)
    # This sets up console and file logging
    initialize_logging(
        game_name="Evoland", config_data=config_data, curses_win=logger_win
    )

    main_win = create_main_window(screen=screen)
    stats_win = create_stats_window(screen=screen)
    create_borders(screen=screen)
    screen.refresh()

    func(main_win=main_win, stats_win=stats_win, config_data=config_data)

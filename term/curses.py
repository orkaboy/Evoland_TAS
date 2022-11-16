import curses
from curses import wrapper as curses_wrapper

from term.log_init import initialize_logging


def entry_point(config_data: dict, func):
    curses_wrapper(setup_curses, config_data, func)


logger_height = 15
stats_width = 25


def create_logger_window(screen):
    # Determine the dimensions of the logger window
    maxy, maxx = screen.getmaxyx()
    begin_y, begin_x = maxy - logger_height, 1
    height, width = logger_height, maxx - 2
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
    begin_y, begin_x = 0, 0
    height, width = maxy - logger_height, maxx - stats_width
    # Create curses window to hold the main data
    main_win = curses.newwin(height, width, begin_y, begin_x)
    # Set parameters on window so that it scrolls automatically
    main_win.refresh()

    return main_win


def create_stats_window(screen):
    # Determine the dimensions of the stats window
    maxy, maxx = screen.getmaxyx()
    begin_y, begin_x = 0, maxx - stats_width
    height, width = maxy - logger_height, stats_width
    # Create curses window to hold the gamestate data
    stats_win = curses.newwin(height, width, begin_y, begin_x)
    # Set parameters on window so that it scrolls automatically
    stats_win.refresh()

    return stats_win


def setup_curses(screen, config_data: dict, func):
    screen.nodelay(1)

    logger_win = create_logger_window(screen=screen)
    # This sets up console and file logging
    initialize_logging(
        game_name="Evoland", config_data=config_data, curses_win=logger_win
    )

    main_win = create_main_window(screen=screen)
    stats_win = create_stats_window(screen=screen)

    func(main_win=main_win, stats_win=stats_win, config_data=config_data)

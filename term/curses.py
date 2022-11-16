import curses
from curses import wrapper as curses_wrapper

from term.log_init import initialize_logging


def entry_point(config_data: dict):
    curses_wrapper(main_menu, config_data)


def create_logger_window(screen):
    # Determine the dimensions of the logger window
    maxy, maxx = screen.getmaxyx()
    begin_x = 1
    height = 15
    begin_y = maxy - height
    width = maxx - 2
    # Create curses window to hold the logger
    logger_win = curses.newwin(height, width, begin_y, begin_x)
    # Set parameters on window so that it scrolls automatically
    logger_win.refresh()
    logger_win.scrollok(True)
    logger_win.idlok(True)
    logger_win.leaveok(True)

    return logger_win


def main_menu(screen, config_data: dict):
    screen.nodelay(1)

    logger_win = create_logger_window(screen)
    # This sets up console and file logging
    initialize_logging(
        game_name="Evoland", config_data=config_data, curses_win=logger_win
    )

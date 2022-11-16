# This needs to be before the other imports in case they decide to log things when imported
# Libraries
# import logging

import config

# from term.log_init import initialize_logging

# This sets up console and file logging (should only be called once)
# initialize_logging(game_name="Evoland", config_data=config_data)

# logger = logging.getLogger(__name__)

# Main entry point of TAS
if __name__ == "__main__":
    # logger.info("Initialized logging.")

    config_data = config.open_config()
    from term.curses import entry_point

    entry_point(config_data)

    # from term.main_menu import main_menu

    # Capture and log top level exceptions
    # try:
    # main_menu(config_data)
    # logger.info("TAS exited cleanly")
    # except Exception as E:
    # logger.exception(E)

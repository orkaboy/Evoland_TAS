# This needs to be before the other imports in case they decide to log things when imported
# Libraries
import logging

import config
import log_init

# This sets up console and file logging (should only be called once)
config_data = config.open_config()
log_init.initialize_logging(game_name="Evoland", config_data=config_data)

from main_menu import main_menu

logger = logging.getLogger(__name__)

# Main entry point of TAS
if __name__ == "__main__":
    logger.info("Initialized logging.")

    # Capture and log top level exceptions
    try:
        main_menu(config_data)
        logger.info("TAS exited cleanly")
    except Exception as E:
        logger.exception(E)

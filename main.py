# This needs to be before the other imports in case they decide to log things when imported
# Libraries
import logging

import config
import log_init

logger = logging.getLogger(__name__)

# Main entry point of TAS
if __name__ == "__main__":
    # This sets up console and file logging (should only be called once)
    config_data = config.open_config()
    game_name = config_data.get("game", "Evoland1")
    log_init.initialize_logging(game_name=game_name, config_data=config_data)

    logger.info("Hello world")

# This needs to be before the other imports in case they decide to log things when imported
# Libraries
import logging

import config
import log_init

# This sets up console and file logging (should only be called once)
config_data = config.open_config()
game_name = config_data.get("game", "Evoland1")
log_init.initialize_logging(game_name=game_name, config_data=config_data)

import evo1.TAS as evo1
import evo2.TAS as evo2

logger = logging.getLogger(__name__)

# Main entry point of TAS
if __name__ == "__main__":
    logger.info("Initialized logging.")

    try:
        if game_name == "Evoland1":
            evo1.perform_TAS(config_data)
        elif game_name == "Evoland2":
            evo2.perform_TAS(config_data)
        else:
            logger.error(f"Invalid game name: {game_name}. Exiting...")

        logger.info("TAS exited cleanly")
    except Exception as E:
        logger.exception(E)

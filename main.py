import config
from term.curses import entry_point
from term.main_menu import main_menu

# Main entry point of TAS
if __name__ == "__main__":
    # Read config data from file
    config_data = config.open_config()
    # Initialize ncurses and print the main menu
    entry_point(config_data, main_menu)

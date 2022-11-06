from consolemenu import *
from consolemenu.items import *

import evo1.TAS as evo1
import evo2.TAS as evo2


def main_menu(config_data: dict):
    # Create the menu
    menu = ConsoleMenu("Evoland TAS", "Automated speedrun")

    # Main TAS entries
    evo1_menu = ConsoleMenu(title="Evoland1 TAS")
    evo1_start = FunctionItem(
        text="Start Evoland1 TAS",
        function=evo1.perform_TAS,
        args=[config_data],
        menu=evo1_menu,
    )
    evo1_menu.append_item(evo1_start)

    evo2_menu = ConsoleMenu(title="Evoland2 TAS")
    evo2_start = FunctionItem(
        text="Start Evoland2 TAS",
        function=evo2.perform_TAS,
        args=[config_data],
        menu=evo2_menu,
    )
    evo2_menu.append_item(evo2_start)

    # Populate main menu with items
    menu.append_item(SubmenuItem(text="Evoland1", submenu=evo1_menu, menu=menu))
    menu.append_item(SubmenuItem(text="Evoland2", submenu=evo2_menu, menu=menu))

    # Show the interactible menu. This will return once exit is selected
    menu.show()

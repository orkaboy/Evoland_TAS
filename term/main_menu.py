import curses

import evo1.TAS as evo1
import evo2.TAS as evo2


def main_menu(main_win, stats_win, config_data: dict):
    while True:
        # Declare menu options
        options = [
            {
                "name": "Evoland 1",
                "key": "1",
                "func": evo1.perform_TAS,
            },
            {
                "name": "Evoland 2",
                "key": "2",
                "func": evo2.perform_TAS,
            },
        ]

        # Update side window
        stats_win.clear()
        stats_win.addstr(1, 0, "+ Evoland TAS +")
        stats_win.addstr(2, 0, "    author:    ")
        stats_win.addstr(3, 0, "    orkaboy    ")
        stats_win.noutrefresh()

        # Update main window
        main_win.clear()
        line = 1
        for opt in options:
            key = opt.get("key", "x")
            text = opt.get("name", "ERROR")
            main_win.addstr(line, 1, f"({key})  {text}")
            line = line + 1
        line = line + 1
        main_win.addstr(line, 1, "(q) Quit")
        main_win.noutrefresh()

        # Update screen
        curses.doupdate()

        do_refresh = True
        # Get user input
        while do_refresh:
            c = main_win.getch()
            if c == ord("q"):
                return  # Quit

            # Iterate over options
            for opt in options:
                key = opt.get("key", "x")
                func = opt.get("func", None)
                if c == ord(key) and func != None:
                    # Call subfunction
                    func(
                        main_win=main_win, stats_win=stats_win, config_data=config_data
                    )
                    # Break loop to refresh screen
                    do_refresh = False

import evo1
import evo2
from app import TAS_VERSION_STRING
from engine.mathlib import Vec2
from memory.seq_rng_observer import rng_observer
from term.window import WindowLayout


def main_menu(window: WindowLayout):
    while True:
        # Declare menu options
        options = [
            {
                "name": "Evoland 1",
                "key": "1",
                "func": evo1.perform_TAS,
            },
            {
                "name": "Evoland 1 Observer",
                "key": "2",
                "func": evo1.observer,
            },
            {
                "name": "Evoland 2",
                "key": "3",
                "func": evo2.perform_TAS,
            },
            {
                "name": "RNG Observer",
                "key": "4",
                "func": rng_observer,
            },
        ]

        # Update side window
        window.stats.erase()
        window.stats.write_centered(line=1, text="+ Evoland TAS +")
        window.stats.write_centered(line=2, text=TAS_VERSION_STRING)
        window.stats.write_centered(line=4, text="author:")
        window.stats.write_centered(line=5, text="orkaboy")
        window.stats.update()

        # Update main window
        window.main.erase()
        line = 1
        for opt in options:
            key = opt.get("key", "x")
            text = opt.get("name", "ERROR")
            window.main.addstr(Vec2(1, line), f"({key}) {text}")
            line = line + 1
        line = line + 1
        window.main.addstr(Vec2(1, line), "(q) Quit")

        # Update screen
        window.update()
        window.main.nodelay(False)

        do_refresh = True
        # Get user input
        while do_refresh:
            c = window.main.getch()
            if c == ord("q"):
                return  # Quit

            # Iterate over options
            for opt in options:
                key = opt.get("key", "x")
                func = opt.get("func", None)
                if c == ord(key) and func is not None:
                    window.main.nodelay(True)
                    # Call subfunction
                    func(window=window)
                    # Break loop to refresh screen
                    do_refresh = False

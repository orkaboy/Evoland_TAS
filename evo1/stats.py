from evo1.memory import Evoland1Memory


# Decorator
def stats_2d(stats_win):
    # Update stats window
    mem = Evoland1Memory()
    stats_win.clear()
    stats_win.addstr(1, 1, "Evoland 1 TAS")
    stats_win.addstr(2, 1, "2D section")
    pos = mem.get_player_pos()
    stats_win.addstr(4, 1, f"  Player X: {pos[0]:.3f}")
    stats_win.addstr(5, 1, f"  Player Y: {pos[1]:.3f}")
    facing = mem.get_player_facing_str(mem.get_player_facing())
    stats_win.addstr(6, 1, f"    Facing: {facing}")
    stats_win.noutrefresh()

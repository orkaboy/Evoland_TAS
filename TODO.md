# TODO list

* Clean up main menu navigation code?
* Pathfinding
    - Fix the pathfinding so it works for sub-tile/free movement
    - Fix the pathfinding to reduce the number of nav nodes/checkpoints, and have the TAS beeline for objectives when possible (use rays to detect map collision)
    - Create more maps (easier with zoom-cheat)
* Finish entire Edel1 segment
    - Fix combat to more consistently survive the pre-free move section
        + Predict where enemies will be/what areas are threatened
        + Prevent attacking chests
        + Incorporate the waittimer to path more efficiently
    - Add combat that can kill the two knights
        + SeqKnight2D added (stub DONE, can track but not kill)
        + Set up plan
        + Set up movement functions for "juking" enemies
        + Restrict movement to inside arena (could be more free now since the map/obstacles are known)
        + Account for if enemies leave the arena zone
* Kill the four knights in the village
* Do more memory hunting
    - Verify the stuff from the discord

* Fix Curses gui color log if possible
    - Better yet, experiment more with Textual/Rich
* Write a sequence capture script that reads the memory and saves it, but doesn't control the game. Could possibly be used to "record" maps.
    - Ask in Discord if the maps/tiles can be extracted

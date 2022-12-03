# TODO list

* Clean up main menu navigation code?
* Pathfinding
    - Fix the pathfinding so it works for sub-tile/free movement
    - Fix the pathfinding to reduce the number of nav nodes/checkpoints, and have the TAS beeline for objectives when possible (use rays to detect map collision)
    - Improve on the AStar algorithm to use diagonal paths when we have free movement
* Finish entire Edel1 segment
    - Fix combat to more consistently survive the pre-free move section
        + Predict where enemies will be/what areas are threatened
        + Incorporate the waittimer to path more efficiently
* Add combat that can kill knights
    - Set up plan
    - Account for spaces that are threatened
* Cavern
    - Fix trigger tile (SeqHoldInPlace)
    - Diagonal movement
    - Fix smarter ATB combat
* Do more memory hunting
    - Verify the stuff from the discord
    - 3D enemies are stored elsewhere in memory? find where
* 3D Movement and combat
    - Handle 3D enemy detection/tracking
    - Handle pathfinding past breakable objects
    - Improve GrabChest logic (must be in correct position and approach). Can build together several steps into one

* Fix the trigger issues in Crystal Caverns

* Fix Curses gui color log if possible
    - Better yet, experiment more with Textual/Rich
* Write a sequence capture script that reads the memory and saves it, but doesn't control the game. Could possibly be used to "record" maps.

* Test out stuff with the evo classic codebase (EKind etc.)

# TODO list

* Clean up main menu navigation code?
* Pathfinding
    - Fix the pathfinding so it works for sub-tile movement
    - Fix the pathfinding to reduce the number of nav nodes/checkpoints, and have the TAS beeline for objectives when possible (use rays to detect map collision)
* Finish entire Edel1 segment
    - Fix combat to more consistently survive the pre-free move section
        + Predict where enemies will be/what areas are threatened
        + Incorporate the waittimer to path more efficiently
        + Use target value for enemies
* Add combat that can kill knights
    - Account for spaces that are invalid (not passable). Can use navmap here
    - Make this code reusable for enemies later
* Cavern
    - Fix smarter ATB combat
    - Track enemy hp, stats
    - Smart RNG manip to get favorable encounters
    - Defeat Kefka's Ghost
* Do more memory hunting
    - ATB combat values (Atk, Def, Acc, Evade, ATB gauge, Invincibility)
* 3D Movement and combat
    - Handle 3D enemy detection/tracking (Skellies/Mages)
    - Killing bats
    - Handle pathfinding past breakable objects (bushes/pots)
* Routing
    - Route Noria mines

* Terminal improvements
    - Move WindowLayout into abstract class with exposed methods to abstract away all curses code from TAS
    - Experiment more with Textual/Rich
* Write a sequence capture script that reads the memory and saves it, but doesn't control the game. Could possibly be used to "record" maps.

* Test out stuff with the evo classic codebase (EKind etc.)

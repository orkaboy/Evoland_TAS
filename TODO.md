# TODO list

* Next:
  * Go ahead a bit in the run and do a rough routing of the later parts (Aogai, Sacred Grove, Sarudnahk). Verify using saves
  * Display hp in zelda mode
  * Clink attacks from just out of range, swinging in the air
  * Solve floor puzzle
  * Navigate the fireballs/wind traps
  * Deathwarp? Some issues reloading currently (need to know which save slot we are using. For now, require use of slot 1?)
  * Bossfight Dark Clink
    * Observer in place, logic/math TODO

* Save games
  * Clean up main menu navigation code? Checking for if New game is available
  * Actually use menu memory pos
  * Load game will not work correctly if all 5 saves are used

* Do more memory hunting
  * ATB
    * Potion/phoenix down usage (item amount/pos in menu)
    * Logic for the current active turn (use turn gauge)
  * Sarudnahk
    * Health
    * Enemies
    * Boss

* Pathfinding
  * Fix the pathfinding to reduce the number of nav nodes/checkpoints, and have the TAS beeline for objectives when possible (use rays to detect map collision)
* Improve knights combat logic
  * Account for spaces that are invalid (not passable). Can use navmap here
* Cavern
  * Improve on encounter manip logic
    * Read chest timers from memory and avoid moving just before they advance RNG
* 3D Movement and combat
  * Handle pathfinding past breakable objects (bushes/pots). Can do this manually, but it's less elegant
* Routing
  * Route Noria mines
  * Route Aogai/Bomb skip
  * Route Sacred Grove
  * Route Sarudnahk
  * Zephyros ATB fight
* Final Zephyros fight
  * Improve/optimize movement
  * Get in 3-4 attacks in the first phase
  * Dodge attacks in armless phase
  * Dodge red attacks in Ganon phase


* Terminal improvements
  * Experiment more with Textual/Rich
  * Fix so that the map/stats window has fixed height, to prevent crashes when the window is too small

* Write a sequence capture script that reads the memory and saves it, but doesn't control the game. Could possibly be used to "record" maps.

* Test out stuff with the evo classic codebase (EKind etc.)

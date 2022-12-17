# TODO list

* Next:
  * Go ahead a bit in the run and do a rough routing of the later parts (Aogai, Sacred Grove, Sarudnahk). Verify using saves
  * Display hp in zelda mode
  * Clink attacks from just out of range, swinging in the air
  * Killing 3 skellies (knight-like logic, but in 3d, using modified rotation angle)
    * This logic can be applied to knights combat also
  * Skip past the first skeleton without fighting it
  * Juke the two skellies before push block
  * Push armored enemy into pit
  * Navigate the maze (easy)/fireballs/wind traps
  * Knight combat: Prevent standing next to the knight while it's invulnerable
  * Start doing cutscene skips with menu-glitch
  * Deathwarp? Some issues reloading currently (need to know which save slot we are using. For now, require use of slot 1?)
  * Bossfight Dark Clink

* Do more memory hunting
  * Dark Clink attack/vulnerable state
  * ATB
    * Cursor position in menues
    * Potion/phoenix down usage (item amount/pos in menu)
    * Logic for the current active turn (use turn gauge)

* Clean up main menu navigation code? Checking for if New game is available
* Pathfinding
  * Fix the pathfinding so it works for sub-tile movement (approximate, then inject real goal at last node)
  * Fix the pathfinding to reduce the number of nav nodes/checkpoints, and have the TAS beeline for objectives when possible (use rays to detect map collision)
* Improve knights combat logic
  * Account for spaces that are invalid (not passable). Can use navmap here
* Cavern
  * Fix smarter ATB combat (run/heal)
    * Should take any low damage encounter and run before the exp chest
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

* Terminal improvements
  * Experiment more with Textual/Rich
  * Fix so that the map/stats window has fixed height, to prevent crashes when the window is too small

* Write a sequence capture script that reads the memory and saves it, but doesn't control the game. Could possibly be used to "record" maps.

* Test out stuff with the evo classic codebase (EKind etc.)

# TODO list

* Next:
  * Killing 3 skellies (knight-like logic, but in 3d, using modified rotation angle)
    * This logic can be applied to knights combat also
  * Skip past the first skeleton without fighting it
  * Push armored enemy into pit
  * Navigate the maze/fireballs
  * Deathwarp? Some issues reloading currently
  * Bossfight

* Clean up main menu navigation code? This logic should be reusable for evo2 as well, shouldn't be in the "start" sequence of evo1
* Pathfinding
  * Fix the pathfinding so it works for sub-tile movement (approximate, then inject real goal at last node)
  * Fix the pathfinding to reduce the number of nav nodes/checkpoints, and have the TAS beeline for objectives when possible (use rays to detect map collision)
* Finish entire Edel1 segment
  * Fix combat to more consistently survive the pre-free move section
    * Predict where enemies will be/what areas are threatened
    * Incorporate the waittimer to path more efficiently
    * Use target value for enemies
* Improve knights combat logic
  * Account for spaces that are invalid (not passable). Can use navmap here
* Cavern
  * Fix smarter ATB combat (run/heal)
* Do more memory hunting
  * Cursor position in menues
  * Logic for the current active turn (use turn gauge)
* 3D Movement and combat
  * Clink attacks from just out of range, swinging in the air
  * Handle 3D enemy detection/tracking (Skellies/Mages)
  * Handle pathfinding past breakable objects (bushes/pots). Can do this manually, but it's less elegant
* Routing
  * Route Noria mines
  * Start doing cutscene skips with menu-glitch

* Terminal improvements
  * Experiment more with Textual/Rich
  * Fix so that the map/stats window has fixed height, to prevent crashes when the window is too small

* Write a sequence capture script that reads the memory and saves it, but doesn't control the game. Could possibly be used to "record" maps.

* Test out stuff with the evo classic codebase (EKind etc.)

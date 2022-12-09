# TODO list

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
  * Fix smarter ATB combat
    * Set up ATB combat handler for combat
  * Defeat Kefka's Ghost
* Do more memory hunting
  * Cursor position in menues
  * Logic for the current active turn (use turn gauge)
  * Inspect pointer path to battle struct, to see if it can be use to decide if combat is active or not
    * It can (0x860, 0x0, 0x244), but it remains even after combat is done. It will be allocated again on new combat
* 3D Movement and combat
  * Clink attacks from just out of range, swinging in the air
  * Handle 3D enemy detection/tracking (Skellies/Mages)
  * Killing bats (some detection issues atm)
    * Could also use improvement; currently tries to move away from the bats rather than killing them if they're too close. Check radial collision
  * Killing 3 skellies (knight-like logic, but in 3d, using modified rotation angle)
  * Handle pathfinding past breakable objects (bushes/pots). Can do this manually, but it's less elegant
* Routing
  * Route Noria mines
  * Push armored enemy into pit
  * Start doing cutscene skips with menu-glitch

* Terminal improvements
  * Experiment more with Textual/Rich
  * Fix so that the map/stats window has fixed height, to prevent crashes when the window is too small

* Write a sequence capture script that reads the memory and saves it, but doesn't control the game. Could possibly be used to "record" maps.

* Test out stuff with the evo classic codebase (EKind etc.)

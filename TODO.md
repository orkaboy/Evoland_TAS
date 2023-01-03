# TODO list

* Route Sarudnahk
  * Usage of heal glitch
  * Survival/movement, comboing
  * Lich boss fight
  * Navmesh for Sarudnahk?
  * Map for Saurdnahk?
* Blackboard code
  * Need to track what glitches we have active, especially when using save/load


# Improvements for later

* Do more memory hunting
  * Sarudnahk
    * Health
    * Boss (projectiles)

* Seq:
  * Make a SeqConditional (can inherit from) - could do if/match
  * Make a SeqWhile/For or similar to allow for routing loops

* Save games/Main menu
  * Clean up main menu navigation code? Checking for if New game is available
  * Actually use menu memory pos
  * Load game will not work correctly if all 5 saves are used

* 3D Movement and combat
  * Display hp in zelda mode
  * Clink attacks from just out of range, swinging in the air
  * Handle pathfinding past breakable objects (bushes/pots). Can do this manually, but it's less elegant
  * Use joystick for free movement
* Pathfinding
  * Fix the pathfinding to reduce the number of nav nodes/checkpoints, and have the TAS beeline for objectives when possible (use rays to detect map collision)
  * Path adjustments due to being hit/diverging for attacks
    * Use the full navmap, don't recalculate AStar? This would require holding all the navmaps in memory, so maybe not so good.

* Improve knights combat logic
  * Account for spaces that are invalid (not passable). Can use navmap here
* Overworld gli farm
  * Improve on encounter manip logic
    * Allow for entering/leaving Meadow as manip (relatively quick, worth it? Consistency?)
* Cavern
  * Improve on encounter manip logic
    * Read chest timers from memory and avoid moving just before they advance RNG?
* Noria
  * Improve on 2xBat room (can fail detection)
  * Fallback for floor puzzle
  * Fallback for fireballs? Can sometimes fail on this section.
  * Deathwarp
    * Allow for other save slots than 0 to be used
    * Bugs in timing. Use cursor memory value to ensure we are actually selecting things correctly
  * Bossfight Dark Clink
    * Make the logic more complicated (though maybe it doesn't need to be?)
    * Menu glitch after boss death
* Aogai
  * Map for display.
* Sacred Grove
  * Fallbacks for accidentally killing bats with the arrows in the puzzle
    * Safety could be to just kill the first bat?
  * Menu glitches
* Zephyros ATB fight
  * Double turns confuse the TAS (when both Clink and Kaeris act at the same time). Kaeris will take the wrong action
  * Fallback for if we run out of potions
* Final Zephyros fight
  * Improve/optimize movement
  * Get in 3-4 attacks in the first phase
  * Dodge attacks in armless phase
  * Dodge red attacks in Ganon phase


* Terminal improvements
  * Experiment more with Textual/Rich
  * Fix so that the map/stats window has fixed height, to prevent crashes when the window is too small

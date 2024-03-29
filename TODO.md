# TODO list

* Route Sarudnahk
  * Survival/movement
    * Tweak boid behavior (weights)
      * Need to become better at juking/avoiding getting hit
      * Need to handle the skeletons differently, they hit very hard (bigger weight to avoid)
      * Need to avoid getting stuck on terrain
      * Fix heal glitch (can switch to "no" option)
    * Improve health pickup code
      * (r^2 distance? Must find a way to only prioritize closest, or risk missing a bunch)
      * Weight according to health level
      * Maybe just pick closest and put all boid behavior on that
      * Must avoid issues where the code locks movement
  * Lich boss fight
    * Completing combo correctly when fighting Lich (sometimes fails to combo)
    * Movement post-battle (gets stuck on rocks). Boid-like behavior with list of obstacles?

* Fix saves so that shopkeeper is unlocked:
(Could also check in final turn if the shopkeeper/chest is there and adjust)
  * sacred_grove
  * amulet_cave
  * aogai2
  * black_citadel

## Improvements for later

* Save games/Main menu
  * Clean up main menu navigation code? Checking for if New game is available
  * Actually use menu memory pos
  * Load game will not work correctly if all 5 saves are used

* 3D Movement and combat
  * Display hp in zelda mode
  * Clink attacks from just out of range, swinging in the air
  * Handle pathfinding past breakable objects (bushes/pots). Can do this manually, but it's less elegant
* Pathfinding
  * Fix the pathfinding to reduce the number of nav nodes/checkpoints, and have the TAS beeline for objectives when possible (use rays to detect map collision)
  * Path adjustments due to being hit/diverging for attacks
    * Use the full navmap, don't recalculate AStar? This would require holding all the navmaps in memory, so maybe not so good

* Improve knights combat logic
  * Account for spaces that are invalid (not passable). Can use navmap here
* Overworld gli farm
  * Improve on encounter manip logic
    * Allow for entering/leaving Meadow as manip (relatively quick, worth it? Consistency?)
* Papurika
  * Minor pathing issues
* Cavern
  * Improve on encounter manip logic
    * Read chest timers from memory and avoid moving just before they advance RNG?
* Noria
  * Improve on 2xBat room (can fail detection). Should menu-skip on bat kills.
  * Improve on skeleton juking. Can lure the first one to not get in the way.
  * Fallback for floor puzzle (need to know when we fail)
  * Add menu-manip on floor puzzle end.
  * Fallback for fireballs? Can sometimes fail on this section (need to be able to reset the maze)
  * Deathwarp
    * Allow for other save slots than 0 to be used
    * Bugs in timing. Use cursor memory value to ensure we are actually selecting things correctly
  * Bossfight Dark Clink
    * Make the logic more complicated (though maybe it doesn't need to be?)
    * Menu glitch after boss death
* Aogai
  * Map for display
* Sacred Grove
  * Optimize weapon swapping in the south-east puzzle
  * Fallbacks for accidentally killing bats with the arrows in the puzzle
    * Safety could be to just kill the first bat?
    * Can check for statue on the way north and shoot an arrow.
  * Menu glitches
* Zephyros ATB fight
  * Double turns confuse the TAS (when both Clink and Kaeris act at the same time). Kaeris will take the wrong action
  * Fallback for if we run out of potions (hasn't happened so far, but could in theory)
* Final Zephyros fight
  * Improve/optimize movement
  * Get in 3-4 attacks in the first phase
  * Dodge attacks in armless phase (run in the correct direction)
  * Improve on movement in armless phase (doesn't correctly anticipate where the enemy will end up. Sometimes hit twice)
  * Dodge red attacks in Ganon phase (detect, move out of the way) if we are low on health

* Terminal improvements
  * Experiment more with Textual/Rich
  * Fix so that the map/stats window has fixed height, to prevent crashes when the window is too small

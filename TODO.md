# TODO list

* Route Aogai bomb skip (WIP), tying the Noria and Sacred Grove segments together
* Route Aogai segments (Bomb skip, heal glitch for Sarudnahk, Buying pots for Zephy, getting airship)
* Automate the skeleton/mage fight in the Amulet cave
* Route Sacred Grove (fallbacks for killing bats, menu glitches, killing skellies/mages)
* Route Sarudnahk (heal glitch, survival/movement, boss fight, comboing)
* Zephyros ATB fight (phase detection, healing, X-crystal, 2nd phase, babamut)

# Improvements for later

* Do more memory hunting
  * ATB
    * Potion/phoenix down usage (item amount/pos in menu)
    * Logic for the current active turn (use turn gauge)
  * Sarudnahk
    * Health
    * Enemies
    * Boss

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
  * Deathwarp. Allow for other save slots than 0 to be used
  * Bossfight Dark Clink
    * Make the logic more complicated (though maybe it doesn't need to be?)
    * Menu glitch after boss death
* Final Zephyros fight
  * Improve/optimize movement
  * Get in 3-4 attacks in the first phase
  * Dodge attacks in armless phase
  * Dodge red attacks in Ganon phase


* Terminal improvements
  * Experiment more with Textual/Rich
  * Fix so that the map/stats window has fixed height, to prevent crashes when the window is too small

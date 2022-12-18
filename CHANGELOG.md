# Current

0.0.6:

* The TAS can somewhat reliably kill the final boss of the game
* Added rng tracker to TAS display
* Added Crystal Caverns menu manipulation
* Improved on Crystal Caverns ATB battle manipulation (can now run)


# Older changelogs

0.0.5:

* Added full attack prediction, in and out of combat
* Improved on ATB combat detection and state tracking
* TAS can now kill Kefka's Ghost on its own
* A very minimal Evoland 2 TAS
* Early game, prevented running headlong into enemies before free move

0.0.4:

* Battle stats and damage prediction
* ATB Encounter prediction and manipulation on overworld map
* ATB Encounter prediction and manipulation in the crystal caverns
* Massive refactoring of code, splitting into files
* Refactored knights combat to be reusable. Can currently kill the forced bats in Noria
* Pathed Noria up to the bottomless pit
* Current manual sections:
  * Kefka's Ghost
  * Killing 3 skellies in Noria
  * Pushing the armored enemy into the pit
  * (Some more the TAS hasn't reached yet)

0.0.3:

* TAS can progress to the start of Noria mines (though it needs some handholding against Kefka's Ghost)
  * Pathing done to the start of the maze
* Improvements to knight combat
* Zone transitions are now verified against memory
* A lot of backend work to make RNG prediction possible
* Added countdown to main menu
* Added diagonal movement to pathfinding

0.0.2:

* TAS now loads maps from tmx (village/cavern)
* TAS can now progress through cavern up to Kefka's Ghost (some pathing issues remain)
* TAS can now kill the knights! No manual intervention required anymore

0.0.1:

* Added timer to the main window
* TAS no longer blindly attacks chests (can differentiate between different types of actors)
* TAS now loads maps from pngs (both for display and pathfinding)
* TAS can now progress until the end of Papurika village (with manual help for knight fights)

0.0.0:

* Initial version of the TAS

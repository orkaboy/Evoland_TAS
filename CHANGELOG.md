# Current

0.0.9:

* Added simple boid behavior for Sarudnahk. Not able to complete the dungeon yet.
* Added a map for Sarudnahk. Nav graph is used for pathing, not AStar.
* Added a timekeeping module to log segment timing.
* Added backend: SeqIf/SeqWhile building blocks. Removed SeqOptional.

# Older changelogs

0.0.8:

* Routed Aogai bomb skip (tying together Noria Mines and Sacred Grove segments)
* Routed initial Sacred Grove section. Very buggy and prone to failure.
* Routed Aogai airship pickup and navigation to the Mana Tree.
* Now tracking IKind of KInteract entities. These are for example fireballs, arrows, bombs, hearts etc.
* Drawing entities with unique symbols (different types of enemies look different on the mini-map).
* Fixed some broken pathing on the world map due to missing tiles.
* Backend work on evo2.

0.0.7:

* TAS can perform a deathwarp in Noria Mines, skipping a forced combat encounter. Note! This requires using save slot 1, either from new game or when loading.
* TAS can kill Dark Clink boss, making the Noria section completely automated (if unreliable).
* Very crude routing of Sarudnahk. Can't make it through without help/cheats.
* Very crude routing of Sacred Grove. Has some minor issues still.
* TAS can kill Zephyros in the first ATB battle.
* Very crude routing of Aogai sections. Need more work.

0.0.6:

* Added rng tracker to TAS display
* Improved on the ability to load saves. Saves uploaded, provided by Zatura24
* Minor optimization in Papurika Village (shopping)
* Added Crystal Caverns menu manipulation
* Improved on Crystal Caverns ATB battle manipulation (can now run)
* Added some menu manipulation glitches in Noria Mines
* Major glitch getting two keys at the start of the Noria Mines implemented
* The TAS can defeat the armored enemy in Noria Mines
* The TAS can navigate the wind traps in Noria Mines
* The TAS can somewhat reliably solve the floor puzzle in Noria Mines
* The TAS can somewhat reliably get past the fireballs in Noria Mines
* Routed Sacred Grove up to Amulet cave
* The TAS can somewhat reliably kill the final boss of the game

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

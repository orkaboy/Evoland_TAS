# Memory Hunt

## TODO

* Main menu save slots

* Menu cursor stuff in combat (other than main ATB)

* Anything that can help with menu glitch manip

* Dark Clink attack/dizzy state

* Bomb/Bow usage

* Diablo section boss state. Health if needed

* Zephy ATB state

* Zephyros final arena movement
* Zephyros golem stats
* Zephyros Ganon stats + projectile tracking

## Found

Zatura24:
```
Found another field for the ATB entity structure. 0x118 is a double indicating how fast the turn gauge increases
if you set it to 1, you'll always attack

I might have another, 0x109 is a single byte indicating if you run away

I think, but not sure, that this 0xD0 is the current animation frame. And since attacking gives another animation, it seems like it resets

Found 2 others, 0x70 is the on screen x position, 0x78 is the on screen y position (both doubles). Which both also seem to be available at 0x10 and 0x18
Okay strange, 0x10 and 0x18 seem to be used by UI elements like damage and healing. And 0x70, 0x78 are the actual sprite location (which is writeable)

0x3C seems to be the name structure. Followed by 0x4 the string buffer, 0x8 the amount of chars
```

* Player level
* Kefka invincibility
* Current map
* Enemy projectiles (EKind.SPECIAL, actor array)
* Enemy stats in combat
* Player stats in combat
* Differentiate between enemies and other actors (chests etc.) in zelda mode.
* Player struct (x,y,direction) in world movement [ptr]
* In control
  * Inv open(?)
  * Is-in-battle (an ugly hack to start with)
* Attacking

* Enemy array in zelda-mode

* Gli amount
* Overworld health

* Kaeris health overworld DONE (needs testing)

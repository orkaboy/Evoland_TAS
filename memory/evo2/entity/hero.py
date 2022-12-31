from enum import IntEnum

from memory.evo2.entity.fighter import entZFighter


class HeroState(IntEnum):
    STAND = 0
    ATTACK = 1
    SPECIAL = 2
    SHEATHE = 3
    HURT = 4
    DEAD = 5


# Only valid when instantiated, on the screen that they live
class entZHero(entZFighter):
    """ent.z.Hero hashlink class."""

    _HERO_STATE_PTR = [0xB4, 0x4]  # ptr to HENUM, HeroState
    _DO_COLLIDE_PTR = [0xB8]  # bool
    _K_PTR = [0xBC]  # ptr to HOBJ
    _SPEED_REF_PTR = [0xC0]  # double
    _SHEATHE_TIME_PTR = [0xC8]  # double
    _RUN_FRAME_PTR = [0xD0]  # double
    _CURRENT_PUSH_PTR = [0xD8]  # ptr to HOBJ
    _PUSH_TIME_PTR = [0xE0]  # double
    _PT_PTR = [0xE8]  # ptr to HOBJ
    _PREV_FRAME_PTR = [0xF0]  # double
    _ON_BOAT_PTR = [0xF8]  # bool
    _ON_WING_PTR = [0xF9]  # bool
    _BOAT_TIME_PTR = [0x100]  # double
    _ALLOW_DEATH_STATE_PTR = [0x108]  # bool
    _ON_USE_POWER_PTR = [0x10C]  # ptr to HFUN
    _ANIM_PLAYED_PTR = [0x110]  # bool
    _ANIM_PLAYED_SPEED_PTR = [0x118]  # double
    _BOAT_PTR = [0x120]  # ptr to HOBJ
    _WAIT_ATTACK_END_PTR = [0x124]  # bool
    _HURT_LOCK_PTR = [0x125]  # bool
    _IN_CART_PTR = [0x126]  # bool
    _FLYING_PTR = [0x127]  # bool
    _ON_LIFT_PTR = [0x128]  # bool
    _ON_GROUND_PTR = [0x129]  # bool
    _LAST_PUSH_PTR = [0x130]  # double
    _PRESS_TIME_PTR = [0x138]  # double
    _LAST_POS_PTR = [0x140]  # ptr to HOBJ
    _STOP_MOVING_PTR = [0x144]  # bool

    @property
    def hero_state(self) -> HeroState:
        ptr = self.process.get_pointer(self.entity_ptr, offsets=self._HERO_STATE_PTR)
        hstate = self.process.read_u32(ptr)
        return HeroState(hstate)

    @property
    def in_control(self) -> bool:
        return not self.move_lock

    # TODO: Implement a bunch of stuff

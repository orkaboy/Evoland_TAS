# Libraries and Core Files
from engine.mathlib import Vec2
from memory.core import LocProcess
from memory.evo2.entity.kind import EKind
from memory.evo2.sprite import Sprite
from memory.zelda_base import GameEntity2D


# Only valid when instantiated, on the screen that they live
class entEntity(GameEntity2D):
    """ent.Entity hashlink class."""

    _HASHLINK_PTR = [0x0]  # ptr to hl_type
    _GAME_PTR = [0x4]  # ptr to HOBJ
    _EVENT_PTR = [0x8]  # ptr to HOBJ
    _MASS_PTR = [0x10]  # double
    _TMP_PTR = [0x18]  # ptr to HOBJ
    _COLLIDE_BOUNDS = [0x1C]  # ptr to HOBJ
    _HIT_BOUNDS = [0x20]  # ptr to HOBJ
    _KIND_PTR = [0x24, 0x4]  # ptr to HENUM EKind
    _CACHED_KIND_STR = [0x28]  # ptr to HOBJ
    _SPRITE_PTR = [0x2C]  # ptr to HOBJ
    _IS_COLLIDE_PTR = [0x30]  # bool
    _TARGET_ROTATION_PTR = [0x38]  # double
    _DO_RECAL_PTR = [0x40]  # bool
    _DO_SCRIPT_LOCK_PTR = [0x41]  # bool
    _DO_CAN_BE_FREEZE_PTR = [0x42]  # bool
    _DO_IS_3D_PTR = [0x43]  # bool
    _FXS_PTR = [0x44]  # ptr to HOBJ
    _CHECK_FULL_MOVE_PTR = [0x48]  # bool
    _REAL_DT_PTR = [0x50]  # double
    _CHANNELS_PTR = [0x58]  # ptr to HOBJ
    _IS_SHAKING_PTR = [0x5C]  # bool
    _PUSHING_BACK_PTR = [0x60]  # int

    def __init__(self, process: LocProcess, entity_ptr: int = 0) -> None:
        super().__init__(process, entity_ptr)
        sprite_ptr = self.process.get_pointer(self.entity_ptr, offsets=self._SPRITE_PTR)
        self.sprite = Sprite(process, sprite_ptr)

    @property
    def ch(self) -> str:
        return self.sprite.ch

    @property
    def kind(self) -> EKind:
        ptr = self.process.get_pointer(self.entity_ptr, offsets=self._KIND_PTR)
        kind = self.process.read_u32(ptr)
        return EKind(kind)

    @property
    def pos(self) -> Vec2:
        return self.sprite.pos

    @property
    def rotation(self) -> float:
        ptr = self.process.get_pointer(
            self.entity_ptr, offsets=self._TARGET_ROTATION_PTR
        )
        return self.process.read_double(ptr)

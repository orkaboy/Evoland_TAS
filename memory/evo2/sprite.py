# Libraries and Core Files
from engine.mathlib import Vec2
from memory.core import LocProcess
from memory.evo2.entity.kind import EKind


# Only valid when instantiated, on the screen that they live
class Sprite:
    """ent.Entity hashlink class."""

    _HASHLINK_PTR = [0x0]  # ptr to hl_type
    _KIND_PTR = [0x4, 0x4]  # ptr to HENUM EKind
    _GAME_PTR = [0x8]  # ptr to HOBJ
    _ANIM_PTR = [0x10]  # ptr to HOBJ
    _ANIM_FRAMES_PTR = [0x14]  # ptr to HOBJ
    _SIZE_PTR = [0x18]  # int
    _DUMMY_ANIM_TEXT_PTR = [0x1C]  # ptr to HOBJ
    _CURRENT_BOUNDS_2D_PTR = [0x20]  # ptr to HOBJ
    _FX_PTR = [0x24]  # ptr to HOBJ
    _SHADOW_STR = [0x28]  # ptr to HOBJ
    _SHADOW_Y_PTR = [0x2C]  # int
    _DEBUG_BOUNDS_COLOR_PTR = [0x30]  # int (rgb)
    _X_PTR = [0x38]  # double
    _Y_PTR = [0x40]  # double
    _Z_PTR = [0x48]  # double
    _DIR_PTR = [0x50]  # int
    _ROTATION_PTR = [0x58]  # double
    _ROTATION_2D_PTR = [0x60]  # double
    _GLOBAL_SPEED_PTR = [0x68]  # double
    _BLEND_MODE_PTR = [0x70, 0x4]  # ptr to HENUM, BlendMode
    _DEBUG_BOUNDS_PTR = [0x74]  # ptr to HOBJ
    _LEVEL_OVER_VALUE_PTR = [0x78]  # bool
    _EYES_PTR = [0x7C]  # ptr to HOBJ
    _FREEZE_FACTOR_PTR = [0x80]  # double

    def __init__(self, process: LocProcess, base_ptr: int = 0) -> None:
        self.process = process
        self.base_ptr = base_ptr

    @property
    def kind(self) -> EKind:
        ptr = self.process.get_pointer(self.base_ptr, offsets=self._KIND_PTR)
        kind = self.process.read_u32(ptr)
        return EKind(kind)

    # TODO: As dict?
    @property
    def ch(self) -> str:
        match self.kind:
            case EKind.HERO:
                return "@"
            case EKind.MOB:
                return "!"
            case EKind.PROJECTILE:
                return "*"
            # TODO: More EKinds
            case _:
                return "?"

    @property
    def pos(self) -> Vec2:
        x_ptr = self.process.get_pointer(self.base_ptr, offsets=self._X_PTR)
        y_ptr = self.process.get_pointer(self.base_ptr, offsets=self._Y_PTR)
        return Vec2(
            self.process.read_double(x_ptr),
            self.process.read_double(y_ptr),
        )

from engine.mathlib import Vec2
from memory.core import LocProcess


class ZephyrosPlayerMemory:
    _X_PTR = [0x8]  # double
    _Y_PTR = [0x10]  # double
    _POLAR_ANGLE_PTR = [0x20]  # double
    _POLAR_DIST_PTR = [0x28]  # double
    _MOVING_PTR = [0x38]  # int (0/1)
    _HP_PTR = [0x48]  # int (0-12/16)
    _ROTATION_PTR = [0x90]  # double (abs rotation of player in world space)

    def __init__(self, process: LocProcess, base_ptr: int) -> None:
        self.process = process
        self.base_ptr = base_ptr

        self.setup_pointers()

    def setup_pointers(self) -> None:
        self.x_ptr = self.process.get_pointer(self.base_ptr, offsets=self._X_PTR)
        self.y_ptr = self.process.get_pointer(self.base_ptr, offsets=self._Y_PTR)
        self.polar_angle_ptr = self.process.get_pointer(
            self.base_ptr, offsets=self._POLAR_ANGLE_PTR
        )
        self.polar_dist_ptr = self.process.get_pointer(
            self.base_ptr, offsets=self._POLAR_DIST_PTR
        )
        self.moving_ptr = self.process.get_pointer(
            self.base_ptr, offsets=self._MOVING_PTR
        )
        self.hp_ptr = self.process.get_pointer(self.base_ptr, offsets=self._HP_PTR)
        self.rotation_ptr = self.process.get_pointer(
            self.base_ptr, offsets=self._ROTATION_PTR
        )

    @property
    def pos(self) -> Vec2:
        return Vec2(
            self.process.read_double(self.x_ptr),
            self.process.read_double(self.y_ptr),
        )

    @property
    def rotation(self) -> float:
        return self.process.read_double(self.rotation_ptr)

    @property
    def hp(self) -> int:
        return self.process.read_u32(self.hp_ptr)

    @property
    def polar_angle(self) -> float:
        return self.process.read_double(self.polar_angle_ptr)

    @property
    def polar_dist(self) -> float:
        return self.process.read_double(self.polar_dist_ptr)

    @property
    def moving(self) -> bool:
        return self.process.read_u32(self.moving_ptr) == 1


class ZephyrosGolemMemory:
    _ROTATION_PTR = [0x20]  # double

    _HP_BP0_PTR = [0x48, 0x8, 0x10, 0x18]
    _HP_BP1_PTR = [0x48, 0x8, 0x14, 0x18]
    _HP_BP2_PTR = [0x48, 0x8, 0x18, 0x18]
    _HP_BP3_PTR = [0x48, 0x8, 0x1C, 0x18]

    def __init__(self, process: LocProcess, base_ptr: int, armless: bool) -> None:
        self.process = process
        self.base_ptr = base_ptr
        self.armless = armless

        self.rotation_ptr = self.process.get_pointer(
            self.base_ptr, offsets=self._ROTATION_PTR
        )
        if armless:
            self.hp_armor_ptr = self.process.get_pointer(
                self.base_ptr, offsets=self._HP_BP0_PTR
            )
            self.hp_core_ptr = self.process.get_pointer(
                self.base_ptr, offsets=self._HP_BP1_PTR
            )
        else:
            # NOTE: These will be invalid and overwritten with something else
            # after the golem phase ends. Don't use once all 3 hp bars are exhausted
            self.hp_left_arm_ptr = self.process.get_pointer(
                self.base_ptr, offsets=self._HP_BP0_PTR
            )
            self.hp_right_arm_ptr = self.process.get_pointer(
                self.base_ptr, offsets=self._HP_BP1_PTR
            )
            # NOTE: These are adjusted when the first phase ends, they are no longer valid
            self.hp_armor_ptr = self.process.get_pointer(
                self.base_ptr, offsets=self._HP_BP2_PTR
            )
            self.hp_core_ptr = self.process.get_pointer(
                self.base_ptr, offsets=self._HP_BP3_PTR
            )

    @property
    def rotation(self) -> float:
        return self.process.read_double(self.rotation_ptr)

    @property
    def hp_left_arm(self) -> int:
        return 0 if self.armless else self.process.read_u32(self.hp_left_arm_ptr)

    @property
    def hp_right_arm(self) -> int:
        return 0 if self.armless else self.process.read_u32(self.hp_right_arm_ptr)

    @property
    def hp_armor(self) -> int:
        return self.process.read_u32(self.hp_armor_ptr)

    @property
    def hp_core(self) -> int:
        return self.process.read_u32(self.hp_core_ptr)


class ZephyrosGanonMemory:
    _X_PTR = [0x30]
    _Y_PTR = [0x38]
    _Z_PTR = [0x40]

    _GANON_HP_PTR = [0x5C]

    def __init__(self, process: LocProcess, base_ptr: int) -> None:
        self.process = process
        self.base_ptr = base_ptr

        self.x_ptr = self.process.get_pointer(self.base_ptr, offsets=self._X_PTR)
        self.y_ptr = self.process.get_pointer(self.base_ptr, offsets=self._Y_PTR)
        self.z_ptr = self.process.get_pointer(self.base_ptr, offsets=self._Z_PTR)

        self.ganon_hp_ptr = self.process.get_pointer(
            self.base_ptr, offsets=self._GANON_HP_PTR
        )

    @property
    def pos(self) -> Vec2:
        return Vec2(
            self.process.read_double(self.x_ptr),
            self.process.read_double(self.y_ptr),
        )  # TODO: Z?

    @property
    def hp(self) -> int:
        return self.process.read_u32(self.ganon_hp_ptr)

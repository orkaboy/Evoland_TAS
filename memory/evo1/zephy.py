from engine.mathlib import Polar, Vec2
from memory.core import LocProcess


class ZephyrosPlayerMemory:
    """Tracks the player stats for the Zephyros fight."""

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
    def polar(self) -> Polar:
        """Return the position of the player in polar coordinates."""
        return Polar(
            r=self.process.read_double(self.polar_dist_ptr),
            theta=self.process.read_double(self.polar_angle_ptr),
        )

    @property
    def moving(self) -> bool:
        return self.process.read_u32(self.moving_ptr) == 1


class ZephyrosGolemBodypart:
    _X_PTR = [0x8, 0x18]  # double
    _Y_PTR = [0x8, 0x20]  # double
    _Z_PTR = [0x8, 0x28]  # double
    _HP_PTR = [0x18]

    def __init__(self, process: LocProcess, base_ptr: int) -> None:
        self.process = process
        self.base_ptr = base_ptr
        self.setup_pointers()

    def setup_pointers(self) -> None:
        self.x_ptr = self.process.get_pointer(self.base_ptr, offsets=self._X_PTR)
        self.y_ptr = self.process.get_pointer(self.base_ptr, offsets=self._Y_PTR)
        # self.z_ptr = self.process.get_pointer(self.base_ptr, offsets=self._Z_PTR)
        self.hp_ptr = self.process.get_pointer(self.base_ptr, offsets=self._HP_PTR)

    @property
    def pos(self) -> Vec2:
        return Vec2(
            self.process.read_double(self.x_ptr),
            self.process.read_double(self.y_ptr),
        )

    @property
    def hp(self) -> int:
        return self.process.read_u32(self.hp_ptr)


class ZephyrosGolemMemory:
    """Tracks the state of the Zephyros Golem fight."""

    _ROTATION_PTR = [0x20]  # double (polar rotation)

    _ANIM_TIMER_PTR = [
        0x30
    ]  # double (counts down, then resets, toggling between attack states)

    _FACING_PTR = [0xB8]  # double (rotation from golem perspective)

    _BP0_PTR = [0x48, 0x8, 0x10]
    _BP1_PTR = [0x48, 0x8, 0x14]
    _BP2_PTR = [0x48, 0x8, 0x18]
    _BP3_PTR = [0x48, 0x8, 0x1C]

    def __init__(self, process: LocProcess, base_ptr: int, armless: bool) -> None:
        self.process = process
        self.base_ptr = base_ptr
        self.armless = armless
        self.setup_pointers()

    def setup_pointers(self) -> None:
        self.anim_timer_ptr = self.process.get_pointer(
            self.base_ptr, offsets=self._ANIM_TIMER_PTR
        )
        self.rotation_ptr = self.process.get_pointer(
            self.base_ptr, offsets=self._ROTATION_PTR
        )
        self.facing_ptr = self.process.get_pointer(
            self.base_ptr, offsets=self._FACING_PTR
        )
        if self.armless:
            self.armor_ptr = self.process.get_pointer(
                self.base_ptr, offsets=self._BP0_PTR
            )
            self.core_ptr = self.process.get_pointer(
                self.base_ptr, offsets=self._BP1_PTR
            )
            self.left = None
            self.right = None
        else:
            # NOTE: These will be invalid and overwritten with something else
            # after the golem phase ends. Don't use once all 3 hp bars are exhausted
            self.left_arm_ptr = self.process.get_pointer(
                self.base_ptr, offsets=self._BP0_PTR
            )
            self.right_arm_ptr = self.process.get_pointer(
                self.base_ptr, offsets=self._BP1_PTR
            )
            self.left = ZephyrosGolemBodypart(self.process, self.left_arm_ptr)
            self.right = ZephyrosGolemBodypart(self.process, self.right_arm_ptr)
            # NOTE: These are adjusted when the first phase ends, they are no longer valid
            self.armor_ptr = self.process.get_pointer(
                self.base_ptr, offsets=self._BP2_PTR
            )
            self.core_ptr = self.process.get_pointer(
                self.base_ptr, offsets=self._BP3_PTR
            )
        self.armor = ZephyrosGolemBodypart(self.process, self.armor_ptr)
        self.core = ZephyrosGolemBodypart(self.process, self.core_ptr)

    @property
    def rotation(self) -> float:
        return self.process.read_double(self.rotation_ptr)

    @property
    def facing(self) -> float:
        return self.process.read_double(self.facing_ptr)

    @property
    def anim_timer(self) -> float:
        return self.process.read_double(self.anim_timer_ptr)


class ZephyrosProjectile:
    """Can describe either a blue or red projectile thrown by Ganon Zephyros."""

    _ID_PTR = [0x4]  # int
    _X_PTR = [0x8]  # double
    _Y_PTR = [0x10]  # double
    _Z_PTR = [0x18]  # double
    _BLUE_FLAG_PTR = [0x28]  # bool
    _ACTIVE_FLAG_PTR = [0x29]  # bool
    _COUNTERED_FLAG_PTR = [0x2A]  # bool

    def __init__(self, process: LocProcess, base_ptr: int) -> None:
        self.process = process
        self.base_ptr = base_ptr
        self.setup_pointers()

    def setup_pointers(self) -> None:
        self.id_ptr = self.process.get_pointer(self.base_ptr, offsets=self._ID_PTR)
        self.x_ptr = self.process.get_pointer(self.base_ptr, offsets=self._X_PTR)
        self.y_ptr = self.process.get_pointer(self.base_ptr, offsets=self._Y_PTR)
        self.z_ptr = self.process.get_pointer(self.base_ptr, offsets=self._Z_PTR)

        self.blue_flag_ptr = self.process.get_pointer(
            self.base_ptr, offsets=self._BLUE_FLAG_PTR
        )
        self.active_flag_ptr = self.process.get_pointer(
            self.base_ptr, offsets=self._ACTIVE_FLAG_PTR
        )
        self.countered_flag_ptr = self.process.get_pointer(
            self.base_ptr, offsets=self._COUNTERED_FLAG_PTR
        )

    @property
    def id(self) -> int:
        """Unique id for the projectile. Increments for each new created."""
        return self.process.read_u32(self.id_ptr)

    @property
    def pos(self) -> Vec2:
        """Position of the projectile in world space."""
        return Vec2(
            self.process.read_double(self.x_ptr),
            self.process.read_double(self.y_ptr),
        )

    @property
    def is_blue(self) -> bool:
        """True if the projectile is blue. False if red."""
        return self.process.read_u8(self.blue_flag_ptr) == 1

    @property
    def is_active(self) -> bool:
        """True if the projectile is active. Ignore if False."""
        return self.process.read_u8(self.active_flag_ptr) == 1

    @property
    def is_countered(self) -> bool:
        """True if we hit the blue projectile back."""
        return self.process.read_u8(self.countered_flag_ptr) == 1


class ZephyrosGanonMemory:
    """Tracks the state of the Zephyros Ganon fight, including projectiles fired."""

    _X_PTR = [0x30]
    _Y_PTR = [0x38]
    _Z_PTR = [0x40]

    _PROJECTILES_SIZE_PTR = [0x58, 0x4]
    _PROJECTILES_ARR_PTR = [0x58, 0x8]
    _PROJECTILES_OFFSET = 0x10
    _PROJECTILES_PTR_SIZE = 4
    _GANON_HP_PTR = [0x5C]
    _RED_ATTACKS_CNT_PTR = [0x60]

    def __init__(self, process: LocProcess, base_ptr: int) -> None:
        self.process = process
        self.base_ptr = base_ptr

        self.x_ptr = self.process.get_pointer(self.base_ptr, offsets=self._X_PTR)
        self.y_ptr = self.process.get_pointer(self.base_ptr, offsets=self._Y_PTR)
        self.z_ptr = self.process.get_pointer(self.base_ptr, offsets=self._Z_PTR)

        self.ganon_hp_ptr = self.process.get_pointer(
            self.base_ptr, offsets=self._GANON_HP_PTR
        )
        self.red_cnt_ptr = self.process.get_pointer(
            self.base_ptr, offsets=self._RED_ATTACKS_CNT_PTR
        )
        self._init_projectiles()

    def _init_projectiles(self):
        self.projectiles: list[ZephyrosProjectile] = []
        proj_size_ptr = self.process.get_pointer(
            self.base_ptr, self._PROJECTILES_SIZE_PTR
        )
        proj_arr_size = self.process.read_u32(proj_size_ptr)
        proj_arr_offset = self.process.get_pointer(
            self.base_ptr, self._PROJECTILES_ARR_PTR
        )
        for i in range(proj_arr_size):
            proj_offset = self._PROJECTILES_OFFSET + i * self._PROJECTILES_PTR_SIZE
            proj_ptr = self.process.get_pointer(proj_arr_offset, offsets=[proj_offset])
            self.projectiles.append(ZephyrosProjectile(self.process, proj_ptr))

    @property
    def pos(self) -> Vec2:
        """(x, y) position of the boss in the boss room."""
        return Vec2(
            self.process.read_double(self.x_ptr),
            self.process.read_double(self.y_ptr),
        )  # TODO: Z?

    @property
    def hp(self) -> int:
        """Number of hits the boss can take."""
        return self.process.read_u32(self.ganon_hp_ptr)

    @property
    def red_counter(self) -> int:
        """Number of red attacks since last blue orb."""
        return self.process.read_u32(self.red_cnt_ptr)

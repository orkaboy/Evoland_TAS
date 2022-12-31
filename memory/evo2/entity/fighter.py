from memory.evo2.entity.base import entEntity


# Only valid when instantiated, on the screen that they live
class entFighterBase(entEntity):
    """ent.FighterBase hashlink class."""

    _LIFE_PTR = [0x64]  # int
    _FORCE_AGGRO_PTR = [0x68]  # bool
    _ID_PTR = [0x6C]  # ptr to HOBJ
    _W_PTR = [0x70]  # ptr to HOBJ
    _IS_BLINKING_PTR = [0x74]  # bool (iframes)
    _FID_PTR = [0x78]  # int
    _WKIND_PTR = [0x7C, 0x4]  # ptr to HENUM, WKind
    _COMBO_PTR = [0x80]  # bool
    _ON_DIE_EVENT_PTR = [0x84]  # ptr to HFUN

    def __eq__(self, other: object) -> bool:
        try:
            # TODO: Doesn't seem to work entirely
            return self.fid == other.fid
        except ReferenceError:
            return False

    @property
    def life(self) -> int:
        ptr = self.process.get_pointer(self.entity_ptr, offsets=self._LIFE_PTR)
        return self.process.read_u32(ptr)

    @property
    def is_alive(self) -> bool:
        try:
            return self.life > 0
        except ReferenceError:
            return False

    @property
    def fid(self) -> int:
        ptr = self.process.get_pointer(self.entity_ptr, offsets=self._FID_PTR)
        return self.process.read_u32(ptr)

    @property
    def force_aggro(self) -> bool:
        ptr = self.process.get_pointer(self.entity_ptr, offsets=self._FORCE_AGGRO_PTR)
        return self.process.read_u8(ptr) == 1

    @property
    def iframe(self) -> bool:
        ptr = self.process.get_pointer(self.entity_ptr, offsets=self._IS_BLINKING_PTR)
        return self.process.read_u8(ptr) == 1

    @property
    def combo(self) -> bool:
        ptr = self.process.get_pointer(self.entity_ptr, offsets=self._COMBO_PTR)
        return self.process.read_u8(ptr) == 1

    # TODO: Implement properties


# Only valid when instantiated, on the screen that they live
class entZFighter(entFighterBase):
    """ent.z.Fighter hashlink class."""

    _ATTACK_DELAY_PTR = [0x88]  # double
    _MOVE_LOCK_PTR = [0x90]  # bool, in_control
    _SPEED_PTR = [0x98]  # double
    _ROTATION_VAR_PTR = [0xA0]  # double
    _ROTATION_SPEED_PTR = [0xA8]  # double
    _WEAPONS_PTR = [0xB0]  # ptr to HOBJ

    @property
    def attack_delay(self) -> float:
        ptr = self.process.get_pointer(self.entity_ptr, offsets=self._ATTACK_DELAY_PTR)
        return self.process.read_double(ptr)

    @property
    def move_lock(self) -> bool:
        ptr = self.process.get_pointer(self.entity_ptr, offsets=self._MOVE_LOCK_PTR)
        return self.process.read_u8(ptr) == 1

    @property
    def speed(self) -> float:
        ptr = self.process.get_pointer(self.entity_ptr, offsets=self._SPEED_PTR)
        return self.process.read_double(ptr)

    @property
    def rotation_var(self) -> float:
        ptr = self.process.get_pointer(self.entity_ptr, offsets=self._ROTATION_VAR_PTR)
        return self.process.read_double(ptr)

    @property
    def rotation_speed(self) -> float:
        ptr = self.process.get_pointer(
            self.entity_ptr, offsets=self._ROTATION_SPEED_PTR
        )
        return self.process.read_double(ptr)

    # TODO: WEAPONS

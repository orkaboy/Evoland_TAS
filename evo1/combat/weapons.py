from typing import Optional

from control import evo_ctrl
from engine.seq import SeqBase
from memory.evo1 import Evo1Weapon, get_memory


class SeqSwapWeapon(SeqBase):
    def __init__(self, name: str, new_weapon: Evo1Weapon):
        self.new_weapon = new_weapon
        self.cur_selection: Optional[Evo1Weapon] = None
        self.menu_open = False
        super().__init__(name)

    def reset(self):
        self.cur_selection = None
        self.menu_open = False

    def execute(self, delta: float) -> bool:
        if self.cur_selection is None:
            self.cur_selection = get_memory().cur_weapon

        ctrl = evo_ctrl()
        ctrl.dpad.none()
        if not self.menu_open:
            # 1. Open menu
            ctrl.menu(tapping=True)
            self.menu_open = True
        elif self.cur_selection == self.new_weapon:
            ctrl.menu(tapping=True)
            # 3. Close menu
            return True
        else:
            # 2. Move cursor to target weapon
            match self.cur_selection:
                case Evo1Weapon.SWORD:
                    if self.new_weapon != self.cur_selection:
                        self.cur_selection = Evo1Weapon.BOMB
                        ctrl.dpad.tap_right()
                case Evo1Weapon.BOMB:
                    match self.new_weapon:
                        case Evo1Weapon.SWORD:
                            self.cur_selection = Evo1Weapon.SWORD
                            ctrl.dpad.tap_left()
                        case Evo1Weapon.BOW:
                            self.cur_selection = Evo1Weapon.BOW
                            ctrl.dpad.tap_right()
                case Evo1Weapon.BOW:
                    if self.new_weapon != self.cur_selection:
                        self.cur_selection = Evo1Weapon.BOMB
                        ctrl.dpad.tap_left()
        return False

    def __repr__(self) -> str:
        return f"Swap to weapon: {self.new_weapon.name}"

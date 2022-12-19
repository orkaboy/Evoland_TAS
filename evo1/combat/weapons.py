from enum import Enum

from control import evo_ctrl
from engine.seq import SeqBase


class Evo1Weapon(Enum):
    SWORD = 0
    BOMB = 1
    BOW = 2


class SeqSwapWeapon(SeqBase):
    def __init__(self, name: str, cur_weapon: Evo1Weapon, next_weapon: Evo1Weapon):
        self.cur_weapon = cur_weapon
        self.next_weapon = next_weapon
        self.cur_selection = cur_weapon
        self.menu_open = False
        super().__init__(name)

    def reset(self):
        self.cur_selection = self.cur_weapon
        self.menu_open = False

    def execute(self, delta: float) -> bool:
        ctrl = evo_ctrl()
        ctrl.dpad.none()
        if not self.menu_open:
            # 1. Open menu
            ctrl.menu(tapping=True)
            self.menu_open = True
        elif self.cur_selection == self.next_weapon:
            ctrl.menu(tapping=True)
            # 3. Close menu
            return True
        else:
            # 2. Move cursor to target weapon
            match self.cur_selection:
                case Evo1Weapon.SWORD:
                    if self.next_weapon != self.cur_selection:
                        self.cur_selection = Evo1Weapon.BOMB
                        ctrl.dpad.tap_right()
                case Evo1Weapon.BOMB:
                    match self.next_weapon:
                        case Evo1Weapon.SWORD:
                            self.cur_selection = Evo1Weapon.SWORD
                            ctrl.dpad.tap_left()
                        case Evo1Weapon.BOW:
                            self.cur_selection = Evo1Weapon.BOW
                            ctrl.dpad.tap_right()
                case Evo1Weapon.BOW:
                    if self.next_weapon != self.cur_selection:
                        self.cur_selection = Evo1Weapon.BOMB
                        ctrl.dpad.tap_left()
        return False

    def __repr__(self) -> str:
        return f"Swap to weapon: {self.next_weapon.name}"

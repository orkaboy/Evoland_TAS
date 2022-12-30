import contextlib
from typing import Optional

from control import evo_ctrl
from engine.mathlib import Vec2, get_box_with_size, is_close
from engine.move2d import SeqSection2D, move_to
from engine.seq import SeqBase
from memory.evo1 import EKind, Evo1Weapon, get_memory, get_zelda_memory


class SeqPlaceBomb(SeqSection2D):
    """Place a bomb at target. Assumes that bomb is the currently selected weapon."""

    def __init__(
        self,
        name: str,
        target: Vec2,
        use_menu_glitch: bool = False,
        swap_to_sword: bool = False,
        precision: float = 0.2,
    ):
        super().__init__(name)
        # If menu glitch is used, stay in place with menu open, waiting form bomb to blow
        self.use_menu_glitch = use_menu_glitch
        self.swap_to_sword = swap_to_sword
        self.precision = precision
        self.target = target
        self.bombed = False

    def reset(self) -> None:
        self.bombed = False
        return super().reset()

    def execute(self, delta: float) -> bool:
        ctrl = evo_ctrl()
        mem = get_zelda_memory()
        player_pos = mem.player.pos
        # Move to target area
        if self.bombed is False:
            move_to(player=player_pos, target=self.target, precision=self.precision)
            if not is_close(player_pos, self.target, precision=self.precision):
                return False
            self.bombed = True
            ctrl.attack()
            if self.use_menu_glitch:
                ctrl.dpad.none()
                ctrl.menu()
                return False
        elif self.use_menu_glitch:
            if self.swap_to_sword:
                ctrl.dpad.left()
            with contextlib.suppress(ReferenceError):
                box = get_box_with_size(center=player_pos, half_size=2 * self.precision)
                # Wait for bomb to explode
                for actor in mem.actors:
                    if actor.kind == EKind.INTERACT and box.contains(actor.pos):
                        return False
            # Close menu
            ctrl.dpad.none()
            ctrl.menu()
            return True
        # If we're not using menu glitch and bomb is placed; done
        return True

    def __repr__(self) -> str:
        glitch = ", using menu glitch" if self.use_menu_glitch else ""
        return f"Bombing ({self.name}) at {self.target}{glitch}"


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
            # Check if we don't need to do anything
            if self.cur_selection == self.new_weapon:
                return True

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

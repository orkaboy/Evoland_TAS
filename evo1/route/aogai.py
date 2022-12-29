import logging

from control import evo_ctrl
from engine.mathlib import Facing, Vec2
from engine.move2d import SeqGrabChest, SeqMove2D, SeqMove2DCancel, SeqSection2D
from engine.seq import SeqBase, SeqInteract, SeqList, wait_seconds
from evo1.move2d import SeqZoneTransition
from maps.evo1 import GetNavmap
from memory.evo1 import MapID, get_memory

logger = logging.getLogger(__name__)

_aogai_nav = GetNavmap(MapID.AOGAI)

_SOUTH_ENTRANCE = _aogai_nav.map[0]  # Exit is down
_NORTH_ENTRANCE = _aogai_nav.map[18]  # Exit is up
_SID = _aogai_nav.map[6]  # Sid is left
_HEALER = _aogai_nav.map[16]  # Healer is right
_CARD_CHEST = _aogai_nav.map[10]  # Chest is up
_SHOP_CHEST = _aogai_nav.map[13]  # Chest is left
_GRANNY = _aogai_nav.map[5]  # Note, adjacent point to Granny map
_DEPUTY = _aogai_nav.map[21]  # Deputy is left
_MOM = _aogai_nav.map[7]  # Mom is up
_CARD_PLAYER = _aogai_nav.map[22]  # Player is left
_SHOP_KEEPER = _aogai_nav.map[19]  # Shop is up
_KID_CHEST = _aogai_nav.map[23]  # Chest is up


class AogaiWrongWarp(SeqBase):
    """When on the world map, to the north of Aogai, wrong warp to south entrance. This requires precise joystick input."""

    def __init__(self, name: str):
        super().__init__(name)

    def execute(self, delta: float) -> bool:
        ctrl = evo_ctrl()
        ctrl.dpad.none()
        ctrl.set_joystick(Vec2(-1, -0.1))

        mem = get_memory()
        if mem.map_id == MapID.AOGAI:
            ctrl.set_neutral()
            logger.info(f"Transitioned to zone: {MapID.AOGAI.name}")
            return True
        return False

    def __repr__(self) -> str:
        return f"Transition to {self.name}, using wrong-warp"


class TalkToGranny(SeqBase):
    """Requires some special movement, since this zone has rotated controls."""

    def __init__(self):
        super().__init__(name="Granny")

    def execute(self, delta: float) -> bool:
        ctrl = evo_ctrl()
        # Go from [8.8, 6.6] into Granny area (hold right)
        ctrl.dpad.none()
        ctrl.dpad.right()
        # Wait for screen transition
        wait_seconds(0.5)
        # Approach Granny (hold up)
        ctrl.dpad.none()
        ctrl.dpad.up()
        player = self.zelda_mem().player
        # Wait until x < 3.5
        while player.pos.x > 3.5:
            wait_seconds(0.1)
        ctrl.dpad.none()
        # Talk to Granny (bomb skip?)
        ctrl.confirm()
        # Go away from Granny
        ctrl.dpad.down()
        # Detect when we return to regular control area
        while player.pos.x < 7:
            wait_seconds(0.1)
        ctrl.dpad.none()
        return True


class TriggerCardGlitch(SeqBase):
    def __init__(self):
        super().__init__(name="Card glitch")

    def execute(self, delta: float) -> bool:
        ctrl = evo_ctrl()
        ctrl.dpad.none()
        # Turn
        ctrl.dpad.left()
        wait_seconds(0.4)
        ctrl.dpad.none()
        # Talk
        ctrl.confirm(tapping=True)
        # Tap past first text
        ctrl.confirm(tapping=True)
        # Select "Yes" to trigger glitch
        ctrl.confirm(tapping=False)
        # Move on
        return True


class HealerGlitch(SeqBase):
    def __init__(self):
        super().__init__(name="Healer glitch")

    def execute(self, delta: float) -> bool:
        ctrl = evo_ctrl()
        ctrl.confirm(tapping=False)
        return True


class Aogai1(SeqList):
    """First time in Aogai. Talk to Sid and get the bombs, then leave for Sacred Grove."""

    def __init__(self):
        super().__init__(
            name="Aogai Village",
            children=[
                # TODO: Handle menu glitch logic (optional?)
                SeqMove2DCancel(
                    "Move to Sid",
                    coords=_aogai_nav.calculate(start=_SOUTH_ENTRANCE, goal=_SID),
                    invert=True,
                ),
                SeqInteract("Sid"),
                SeqMove2D(
                    "Move to Card player",
                    coords=_aogai_nav.calculate(start=_SID, goal=_CARD_CHEST),
                    invert=True,
                ),
                SeqGrabChest("Card players", direction=Facing.UP),
                SeqMove2D("Card player", coords=[Vec2(-8.5, -6)], invert=True),
                # Talk to top card player
                SeqInteract("Card player"),
                SeqMove2D("Card player", coords=[_CARD_PLAYER], invert=True),
                TriggerCardGlitch(),
                # Some wonky movement getting the chest, not quite correct coordinates
                SeqMove2D(
                    "Move to chest",
                    coords=_aogai_nav.calculate(
                        start=_CARD_CHEST, goal=_SHOP_CHEST, final_pos=Vec2(-9.5, -3)
                    ),
                    invert=True,
                ),
                # SeqGrabChest("Shop keeper", direction=Facing.LEFT),
                SeqMove2D(
                    "Move to Healer",
                    coords=_aogai_nav.calculate(start=_SHOP_CHEST, goal=_HEALER),
                    invert=True,
                ),
                HealerGlitch(),
                SeqMove2D(
                    "Move to Exit",
                    coords=_aogai_nav.calculate(start=_HEALER, goal=_NORTH_ENTRANCE),
                    invert=True,
                ),
                SeqZoneTransition(
                    "Overworld", direction=Facing.UP, target_zone=MapID.OVERWORLD
                ),
                SeqMove2D(  # Adjusting to be slightly faster
                    "Adjust position",
                    coords=[Vec2(95, 91.4)],
                ),
                AogaiWrongWarp("Aogai"),
                SeqMove2D(
                    "Move to Granny",
                    coords=_aogai_nav.calculate(start=_SOUTH_ENTRANCE, goal=_GRANNY),
                    invert=True,
                ),
                # Get bombs by talking to everyone
                TalkToGranny(),
                SeqMove2D(
                    "Move to Deputy",
                    coords=_aogai_nav.calculate(start=_GRANNY, goal=_DEPUTY),
                    invert=True,
                ),  # TODO: Bomb glitch
                SeqInteract("Deputy"),
                SeqMove2D(
                    "Move to Mom",
                    coords=_aogai_nav.calculate(start=_DEPUTY, goal=_MOM),
                    invert=True,
                ),  # TODO: Bomb glitch
                SeqInteract("Mom"),
                SeqMove2D(
                    "Move to kid",
                    coords=_aogai_nav.calculate(start=_MOM, goal=_KID_CHEST),
                    invert=True,
                ),
                # TODO: Get bombs (get chest, talk to kid)
                # TODO: Bomb skip
                SeqMove2D(
                    "Move to exit",
                    coords=_aogai_nav.calculate(start=_KID_CHEST, goal=_SOUTH_ENTRANCE),
                    invert=True,
                ),
                SeqZoneTransition(
                    "Overworld", direction=Facing.DOWN, target_zone=MapID.OVERWORLD
                ),
            ],
        )


class Aogai2(SeqList):
    """Back in Aogai village, preparing for Sarudnahk. Leave to the north."""

    def __init__(self):
        super().__init__(
            name="Aogai Village",
            children=[
                # Get heal bug (card player, healer)
                # TODO: Consistently fails
                SeqMove2D(
                    "Move to card player",
                    coords=_aogai_nav.calculate(
                        start=_SOUTH_ENTRANCE, goal=_CARD_PLAYER
                    ),
                    invert=True,
                ),
                TriggerCardGlitch(),
                SeqMove2D(
                    "Move to healer",
                    coords=_aogai_nav.calculate(start=_CARD_PLAYER, goal=_HEALER),
                    invert=True,
                ),
                HealerGlitch(),
                SeqMove2D(
                    "Move to exit",
                    coords=_aogai_nav.calculate(start=_HEALER, goal=_NORTH_ENTRANCE),
                    invert=True,
                ),
                # Exit north
                SeqZoneTransition(
                    "Overworld", direction=Facing.UP, target_zone=MapID.OVERWORLD
                ),
            ],
        )


class AogaiPotionShopping(SeqSection2D):
    def __init__(self, amount: int):
        super().__init__(name="Buying potions")
        self.amount = amount
        self.pots = 0

    def reset(self) -> None:
        self.pots = 0

    _SHOP_KEEPER_POS = Vec2(-11, -3)

    def execute(self, delta: float) -> bool:
        ret = self.turn_towards_pos(self._SHOP_KEEPER_POS, invert=True)
        if ret is False:
            return False

        mem = get_memory()
        self.pots = mem.nr_potions
        if self.pots < self.amount:
            ctrl = evo_ctrl()
            # Approach vendor
            ctrl.confirm(tapping=True)
            # Select buy
            ctrl.confirm(tapping=True)
            # Buy the potion
            ctrl.confirm(tapping=True)
            # Cancel out of confirmation dialog
            ctrl.confirm(tapping=True)
            return False
        return True

    def __repr__(self) -> str:
        return f"{self.name}: {self.pots}/{self.amount}"


class Aogai3(SeqList):
    """Back in Aogai village (from town portal). Buy pots and leave to the north for Black Citadel."""

    def __init__(self):
        super().__init__(
            name="Aogai Village",
            children=[
                # Teleport into town square
                SeqMove2D(
                    "Move to shop keeper",
                    coords=[_SHOP_KEEPER],
                    invert=True,
                ),
                AogaiPotionShopping(amount=5),  # TODO: is 5 enough?
                # Get heal bug (card player, healer)
                SeqMove2D(
                    "Move to card player",
                    coords=[_CARD_PLAYER],
                    invert=True,
                ),
                # TODO: Glitchy, sometimes doesn't exit the menu
                TriggerCardGlitch(),
                SeqMove2D(
                    "Move to exit",
                    coords=_aogai_nav.calculate(
                        start=_CARD_PLAYER, goal=_NORTH_ENTRANCE
                    ),
                    invert=True,
                ),
                # Exit north
                SeqZoneTransition(
                    "Overworld", direction=Facing.UP, target_zone=MapID.OVERWORLD
                ),
            ],
        )


class Aogai4(SeqList):
    """Final Aogai section. Get the airship and leave to the south."""

    def __init__(self):
        super().__init__(
            name="Aogai Village",
            children=[
                SeqMove2D(
                    "Move to square",
                    coords=_aogai_nav.calculate(start=_SOUTH_ENTRANCE, goal=_SID),
                    invert=True,
                ),
                # TODO: Trigger conversation to get airship
                # TODO: Need to leave the menu if holding menu skip
                SeqMove2D(
                    "Move to exit",
                    coords=_aogai_nav.calculate(start=_SID, goal=_SOUTH_ENTRANCE),
                    invert=True,
                ),
                # Exit south
                SeqZoneTransition(
                    "Overworld", direction=Facing.DOWN, target_zone=MapID.OVERWORLD
                ),
            ],
        )

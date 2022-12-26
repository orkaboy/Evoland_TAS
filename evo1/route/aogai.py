import logging

from control import evo_ctrl
from engine.mathlib import Facing, Vec2
from engine.move2d import SeqGrabChest, SeqMove2DCancel
from engine.seq import SeqBase, SeqInteract, SeqList
from evo1.move2d import SeqZoneTransition
from maps.evo1 import GetNavmap
from memory.evo1 import MapID, get_memory

logger = logging.getLogger(__name__)

_aogai_nav = GetNavmap(MapID.AOGAI)

_SOUTH_ENTRANCE = _aogai_nav.map[0]
_NORTH_ENTRANCE = _aogai_nav.map[18]
_SID = _aogai_nav.map[6]
_HEALER = _aogai_nav.map[16]
_CARD_CHEST = _aogai_nav.map[10]
_SHOP_CHEST = _aogai_nav.map[13]
_GRANNY = _aogai_nav.map[5]  # Note, not on Granny map
_DEPUTY = _aogai_nav.map[1]  # TODO
_MOM = _aogai_nav.map[6]  # TODO


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
        # TODO: Implement:
        # Go from [5] into Granny area
        # Approach Granny (rotated controls)
        # Talk to Granny (bomb skip?)
        # Go away from Granny
        # Detect when we return to regular control area
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
                SeqMove2DCancel(
                    "Move to Card player",
                    coords=_aogai_nav.calculate(start=_SID, goal=_CARD_CHEST),
                    invert=True,
                ),
                SeqGrabChest("Card players", direction=Facing.UP),
                SeqMove2DCancel("Card player", coords=[Vec2(-8.5, -6)], invert=True),
                # TODO: Talk to top card player
                SeqInteract("Card player"),
                # TODO: Get the text glitch from card player in Aogai
                SeqMove2DCancel(
                    "Move to chest",
                    coords=_aogai_nav.calculate(start=_CARD_CHEST, goal=_SHOP_CHEST),
                    invert=True,
                ),
                # TODO: Some wonky movement getting the chest, not quite correct coordinates
                SeqGrabChest("Shop keeper", direction=Facing.LEFT),
                SeqMove2DCancel(
                    "Move to Healer",
                    coords=_aogai_nav.calculate(start=_SHOP_CHEST, goal=_HEALER),
                    invert=True,
                ),
                SeqInteract("Healer"),
                SeqMove2DCancel(
                    "Move to Exit",
                    coords=_aogai_nav.calculate(start=_HEALER, goal=_NORTH_ENTRANCE),
                    invert=True,
                ),
                SeqZoneTransition(
                    "Overworld", direction=Facing.UP, target_zone=MapID.OVERWORLD
                ),
                AogaiWrongWarp("Aogai"),  # TODO: Could be slightly faster
                SeqMove2DCancel(
                    "Move to Granny",
                    coords=_aogai_nav.calculate(start=_SOUTH_ENTRANCE, goal=_GRANNY),
                    invert=True,
                ),
                # TODO: Get bombs by talking to everyone
                TalkToGranny(),
                SeqMove2DCancel(
                    "Move to Deputy",
                    coords=_aogai_nav.calculate(start=_GRANNY, goal=_DEPUTY),
                    invert=True,
                ),  # TODO: Approach deputy (coords)
                SeqMove2DCancel(
                    "Move to Mom",
                    coords=_aogai_nav.calculate(start=_DEPUTY, goal=_MOM),
                    invert=True,
                ),  # TODO: Approach mom (coords)
                # TODO: Bomb skip
                SeqMove2DCancel(
                    "Move to exit",
                    coords=_aogai_nav.calculate(start=_MOM, goal=_SOUTH_ENTRANCE),
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
                # TODO: Get heal bug (card player, healer)
                # TODO: Exit north
            ],
        )


class Aogai3(SeqList):
    """Back in Aogai village (from town portal). Buy pots and leave to the north for Black Citadel."""

    def __init__(self):
        super().__init__(
            name="Aogai Village",
            children=[
                # Teleport into town square
                # TODO: Buy potions
                # TODO: Get heal bug (card player)
                # TODO: Exit north
            ],
        )


class Aogai4(SeqList):
    """Final Aogai section. Get the airship and leave to the south."""

    def __init__(self):
        super().__init__(
            name="Aogai Village",
            children=[
                # TODO: Trigger conversation to get airship
                # TODO: Exit south
            ],
        )

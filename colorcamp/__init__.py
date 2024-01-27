"""ColorCamp

ColorCamp consists of several submodules designed to add additional context and make working with colors and collections of colors easier.

"""

from .color import BaseColor, Hex, RGB, HSL
from .palette import Palette
from .scale import Scale
from .map import Map
from .camp import Camp

from ._settings import settings

__all__ = [
    "BaseColor",
    "Hex",
    "RGB",
    "HSL",
    "Palette",
    "Map",
    "Scale",
    "Camp",
    "settings",
]

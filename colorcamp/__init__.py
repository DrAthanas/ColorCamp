"""ColorCamp

ColorCamp consists of several submodules designed to add additional context and make working with colors and collections of colors easier.

"""

from .color_objects.color_space import Hex, RGB, HSL
from .color_objects import Palette, Scale, Map
from ._camp import Camp

from ._settings import settings

__all__ = [
    "Hex",
    "RGB",
    "HSL",
    "Palette",
    "Map",
    "Scale",
    "Camp",
    "settings",
]

"""ColorCamp

ColorCamp consists of several submodules designed to add additional context and make working with colors and collections of colors easier.

"""

from .color_objects.color import Hex, RGB, HSL
from .color_objects.palette import Palette
from .color_objects.scale import Scale
from .color_objects.map import Map
from .camp import Camp

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

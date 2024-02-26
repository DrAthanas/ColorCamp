"""ColorCamp

ColorCamp consists of several submodules designed to add additional context and make working with colors and collections of colors easier.

"""

from ._camp import Camp
from ._report import report
from ._settings import settings
from .color_space import HSL, RGB, Hex
from .groups import Map, Palette, Scale

__all__ = ["Hex", "RGB", "HSL", "Palette", "Map", "Scale", "Camp", "settings", "report"]

"""ColorCamp

ColorCamp consists of several submodules designed to add additional context and make working with colors and collections of colors easier.

"""

from .color import WebColor, Hex, RGB, HSL
from .palette import Palette
from .scale import Scale
from .camp import Camp

from ._settings import Settings

settings = Settings()


__all__ = [
    'WebColor',
    'Hex',
    'RGB',
    'HSL',
    'Palette',
    'Scale',
    'Camp',
    'settings',
]
""" Conversions between different color formats e.g.:
    * hex -> rgb
    * rgb -> hex
    * rgb -> hsl
    * hsl -> rgb
"""

import colorsys

from ._settings import settings
from .common.types import AnyGenericColorTuple, AnyRGBColorTuple
from .common.validators import HexStringValidator

__all__ = [
    "hex_to_rgb",
    "rgb_to_hex",
    "rgb_to_hsl",
]


def hex_to_rgb(hex_str: str) -> AnyRGBColorTuple:
    """Convert hex strings into rgb tuples.

    Parameters
    ----------
    hex : str
        Standard web color hex string, optionally starting with '#'

    Returns
    -------
    AnyRGBColorTuple
        Red, Green, Blue, [and alpha] channels
    """

    HexStringValidator().validate(hex_str)

    hex_str = hex_str.lstrip("#")
    len_hex = len(hex_str)
    if len_hex > 4:
        # 256 color space
        rgb = [int(hex_str[i : i + 2], 16) for i in range(0, len(hex_str), 2)]
    else:
        rgb = [int(i + i, 16) for i in hex_str]
    if len(rgb) == 4:
        rgb[3] = rgb[3] / 255  # type: ignore

    return tuple(rgb)  # type: ignore


def rgb_to_hex(rgb: AnyRGBColorTuple) -> str:
    """Convert rgb tuples into hex strings

    Parameters
    ----------
    rgb : AnyRGBColorTuple
        Red, Green, Blue, [and alpha] channels

    Returns
    -------
    str
        Hex string representation of 256rgb color
    """

    hex_str = "#{:02X}{:02X}{:02X}".format(*rgb[:3])  # pylint: disable=C0209
    if len(rgb) == 4:
        hex_str += f"{int(rgb[3]*255):02X}"  # type: ignore
    return hex_str


def rgb_to_hsl(rgb: AnyGenericColorTuple) -> AnyGenericColorTuple:
    """Convert rgb tuples into hsl tuples

    Parameters
    ----------
    rgb : AnyRGBColorTuple
        Red, Green, Blue, [and alpha] channels

    Returns
    -------
    tuple
        HSL tuple
    """

    hue, lightness, saturation = colorsys.rgb_to_hls(*rgb[:3])
    ## remove floating point errors
    hue = round(hue * 360, settings.max_precision)
    lightness = round(lightness, settings.max_precision)
    saturation = round(saturation, settings.max_precision)

    if len(rgb) == 4:
        return (hue, saturation, lightness, rgb[3])

    return (hue, saturation, lightness)

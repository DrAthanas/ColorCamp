""" Conversions between different color formats e.g.:
    * hex -> rgb
    * rgb -> hex
"""
# Imports
from .common.types import AnyRGBColorTuple, RGBColorTuple
from .common.validators import HexStringValidator

def hex_to_rgb(hex: str) -> RGBColorTuple:
    """Convert hex strings into rgb tuples.

    Parameters
    ----------
    hex : str
        Standard web color hex string, optionally starting with '#'

    Returns
    -------
    RGBColorTuple
        Red, Green, Blue, [and alpha] channels
    """
    HexStringValidator().validate(hex)

    hex = hex.lstrip("#")
    len_hex = len(hex)
    if len_hex > 4:
        # 256 color space
        rgb = [int(hex[i : i + 2], 16) for i in range(0, len(hex), 2)]
    else:
        rgb = [int(i + i, 16) for i in hex]
    if len(rgb) == 4:
        rgb[3] = rgb[3] / 255
        
    return tuple(rgb)


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
    hex = "#{:02X}{:02X}{:02X}".format(*rgb[:3])
    if len(rgb) == 4:
        hex += f"{int(rgb[3]*255):02X}"
    return hex


# def rgb_to_cmyk(rgb: AnyRGBColorTuple) -> tuple:
#     # TODO: Alpha?!
#     red, green, blue = [channel / 255 for channel in rgb[:3]]

#     key = 1 - max(red, green, blue)
#     if key == 1:
#         cyan, magenta, yellow = 0, 0, 0
#     else:
#         cyan = (1 - red - key) / (1 - key)
#         magenta = (1 - green - key) / (1 - key)
#         yellow = (1 - blue - key) / (1 - key)

#     return cyan, magenta, yellow, key

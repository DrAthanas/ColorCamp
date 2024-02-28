"""Hex Color Space"""

from __future__ import annotations

from typing import Any, Dict, Optional

from colorcamp.common.types import Numeric
from colorcamp.common.validators import HexStringValidator, RGB256IntervalValidator
from colorcamp.conversions import hex_to_rgb, rgb_to_hex

from ._base_color import BaseColor

__all__ = ["Hex"]


# NOTE: Alternative is 'from collections import UserString'
# # but then string methods return a Hex object, which I don't want
class Hex(BaseColor, str):
    """Extended str class that represents RGB colors in hexadecimal format"""

    __slots__ = ("_hex", "_alpha", "_name", "_description", "_metadata")

    @staticmethod
    def __adjust_alpha(hex_str: str, alpha):
        if alpha is not None:
            if len(hex_str) > 6:
                hex_str = hex_str[:7] + f"{int(alpha*255):X}"
            else:
                hex_str = hex_str[:4] + f"{int(alpha*15):X}"

        return hex_str

    # pylint: disable=W0613
    def __new__(cls, hex_str, *args, alpha=None, **kwargs):
        hex_str = cls.__adjust_alpha(hex_str, alpha)

        return super().__new__(cls, hex_str)

    # pylint: enable=W0613

    def __init__(
        self,
        hex_str: str,
        alpha: Optional[float] = None,
        name: Optional[str] = None,
        description: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        """extended str class to specifically represent hex color codes

        Parameters
        ----------
        hex_str : str
            color hexadecimal triplet (+ alpha) string with a leading `#`
        alpha : Optional[float], optional
            alpha channel (opacity / transparency) will overwrite alpha in hex_str if there is a conflict, by default None
        name : Optional[str], optional
            descriptive name, cannot contain special characters, by default None
        description : Optional[str], optional
            short descriptive text to provide additional context (max 255 char), by default None
        metadata : Optional[Dict[str, Any]], optional
            unstructured metadata used for querying and additional context, by default None
        """

        rgb = hex_to_rgb(hex_str)
        red, green, blue = map(lambda v: v / 255, rgb[:3])
        if len(rgb) == 4:
            alpha = rgb[3] if alpha is None else alpha  # type: ignore

        self.hex = self.__adjust_alpha(hex_str, alpha)

        super().__init__(
            red=red,
            green=green,
            blue=blue,
            name=name,
            description=description,
            metadata=metadata,
            alpha=alpha,
        )

    @property
    def hex(self) -> str:
        """represents a color in hexadecimal format"""

        return self._hex

    @hex.setter
    def hex(self, hex_string: str):
        if hasattr(self, "_hex"):
            raise AttributeError("can't set attribute 'hex'")

        HexStringValidator().validate(hex_string)
        self._hex = hex_string.upper()

    @property
    def red(self) -> int:
        """red color channel [0,255]"""

        return self.rgb[0]

    @property
    def green(self) -> int:
        """green color channel [0,255]"""

        return self.rgb[1]

    @property
    def blue(self) -> int:
        """blue color channel [0,255]"""

        return self.rgb[2]

    def css(self) -> str:
        """generate inline css for a hex color

        Returns
        -------
        str
            inline css for color representation
        """

        return str(self)

    ### Color manipulations
    def _change_rgb(self, red: Numeric, green: Numeric, blue: Numeric, keep_metadata: bool = False):
        metadata = self.info() if keep_metadata else {}
        return Hex(rgb_to_hex((red, green, blue)), alpha=self.alpha, **metadata)  # type: ignore

    def change_red(self, red: Numeric, keep_metadata: bool = False):
        """create a new color by changing the red color channel

        Parameters
        ----------
        red : Numeric
            new red color channel [0,255]
        keep_metadata : bool, optional
            use the current metadata (not recommended), by default False

        Returns
        -------
        Color
        """

        RGB256IntervalValidator("red").validate(red)
        _, green, blue = self.rgb[:3]
        return self._change_rgb(red, green, blue, keep_metadata)

    def change_green(self, green: Numeric, keep_metadata: bool = False):
        """create a new color by changing the green color channel

        Parameters
        ----------
        green : Numeric
            new green color channel [0,255]
        keep_metadata : bool, optional
            use the current metadata (not recommended), by default False

        Returns
        -------
        Color
        """

        RGB256IntervalValidator("green").validate(green)
        red, _, blue = self.rgb[:3]
        return self._change_rgb(red, green, blue, keep_metadata)

    def change_blue(self, blue: Numeric, keep_metadata: bool = False):
        """create a new color by changing the blue color channel

        Parameters
        ----------
        blue : Numeric
            new blue color channel [0,255]
        keep_metadata : bool, optional
            use the current metadata (not recommended), by default False

        Returns
        -------
        Color
        """

        RGB256IntervalValidator("blue").validate(blue)
        red, green, _ = self.rgb[:3]
        return self._change_rgb(red, green, blue, keep_metadata)

    def __str__(self) -> str:
        return self.upper()

"""RGB Color Space"""

from __future__ import annotations

from typing import Any, Dict, Optional

from colorcamp.common.types import AnyRGBColorTuple, Numeric, RGBColorTuple
from colorcamp.common.validators import RGB256IntervalValidator

from ._base_color import BaseColor

__all__ = ["RGB"]


class RGB(BaseColor, tuple):
    """Extended tuple class that represents RGB colors in 24bit [0,255] format"""

    # pylint: disable=W0613
    def __new__(cls, rgb, *args, alpha=None, **kwargs):
        if alpha is not None:
            rgb = list(rgb[:3]) + [alpha]
        return super().__new__(cls, tuple(rgb))

    # pylint: enable=W0613

    def __init__(
        self,
        rgb: RGBColorTuple,
        alpha: Optional[float] = None,
        name: Optional[str] = None,
        description: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        """extended tuple class to specifically represent rgb color codes

        Parameters
        ----------
        rgb : RGBColorTuple
            a color tuple for red, green, and blue (optional alpha) channels [0,255]
        alpha : Optional[float], optional
            alpha channel (opacity / transparency) will overwrite alpha in rgb if there is a conflict, by default None
        name : Optional[str], optional
            descriptive name, cannot contain special characters, by default None
        description : Optional[str], optional
            short descriptive text to provide additional context (max 255 char), by default None
        metadata : Optional[Dict[str, Any]], optional
            unstructured metadata used for querying and additional context, by default None
        """
        rgb = tuple(rgb)
        red, green, blue = map(lambda v: v / 255, rgb[:3])
        self.rgb = rgb[:3]

        if len(rgb) == 4:
            alpha = rgb[3] if alpha is None else alpha  # type: ignore

        super().__init__(
            red=red,
            green=green,
            blue=blue,
            alpha=alpha,
            name=name,
            description=description,
            metadata=metadata,
        )

    @property
    def rgb(self) -> AnyRGBColorTuple:  # type: ignore
        """represents a color in RGB (Red, Green, Blue) color space"""

        if self.alpha is None:
            return self._rgb  # type: ignore
        return (
            *self._rgb,
            self.alpha,
        )

    @rgb.setter
    def rgb(self, value: RGBColorTuple):
        if hasattr(self, "_rgb"):
            raise AttributeError("can't set attribute 'rgb'")
        for channel, color in zip(["red", "green", "blue"], value):
            RGB256IntervalValidator(channel).validate(color)
        self._rgb = value

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
        """generate inline css for a rgb color

        Returns
        -------
        str
            inline css for color representation
        """

        return f"rgb{self.rgb}"

    ### Color manipulations
    def _change_rgb(self, red: Numeric, green: Numeric, blue: Numeric, keep_metadata: bool = False) -> RGB:
        metadata = self.info() if keep_metadata else {}
        return RGB((red, green, blue), alpha=self.alpha, **metadata)  # type: ignore

    def change_red(self, red: Numeric, keep_metadata: bool = False) -> RGB:
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

        _, green, blue = self.rgb[:3]
        return self._change_rgb(red, green, blue, keep_metadata)

    def change_green(self, green: Numeric, keep_metadata: bool = False) -> RGB:
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

        red, _, blue = self.rgb[:3]
        return self._change_rgb(red, green, blue, keep_metadata)

    def change_blue(self, blue: Numeric, keep_metadata: bool = False) -> RGB:
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

        red, green, _ = self.rgb[:3]
        return self._change_rgb(red, green, blue, keep_metadata)

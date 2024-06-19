"""Base Color Object"""

from __future__ import annotations

import colorsys
from typing import Any, Dict, Optional

from colorcamp.common.types import AnyGenericColorTuple, GenericColorTuple, Numeric
from colorcamp.common.validators import FractionIntervalValidator, HueIntervalValidator

from ._base_color import BaseColor

__all__ = ["HSL"]


class HSL(BaseColor, tuple):
    """Extended tuple class that represents HSL color space"""

    # pylint: disable=W0613
    def __new__(cls, hsl, *args, alpha=None, **kwargs):
        if alpha is not None:
            hsl = list(hsl[:3]) + [alpha]

        return super().__new__(cls, tuple(hsl))

    # pylint: enable=W0613

    def __init__(
        self,
        hsl: GenericColorTuple,
        alpha: Optional[float] = None,
        name: Optional[str] = None,
        description: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        """extended str class to specifically represent hex color codes

        Parameters
        ----------
        hsl : str
            a color tuple for hue, saturation, lightness (optional alpha) ([0,360], [0,1], [0,1])
        alpha : Optional[float], optional
            alpha channel (opacity / transparency) will overwrite alpha in hex_str if there is a conflict, by default None
        name : Optional[str], optional
            descriptive name, cannot contain special characters, by default None
        description : Optional[str], optional
            short descriptive text to provide additional context (max 255 char), by default None
        metadata : Optional[Dict[str, Any]], optional
            unstructured metadata used for querying and additional context, by default None
        """

        # NOTE: order is funky b/c hsl <> hls
        hsl = tuple(hsl)
        red, green, blue = colorsys.hls_to_rgb(hsl[0] / 360, hsl[2], hsl[1])
        self.hsl = hsl[:3]

        if len(hsl) == 4:
            alpha = hsl[3] if alpha is None else alpha  # type: ignore

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
    def hsl(self) -> AnyGenericColorTuple:
        """represents a color in HSL (Hue, Saturation, Lightness) color space"""

        if self.alpha is None:
            return self._hsl  # type: ignore
        return (
            *self._hsl,
            self.alpha,
        )

    @hsl.setter
    def hsl(self, value: GenericColorTuple):
        if hasattr(self, "_hsl"):
            raise AttributeError("can't set attribute 'hsl'")
        HueIntervalValidator().validate(value[0])
        FractionIntervalValidator().validate(value[1])
        FractionIntervalValidator().validate(value[2])
        self._hsl = value

    @property
    def hue(self) -> float:
        """hue component of HSL color [0,360]"""

        return self.hsl[0]

    @property
    def saturation(self) -> float:
        """saturation component of HSL color [0,1]"""

        return self.hsl[1]

    @property
    def lightness(self) -> float:
        """lightness component of HSL color [0,1]"""

        return self.hsl[2]

    def css(self) -> str:
        """generate inline css for a color

        Returns
        -------
        str
            inline css for color representation
        """

        return f"hsl({self.hue:.0f} {self.saturation:.0%} {self.lightness:.0%}{'' if self.alpha is None else ' / '+str(self.alpha)})"

    ### Color manipulations
    def _change_hsl(
        self,
        hue: Numeric,
        saturation: Numeric,
        lightness: Numeric,
        keep_metadata: bool = False,
    ) -> HSL:
        metadata = self.info() if keep_metadata else {}
        return HSL((hue, saturation, lightness), alpha=self.alpha, **metadata)

    def change_hue(self, hue: Numeric, keep_metadata: bool = False) -> HSL:
        """create a new color by changing the hue component

        Parameters
        ----------
        hue : Numeric
            new hue color channel [0,360]
        keep_metadata : bool, optional
            use the current metadata (not recommended), by default False

        Returns
        -------
        Color
        """

        _, saturation, lightness = self.hsl[:3]
        return self._change_hsl(hue, saturation, lightness, keep_metadata)

    def change_saturation(self, saturation: Numeric, keep_metadata: bool = False) -> HSL:
        """create a new color by changing the saturation component

        Parameters
        ----------
        saturation : Numeric
            new saturation color channel [0,1]
        keep_metadata : bool, optional
            use the current metadata (not recommended), by default False

        Returns
        -------
        Color
        """

        hue, _, lightness = self.hsl[:3]
        return self._change_hsl(hue, saturation, lightness, keep_metadata)

    def change_lightness(self, lightness: Numeric, keep_metadata: bool = False) -> HSL:
        """create a new color by changing the lightness component

        Parameters
        ----------
        lightness : Numeric
            new lightness color channel [0,1]
        keep_metadata : bool, optional
            use the current metadata (not recommended), by default False

        Returns
        -------
        Color
        """

        hue, saturation, _ = self.hsl[:3]
        return self._change_hsl(hue, saturation, lightness, keep_metadata)

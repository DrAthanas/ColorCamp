"""Color space objects"""

from __future__ import annotations
from typing import Dict, Any, Union, Optional
from types import MethodType
import colorsys
import math
from functools import cached_property
from itertools import zip_longest

from colorcamp.color_objects._color_metadata import MetaColor
from colorcamp.common.types import (
    GenericColorTuple,
    AnyGenericColorTuple,
    RGBColorTuple,
    AnyRGBColorTuple,
    Numeric,
    ColorSpace,
)
from colorcamp.conversions import (
    hex_to_rgb,
    rgb_to_hex,
    rgb_to_hsl,
)
from colorcamp.common.validators import (
    FractionIntervalValidator,
    HueIntervalValidator,
    HexStringValidator,
    RGB256IntervalValidator,
)

__all__ = ["Hex", "RGB", "HSL"]


HTML_REPR_TEMPLATE = """<!DOCTYPE html>
<html>
<body>
    <div style="
        width: {width}px; 
        height: {height}px; 
        background-color: {css}; 
        display: flex; 
        align-items: center; 
        justify-content: center;
    ">
        <p style="
            text-align: center;
            color: white;
            font-size: 12px; /* Adjust the font size as needed */
            text-shadow: -1px -1px 0 #000, 1px -1px 0 #000, -1px 1px 0 #000, 1px 1px 0 #000;
        ">
            {text}
        </p>
    </div>
</body>
</html>
"""


# pylint: disable=W0613
def make_to_color_type(self: BaseColor, name):
    """A function factory to make short cut methods to quickly convert color subtypes"""

    def changer(self):
        return self.to_color_type(name)

    return changer


# pylint: enable=W0613


class BaseColor(MetaColor):
    """BaseColor is a foundation for all other color formats. It uses the
    RGB color notation as its foundation as it is not bound to a colorspace.
    More importantly, it can represent any other color format, but not vice-versa.

    NOTE: This is not meant to be used within operational code
    """

    _subclasses: Dict[str, BaseColor] = {}

    # pylint: disable=too-many-arguments
    # Users will not have to directly init this object
    # pylint: disable=W0231
    def __init__(
        self,
        red: float,
        green: float,
        blue: float,
        alpha: Optional[float] = None,
        name: Optional[str] = None,
        description: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        """A foundation for all other color representations

        Parameters
        ----------
        red : float
            fractional red color channel [0,1]
        green : float
            fractional green color channel [0,1]
        blue : float
            fractional blue color channel [0,1]
        alpha : Optional[float], optional
            alpha channel (opacity / transparency), by default None
        name : Optional[str], optional
            descriptive name, cannot contain special characters, by default None
        description : Optional[str], optional
            short descriptive text to provide additional context (max 255 char), by default None
        metadata : Optional[Dict[str, Any]], optional
            unstructured metadata used for querying and additional context, by default None
        """

        self.fractional_rgb = (red, green, blue)
        self.alpha = alpha
        self.name = name
        self.description = description
        self.metadata = metadata  # type: ignore

        # Dynamically add functions based on subclasses
        for subclass in self._subclasses:
            env_setter = make_to_color_type(self, subclass)

            method = MethodType(env_setter, self)
            setattr(self, f"to_{subclass.lower()}", method)

    # pylint: enable=too-many-arguments
    # pylint: enable=W0231

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        name = cls.__name__
        cls._subclasses[name] = cls

    @property
    def fractional_rgb(self) -> AnyGenericColorTuple:
        """fractional RGB [0,1]"""

        if self.alpha is None:
            return self._fractional_rgb
        return tuple((*self._fractional_rgb, self.alpha))  # type: ignore

    @fractional_rgb.setter
    def fractional_rgb(self, value: GenericColorTuple):
        if hasattr(self, "_fractional_rgb"):
            raise AttributeError("can't set attribute 'fractional_rgb'")

        for channel, color in zip(["red", "green", "blue"], value):
            FractionIntervalValidator(channel).validate(color)
        self._fractional_rgb = value

    @property
    def alpha(self) -> Union[float, None]:
        """alpha channel [0,1]"""
        return self._alpha

    @alpha.setter
    def alpha(self, value: Union[float, None]):
        if hasattr(self, "_alpha"):
            raise AttributeError("can't set attribute 'alpha'")

        if value is not None:
            FractionIntervalValidator("alpha").validate(value)
        self._alpha = value

    def change_alpha(self, alpha: float):
        """change the alpha value and return a new color object

        Parameters
        ----------
        alpha : float
            the new alpha value [0,1]

        Returns
        -------
        Color
            a new color object with the same metadata and of same color type
        """

        # If it's base color it has a different signature
        if self.__class__.__name__ == "BaseColor":
            return self.__class__(*self.fractional_rgb[:3], alpha=alpha, **self.info())

        # types change based on subclasses - that's the point of this repo
        return self.__class__(self, alpha=alpha, **self.info())  # type: ignore

    ## Stored color types
    @cached_property
    def hsl(self) -> AnyGenericColorTuple:
        """represents a color in HSL (Hue, Saturation, Lightness) color space"""

        return rgb_to_hsl(self.fractional_rgb)

    @cached_property
    def rgb(self) -> AnyRGBColorTuple:
        """represents a color in RGB (Red, Green, Blue) color space"""

        rgb256 = list(map(lambda x: round(x * 255), self.fractional_rgb[:3]))
        if self.alpha is None:
            return tuple(rgb256)  # type: ignore
        return (*rgb256, self.alpha)  # type: ignore

    @cached_property
    def hex(self) -> str:
        """represents a color in hexadecimal format"""

        return rgb_to_hex(self.rgb)

    ## Conversion methods
    def to_color_type(self, color_type: ColorSpace):
        """convert current color object to a new representation

        Parameters
        ----------
        color_type : Literal['BaseColor', 'Hex', 'RGB', 'HSL']
            the new color representation (Color subclass)

        Returns
        -------
        Color
            a new color object with the same metadata in a new color representation
        """

        if color_type is self.__class__.__name__:
            new_color: BaseColor = self
        elif color_type in self._subclasses:
            new_color: BaseColor = self._subclasses[color_type](  # type: ignore
                getattr(self, color_type.lower()),
                **self.info(),
                alpha=self.alpha,
            )
            # Bypass the setter to insure frgb values are exact to avoid fp errors
            new_color._fractional_rgb = self.fractional_rgb[:3]  # pylint: disable=W0212
        elif color_type == "BaseColor":
            new_color = BaseColor(*self.fractional_rgb[:3], **self.info(), alpha=self.alpha)
        else:
            raise ValueError(f'Color type "{color_type}" is not in {list(self._subclasses.keys())}')

        return new_color

    ## Utility functions
    def css(self) -> str:
        """generate inline css for a color

        Returns
        -------
        str
            inline css for color representation
        """

        # Needed some default - using rgb since it's inline with init
        return f"rgb{self.rgb}"

    def to_dict(self) -> Dict[str, Any]:
        """create a dictionary of all color attributes

        Returns
        -------
        Dict[str, Any]
            dictionary with the underlying color representation
        """

        def _tuple_to_list(color):
            if isinstance(color, tuple):
                return list(color)
            else:
                return color

        return {
            "type": "BaseColor",
            **self.info(),
            "red": self.fractional_rgb[0],
            "green": self.fractional_rgb[1],
            "blue": self.fractional_rgb[2],
            "alpha": self.alpha,
            "color_formats": {ct: _tuple_to_list(self.to_color_type(ct)) for ct in self._subclasses},  # type: ignore
        }

    @classmethod
    def from_dict(cls, color_dict: Dict[str, Any], color_type: Optional[ColorSpace] = None) -> BaseColor:
        """Create a new color object from a color dictionary

        Parameters
        ----------
        color_dict : Dict[str, Any]
            A Color dictionary
        color_type : Literal['BaseColor', 'Hex', 'RGB', 'HSL']
            The new color representation (Color subclass). If None is supplied the current representation is used, by default None

        Returns
        -------
        Color
            A new Color object
        """

        init_args = {
            "red",
            "green",
            "blue",
            "name",
            "description",
            "metadata",
            "alpha",
        }

        if color_type is None:
            color_type = cls.__name__  # type: ignore

        color_dict = {key: value for key, value in color_dict.items() if key in init_args}

        return BaseColor(**color_dict).to_color_type(color_type)  # type: ignore

    ## dunders
    def __eq__(self, color):
        # Tolerance is relative based on the left type
        tolerances = {
            "Hex": 1 / (255 * 2),
            "RGB": 1 / (255 * 2),
        }
        if isinstance(color, BaseColor):
            # Determine relative precision

            return all(
                map(
                    lambda p: math.isclose(
                        p[0],
                        p[1],
                        abs_tol=tolerances.get(self.__class__.__name__, 1e-9),
                    ),
                    zip_longest(self.fractional_rgb, color.fractional_rgb, fillvalue=1),
                )
            )
        if isinstance(self, type(color)):
            # This converts the Color to the base type of the other object
            return type(color)(self) == color

        return False

    def __add__(self, color: BaseColor) -> BaseColor:
        if not isinstance(color, BaseColor):
            raise TypeError("addition operator is only supported between two Color objects")

        red, green, blue = map(lambda x: sum(x) / 2, zip(self.fractional_rgb[:3], color.fractional_rgb[:3]))

        return BaseColor(red=red, green=green, blue=blue).to_color_type(self.__class__.__name__)  # type: ignore

    def _repr_html_(self):
        text = "<br>".join(
            map(
                str,
                [val for val in [self.name, self.__class__.__name__, self.css()] if val is not None],
            )
        )

        return HTML_REPR_TEMPLATE.format(css=self.css(), width=100, height=100, text=text)


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


class RGB(BaseColor, tuple):
    """Extended tuple class that represents RGB colors in 24bit [0,255] format"""

    # pylint: disable=W0613
    def __new__(cls, rgb, *args, alpha=None, **kwargs):
        if alpha is not None:
            rgb = tuple(list(rgb[:3]) + [alpha])
        return super().__new__(cls, rgb)

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
        return (*self._rgb, self.alpha)

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


class HSL(BaseColor, tuple):
    """Extended tuple class that represents HSL color space"""

    # pylint: disable=W0613
    def __new__(cls, hsl, *args, alpha=None, **kwargs):
        if alpha is not None:
            hsl = tuple(list(hsl[:3]) + [alpha])

        return super().__new__(cls, hsl)

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
        return (*self._hsl, self.alpha)

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

        return f"hsl({self.hue:.0f} {self.saturation:.2%} {self.lightness:.2%}{'' if self.alpha is None else ' / '+str(self.alpha)})"

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
